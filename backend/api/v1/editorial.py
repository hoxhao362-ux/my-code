"""
编辑中心相关 API 接口

包含编委会管理、编辑看板等功能
"""

from api import dependencies as deps
<<<<<<< HEAD
from core.enums import ManuscriptStatus, ReviewStage, UserRole
from database.dependencies import get_db_session
from database.orm.models.editorial import EditorialBoard
from database.orm.models.manuscript import Manuscript
from database.repositories.editorial_board_repo import EditorialBoardRepository
from database.repositories.manuscript_repo import ManuscriptRepository
from database.repositories.user_repo import UserRepository
from database.uow import transactional
from fastapi import APIRouter, Depends, HTTPException
from model.manuscript import EditorialPendingItemDTO
from model.response import ApiResponse
from service.admin_log_service import admin_log_service
=======
from core.enums import ManuscriptStatus, ReviewStage
from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript
from database.repositories.manuscript_repo import ManuscriptRepository
from fastapi import APIRouter, Depends
from model.manuscript import EditorialPendingItemDTO
from model.response import ApiResponse
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import global_logger

# 创建编辑中心路由
router = APIRouter(
    prefix="/editorial",
    tags=["编辑中心相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
    },
)


@router.get("/dashboard", summary="获取编辑看板")
async def get_editorial_dashboard(
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取编辑工作台看板数据

    功能说明：
    1. 待处理稿件数
    2. 进行中审稿数
    3. 统计数据

    Args:
        current_user: 当前用户信息
        session: 数据库会话

    Returns:
        dict: 看板统计数据
    """
    global_logger.debug(
        "Editorial",
        f"获取编辑看板 - uid: {current_user['uid']}, role: {current_user['role']}",
    )

    repo = ManuscriptRepository(session)

    # 定义待处理状态（需要编辑从业者处理的状态）
    pending_statuses = [
        ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
        ManuscriptStatus.REVISION_SUBMITTED.value,
        ManuscriptStatus.PENDING_PEER_REVIEW.value,
        ManuscriptStatus.REVIEW_COMPLETED.value,
        ManuscriptStatus.PENDING_FINAL_DECISION.value,
    ]

    # 定义审稿中状态
    under_review_statuses = [
        ManuscriptStatus.UNDER_INITIAL_REVIEW.value,
        ManuscriptStatus.UNDER_PEER_REVIEW.value,
        ManuscriptStatus.UNDER_FINAL_DECISION.value,
    ]

    # 定义已完成状态
    completed_statuses = [
        ManuscriptStatus.PUBLISHED.value,
        ManuscriptStatus.FINAL_DECISION_REJECTED.value,
        ManuscriptStatus.WITHDRAWN.value,
        ManuscriptStatus.TRANSFERRED.value,
    ]

    # 通过 Repository 查询各状态统计
    status_counts = await repo.get_status_breakdown()

    # 计算各类别数量
    pending_count = sum(status_counts.get(s, 0) for s in pending_statuses)
    under_review_count = sum(status_counts.get(s, 0) for s in under_review_statuses)
    completed_count = sum(status_counts.get(s, 0) for s in completed_statuses)
    total_count = sum(status_counts.values())

    # 通过 Repository 查询待处理稿件 top 10
    pending_manuscripts = await repo.list_by_statuses(
        pending_statuses,
        limit=10,
        order_by=Manuscript.create_time.asc(),
    )

    # 使用 Pydantic DTO 转换为响应格式
    pending_list = [
        EditorialPendingItemDTO.model_validate(m).model_dump()
        for m in pending_manuscripts
    ]

    # 按阶段统计
    stage_stats = {
        ReviewStage.INITIAL_REVIEW.value: sum(
            status_counts.get(s, 0)
            for s in ManuscriptStatus.get_status_by_phase(ReviewStage.INITIAL_REVIEW)
        ),
        ReviewStage.PEER_REVIEW.value: sum(
            status_counts.get(s, 0)
            for s in ManuscriptStatus.get_status_by_phase(ReviewStage.PEER_REVIEW)
        ),
        ReviewStage.FINAL_DECISION.value: sum(
            status_counts.get(s, 0)
            for s in ManuscriptStatus.get_status_by_phase(ReviewStage.FINAL_DECISION)
        ),
    }

    return ApiResponse.success(
        data={
            "pending_manuscripts": pending_count,
            "under_review": under_review_count,
            "completed_reviews": completed_count,
            "total_manuscripts": total_count,
            "statistics": {
                "by_status": status_counts,
                "by_stage": stage_stats,
            },
            "pending_list": pending_list,
        }
    )


<<<<<<< HEAD
_BOARD_POSITIONS = frozenset({"editor", "associate_editor", "ea_ae"})
_POSITION_TO_ROLE = {
    "editor": UserRole.EDITOR.value,
    "associate_editor": UserRole.ASSOCIATE_EDITOR.value,
    "ea_ae": UserRole.EA_AE.value,
}


=======
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
@router.get("/board", summary="获取编委会列表")
async def get_editorial_board(
    page: int = 1,
    page_size: int = 10,
<<<<<<< HEAD
    position: str | None = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """分页返回在职编委会成员（可筛选职位）。"""
    if position and position not in _BOARD_POSITIONS:
        raise HTTPException(status_code=400, detail="无效的职位筛选")

    repo = EditorialBoardRepository(session)
    total = await repo.count_board(position=position, is_active=True)
    rows = await repo.list_board_page(
        page, page_size, position=position, is_active=True
    )
    for r in rows:
        if r.get("appointed_at"):
            r["appointed_at"] = r["appointed_at"].isoformat()

    global_logger.debug(
        "Editorial",
        f"编委列表 - requester_uid: {current_user['uid']}, total: {total}",
    )
    return ApiResponse.paginated(
        items=rows, total=total, page=page, page_size=page_size
    )
=======
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取编委会成员列表

    Args:
        page: 页码
        page_size: 每页数量
        current_user: 当前用户信息
        session: 数据库会话

    Returns:
        dict: 编委会成员列表
    """
    """
    TODO: 实现编委会列表查询

    建议实现流程：
    1. 构建查询条件：默认仅查询 is_active=True 的在职编委，支持按 position 筛选
    2. 联表查询 EditorialBoard + User，获取编委的用户名、邮箱等基础信息
    3. 计算总数 total，执行分页查询 offset/limit
    4. 将结果转换为响应字典列表，包含编委 ID、用户信息、职位、研究领域、任命时间等
    5. 返回 ApiResponse.paginated 分页响应

    所需 ORM 模型：
    - EditorialBoard (database/orm/models/editorial.py) — 编委会成员表，含 board_id/user_uid/position/title/research_areas/appointed_at/is_active
    - User (database/orm/models/user.py) — 用户表，联表获取 username/email/role

    建议 Repository 方法：
    - EditorialBoardRepository.list_page(page, page_size, position=None, is_active=True) — 分页查询编委列表
    - EditorialBoardRepository.count(position=None, is_active=True) — 统计编委总数

    建议 Service 调用链：
    API → EditorialBoardRepository.list_page() → 联表查询 EditorialBoard+User → 格式化返回

    权限要求：
    - 当前使用 get_current_active_user（已登录用户均可访问）
    - 建议保持，编委会信息属于公开信息

    返回数据格式建议：
    {
        "items": [
            {
                "board_id": 1,
                "user_uid": 10,
                "username": "张三",
                "email": "zhangsan@example.com",
                "position": "editor",
                "title": "教授",
                "research_areas": "计算机科学,人工智能",
                "appointed_at": "2025-01-01T00:00:00",
                "is_active": true
            }
        ],
        "total": 5,
        "page": 1,
        "page_size": 10
    }

    注意事项：
    - EditorialBoard.user_uid 有 unique 约束，一个用户只能有一条编委记录
    - 建议增加 position 可选查询参数（editor/associate_editor/ea_ae）以支持按职位筛选
    - 联表查询时注意使用 joinedload 或显式 join 避免懒加载 N+1 问题
    - 研究领域 research_areas 为逗号分隔的字符串，前端可自行拆分展示
    """
    return ApiResponse.paginated(items=[], total=0, page=page, page_size=page_size)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea


@router.post("/board", summary="添加编委会成员（管理员）")
async def add_editorial_board_member(
    user_id: int,
    position: str,
<<<<<<< HEAD
    title: str | None = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """任命编委并提升用户角色（不低于对应职位）。"""
    if position not in _BOARD_POSITIONS:
        raise HTTPException(status_code=400, detail="position 须为 editor/associate_editor/ea_ae")

    eb_repo = EditorialBoardRepository(session)
    user_repo = UserRepository(session)

    if await eb_repo.get_by_user_uid(user_id):
        raise HTTPException(status_code=400, detail="该用户已在编委会中")

    from datetime import datetime

    try:
        board_id_val: int | None = None
        appointed_val = None
        async with transactional(session):
            user = await user_repo.get_by_id(user_id)
            if not user or user.is_deleted:
                raise HTTPException(status_code=404, detail="用户不存在")

            row = EditorialBoard(
                user_uid=user_id,
                position=position,
                title=title,
                research_areas=None,
                appointed_at=datetime.now(),
                appointed_by_uid=current_user["uid"],
                is_active=True,
            )
            session.add(row)
            await session.flush()
            board_id_val = row.board_id
            appointed_val = row.appointed_at

            target_role = _POSITION_TO_ROLE[position]
            if UserRole.get_role_level(user.role) < UserRole.get_role_level(
                target_role
            ):
                user.role = target_role
                global_logger.info(
                    "Editorial",
                    f"编委任命同步提升角色 uid={user_id} -> {target_role}",
                )

        await admin_log_service.record_admin_log(
            admin_uid=current_user["uid"],
            admin_username=current_user.get("username", str(current_user["uid"])),
            operation_type="添加编委会成员",
            operation_object=f"user_uid={user_id}",
            operation_details=f"position={position}, board_id={board_id_val}",
            session=session,
        )

        global_logger.info(
            "Editorial",
            f"添加编委 - admin_uid: {current_user['uid']}, target_uid: {user_id}, position: {position}",
        )
        return ApiResponse.success(
            data={
                "board_id": board_id_val,
                "user_uid": user_id,
                "position": position,
                "appointed_at": appointed_val.isoformat() if appointed_val else None,
            },
            message="编委成员添加成功",
        )
    except HTTPException:
        raise
    except Exception as e:
        global_logger.exception("Editorial", f"添加编委失败: {e}")
        raise HTTPException(status_code=500, detail="添加编委失败") from e
=======
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    添加编委会成员（仅限管理员或主编）

    Args:
        user_id: 用户 ID
        position: 职位（editor/associate_editor/ea_ae）
        current_user: 管理员用户信息
        session: 数据库会话

    Returns:
        dict: 添加成功消息
    """
    """
    TODO: 实现编委会成员添加逻辑

    建议实现流程：
    1. 参数校验：验证 position 值是否合法（仅允许 editor/associate_editor/ea_ae 三种）
    2. 查询目标用户是否存在且未删除（通过 UserRepository.get_by_id）
    3. 检查目标用户是否已在编委会中（EditorialBoard.user_uid 为 unique，重复添加会报错）
    4. 创建 EditorialBoard 记录，设置 user_uid/position/appointed_at/appointed_by_uid/is_active
    5. 同步更新 User 表中目标用户的 role 字段，使其与编委职位一致（如 position=editor 则 role=editor）
    6. 在事务中执行上述操作（使用 transactional 装饰器或上下文管理器）
    7. 记录管理员操作日志（AdminLog）

    所需 ORM 模型：
    - EditorialBoard (database/orm/models/editorial.py) — 编委会成员表，需新建记录
    - User (database/orm/models/user.py) — 需更新目标用户的 role 字段
    - AdminLog (database/orm/models/admin_log.py) — 记录管理员操作日志

    建议 Repository 方法：
    - EditorialBoardRepository.get_by_user_uid(user_uid) — 查询某用户是否已是编委
    - EditorialBoardRepository.add(board_member) — 新增编委记录
    - UserRepository.get_by_id(uid) — 查询目标用户

    建议 Service 调用链：
    API → 校验参数 → UserRepository.get_by_id() → EditorialBoardRepository.get_by_user_uid()
        → 创建 EditorialBoard 对象 → EditorialBoardRepository.add()
        → 更新 User.role → AdminLog 记录 → 返回成功

    权限要求：
    - 当前使用 get_admin_user（仅管理员可操作），符合要求
    - 建议增加主编(editor)也可操作的权限，可考虑使用 require_role(editor) 依赖

    返回数据格式建议：
    {
        "board_id": 1,
        "user_uid": 10,
        "position": "editor",
        "appointed_at": "2026-04-18T00:00:00"
    }

    注意事项：
    - EditorialBoard.user_uid 为 unique 字段，重复添加会抛出 IntegrityError，需提前检查并给出友好提示
    - 必须在事务中同时更新 User.role 和新增 EditorialBoard 记录，保证数据一致性
    - position 值需要与 UserRole 枚举对应：editor → UserRole.EDITOR, associate_editor → UserRole.ASSOCIATE_EDITOR, ea_ae → UserRole.EA_AE
    - appointed_at 使用当前时间的 ISO 字符串
    - appointed_by_uid 应为当前操作管理员的 uid
    - 不能将自己添加为编委（已有管理员角色，无需重复）
    """
    global_logger.info(
        "Editorial",
        f"添加编委 - admin_uid: {current_user['uid']}, target_uid: {user_id}, position: {position}",
    )

    return ApiResponse.success(message="编委成员添加成功")
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
