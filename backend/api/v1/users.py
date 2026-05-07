"""
用户中心相关 API 接口

包含个人信息查看/修改、消息通知等功能
"""

from api import dependencies as deps
from core.enums import NotificationType, UserRole
from database.dependencies import get_db_session
from database.repositories.notification_repo import NotificationRepository
from database.repositories.user_repo import UserRepository
from database.uow import transactional
from fastapi import APIRouter, Depends, HTTPException
from model.response import ApiResponse
from model.user import UserProfileDTO
from service.redis_service import redis_service
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import global_logger

# 创建用户中心路由
router = APIRouter(
    prefix="/users",
    tags=["用户中心相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
    },
)


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取当前登录用户的个人信息

    功能说明：
    1. 从数据库获取最新用户信息
    2. 检查在线状态

    Args:
        current_user: 当前用户信息（依赖注入）
        session: 数据库会话

    Returns:
        dict: 用户信息字典
    """
    # 从 Redis 验证用户在线状态
    is_online = await redis_service.is_user_online(current_user["uid"])

    # 从数据库获取完整用户信息
    repo = UserRepository(session)
    user = await repo.get_profile_fields_by_id(current_user["uid"])

    if not user:
        global_logger.error("Users", f"用户不存在 - uid: {current_user['uid']}")
        raise HTTPException(status_code=404, detail="用户不存在")

    global_logger.debug(
        "Users",
        f"获取用户信息成功 - uid: {current_user['uid']}, username: {user['username']}",
    )

    # 使用 Pydantic DTO 构建响应数据
    profile_dto = UserProfileDTO.model_validate(user)
    response_data = profile_dto.model_dump()
    response_data["is_online"] = is_online

    return ApiResponse.success(data=response_data)


@router.put("/me", summary="更新当前用户信息")
async def update_current_user_info(
    avatar_hash: str | None = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    更新当前用户个人信息

    功能说明：
    1. 仅允许更新非关键信息（如头像）
    2. 关键信息（用户名、邮箱、角色）不可修改

    Args:
        avatar_hash: 头像哈希值（可选）
        current_user: 当前用户信息
        session: 数据库会话

    Returns:
        dict: 更新成功消息

    Raises:
        HTTPException: 用户不存在
    """
    repo = UserRepository(session)
    async with transactional(session):
        user = await repo.get_by_id(current_user["uid"])
        if not user:
            global_logger.error("Users", f"用户不存在 - uid: {current_user['uid']}")
            raise HTTPException(status_code=404, detail="用户不存在")

        # 仅更新允许的字段
        if avatar_hash is not None:
            user.avatar_hash = avatar_hash

    global_logger.info(
        "Users",
        f"用户信息更新成功 - uid: {current_user['uid']}, username: {current_user['username']}",
    )

    return ApiResponse.success(message="用户信息更新成功")


@router.get("/me/notifications", summary="获取我的消息列表")
async def get_my_notifications(
    page: int = 1,
    page_size: int = 10,
    is_read: bool | None = None,
    notification_type: str | None = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    分页获取当前用户的站内通知；meta 中带 unread_count 供角标展示。
    """
    if notification_type and notification_type not in NotificationType.get_all_types():
        raise HTTPException(status_code=400, detail="无效的通知类型")

    repo = NotificationRepository(session)
    uid = current_user["uid"]
    total = await repo.count_for_user(
        uid, is_read=is_read, notification_type=notification_type
    )
    unread = await repo.count_for_user(uid, is_read=False)
    rows = await repo.list_page_for_user(
        uid,
        page,
        page_size,
        is_read=is_read,
        notification_type=notification_type,
    )
    items = [repo.to_item_dict(n) for n in rows]

    global_logger.debug(
        "Users",
        f"获取用户消息 - uid: {uid}, page: {page}, total: {total}, unread: {unread}",
    )
    return ApiResponse.paginated(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        extra_meta={"unread_count": unread},
    )


@router.put("/me/notifications/{notification_id}", summary="标记消息为已读")
async def mark_notification_as_read(
    notification_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """将通知标为已读；须属于当前用户；重复调用幂等。"""
    repo = NotificationRepository(session)
    async with transactional(session):
        n = await repo.mark_read(notification_id, current_user["uid"])
        if not n:
            global_logger.warning(
                "Users",
                f"标记已读失败（不存在或无权限） uid={current_user['uid']} id={notification_id}",
            )
            raise HTTPException(status_code=404, detail="通知不存在")

    global_logger.info(
        "Users",
        f"标记消息已读 - uid: {current_user['uid']}, notification_id: {notification_id}",
    )
    return ApiResponse.success(
        data={"notification_id": notification_id, "is_read": True},
        message="消息已标记为已读",
    )


@router.get("/", summary="获取用户列表（管理员）")
async def get_user_list(
    page: int = 1,
    page_size: int = 10,
    role: str | None = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取用户列表（仅限管理员）

    功能说明：
    1. 支持按角色筛选
    2. 支持分页查询

    Args:
        page: 页码
        page_size: 每页数量
        role: 角色筛选（可选）
        current_user: 管理员用户信息
        session: 数据库会话

    Returns:
        dict: 用户列表（分页）

    Raises:
        HTTPException: 需要管理员权限
    """
    # 验证角色权限
    if role and role not in UserRole.get_all_roles():
        raise HTTPException(status_code=400, detail=f"无效的角色：{role}")

    repo = UserRepository(session)
    total = await repo.count(role=role)
    users = await repo.list_page(page, page_size, role=role)

    global_logger.info(
        "Users",
        f"管理员获取用户列表 - admin_uid: {current_user['uid']}, total: {total}, role: {role}",
    )

    return ApiResponse.paginated(
        items=users, total=total, page=page, page_size=page_size
    )


@router.get("/{user_id}", summary="获取指定用户信息（管理员）")
async def get_user_info(
    user_id: int,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取指定用户的详细信息（仅限管理员）

    Args:
        user_id: 用户 ID
        current_user: 管理员用户信息
        session: 数据库会话

    Returns:
        dict: 用户详细信息

    Raises:
        HTTPException: 用户不存在、需要管理员权限
    """
    repo = UserRepository(session)
    user = await repo.get_profile_fields_by_id(user_id)

    if not user:
        global_logger.warning("Users", f"管理员查询用户不存在 - uid: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")

    global_logger.info(
        "Users",
        f"管理员获取用户详情 - admin_uid: {current_user['uid']}, target_uid: {user_id}",
    )

    return ApiResponse.success(data=user)


@router.put("/{user_id}", summary="更新指定用户信息（管理员）")
async def update_user_info(
    user_id: int,
    role: str | None = None,
    is_verified: bool | None = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    更新指定用户的信息（仅限管理员）

    功能说明：
    1. 可更新角色和验证状态
    2. 记录管理员操作日志

    Args:
        user_id: 用户 ID
        role: 新角色（可选）
        is_verified: 是否验证（可选）
        current_user: 管理员用户信息
        session: 数据库会话

    Returns:
        dict: 更新成功消息

    Raises:
        HTTPException: 用户不存在、无效角色
    """
    # 验证角色
    if role and role not in UserRole.get_all_roles():
        raise HTTPException(status_code=400, detail=f"无效的角色：{role}")

    repo = UserRepository(session)
    async with transactional(session):
        user = await repo.get_by_id(user_id)
        if not user:
            global_logger.error("Users", f"用户不存在 - uid: {user_id}")
            raise HTTPException(status_code=404, detail="用户不存在")

        # 更新允许的字段
        if role is not None:
            user.role = role
            global_logger.info(
                "Users",
                f"管理员更新用户角色 - admin_uid: {current_user['uid']}, target_uid: {user_id}, new_role: {role}",
            )

        if is_verified is not None:
            user.is_verified = is_verified
            global_logger.info(
                "Users",
                f"管理员更新用户验证状态 - admin_uid: {current_user['uid']}, target_uid: {user_id}, verified: {is_verified}",
            )

    return ApiResponse.success(message="用户信息更新成功")


@router.delete("/{user_id}", summary="删除指定用户（管理员）")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    删除指定用户（仅限管理员）

    注意：这是软删除，不会真正从数据库移除

    Args:
        user_id: 用户 ID
        current_user: 管理员用户信息
        session: 数据库会话

    Returns:
        dict: 删除成功消息

    Raises:
        HTTPException: 用户不存在、不能删除自己
    """
    if user_id == current_user["uid"]:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    repo = UserRepository(session)
    async with transactional(session):
        user = await repo.get_by_id(user_id)
        if not user:
            global_logger.error("Users", f"用户不存在 - uid: {user_id}")
            raise HTTPException(status_code=404, detail="用户不存在")

        # 软删除：禁用账号
        user.is_verified = False
        user.role = UserRole.USER.value

    global_logger.info(
        "Users",
        f"管理员删除用户 - admin_uid: {current_user['uid']}, target_uid: {user_id}",
    )

    return ApiResponse.success(message="用户已删除")
