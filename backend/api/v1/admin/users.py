from datetime import datetime
from typing import Optional

from api import dependencies as deps
from core.enums import UserRole
from database.dependencies import get_db_session
from database.orm.models.editorial import DecisionRecord, EditorialBoard
from database.orm.models.invitation import InvitationCode, InvitationCodeUsage
from database.orm.models.manuscript import (Manuscript, ManuscriptFile,
                                            ManuscriptParticipant,
                                            ManuscriptVersion)
from database.orm.models.payment_order import PaymentOrder
from database.orm.models.review_opinion import ReviewOpinion
from database.repositories.user_repo import UserRepository
from database.uow import transactional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from model.response import ApiResponse
from model.user import LoginRequest
from service.admin_log_service import admin_log_service
from service.redis_service import redis_service
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.jwt import jwt_util
from utils.log import global_logger

router = APIRouter(tags=["管理员-用户管理"])


@router.post("/login", summary="管理员登录")
async def admin_login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """管理员登录接口"""
    # 从数据库查询用户
    user_repo = UserRepository(session)
    user = await user_repo.get_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查角色是否为管理员
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="非管理员账号，无权登录")

    # 验证密码
    if not jwt_util.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="密码错误")

    # 更新最后登录时间
    async with transactional(session):
        user.last_login_time = datetime.now()

    # 生成JWT token
    token = await jwt_util.create_access_token(
        {
            "uid": user.uid,
            "username": request.username,
            "email": user.email,
            "role": user.role,
        }
    )

    # 设置用户在线状态
    expire_time = 3600 * 24 * 30 if request.is_remember else 3600
    await redis_service.set_user_online(
        user_id=user.uid, token=token, expire_time=expire_time
    )

    return ApiResponse.success(
        data={
            "login_time": datetime.now().isoformat(),
            "is_remember": request.is_remember,
            "token": token,
        },
        message="登录成功",
    )


@router.get("/users", summary="获取用户列表")
async def get_users(
    page: int = 1,
    page_size: int = 10,
    role: Optional[str] = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有用户列表，仅限管理员访问"""
    user_repo = UserRepository(session)
    total = await user_repo.count(role=role)
    users = await user_repo.list_page(page=page, page_size=page_size, role=role)

    return ApiResponse.success(
        data={
            "total": total,
            "users": users,
        }
    )


@router.put("/users/{uid}/role", summary="修改用户角色")
async def update_user_role(
    uid: int,
    role: str,
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """修改用户角色，仅限管理员访问"""
    # 检查角色有效性
    if not UserRole.is_valid(role):
        raise HTTPException(
            status_code=400, detail=f"角色无效，允许的角色: {UserRole.get_all_values()}"
        )

    user_repo = UserRepository(session)
    async with transactional(session):
        user = await user_repo.get_by_id(uid)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        old_role = user.role
        user.role = role

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="修改用户角色",
        operation_object=f"用户ID: {uid}",
        operation_details=f"将用户角色从 {old_role} 修改为 {role}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    return ApiResponse.success(
        data={"uid": uid, "new_role": role}, message="用户角色更新成功"
    )


@router.delete("/users/{uid}", summary="软删除用户（停用账户）")
async def delete_user(
    uid: int,
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    软删除用户：标记为已删除状态，清理在线会话。
    不会物理删除数据，可通过管理员恢复。
    """
    user_repo = UserRepository(session)

    async with transactional(session):
        user = await user_repo.get_by_id(uid)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 检查用户是否已被软删除
        if user.is_deleted:
            raise HTTPException(status_code=400, detail="用户已处于删除状态")

        # 禁止删除自己
        if user.uid == current_user["uid"]:
            raise HTTPException(status_code=400, detail="不能删除自己的账户")

        # 软删除：标记状态
        user.is_deleted = True
        user.deleted_at = datetime.now()

    # 清理 Redis 在线会话，强制用户下线
    try:
        # 获取用户 token 并清理会话
        token = await redis_service.get_token_by_user(uid)
        if token:
            await redis_service.set_user_offline(uid, token)
    except Exception as e:
        global_logger.warning("AdminUsers", f"清理用户 {uid} 会话失败: {e}")

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="软删除用户",
        operation_object=f"用户ID: {uid}",
        operation_details=f"软删除用户 {user.username} (邮箱: {user.email})",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    global_logger.info(
        "AdminUsers", f"管理员 {current_user['username']} 软删除了用户 {uid}"
    )

    return ApiResponse.success(data={"uid": uid}, message="用户已停用")


@router.delete("/users/{uid}/permanent", summary="永久删除用户（不可恢复）")
async def permanent_delete_user(
    uid: int,
    confirm: bool = Query(..., description="确认永久删除，此操作不可恢复"),
    request: Request = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    永久删除用户及其所有关联数据。此操作不可恢复，需要 confirm=true 二次确认。
    """
    if not confirm:
        raise HTTPException(
            status_code=400, detail="请确认永久删除操作（confirm=true）"
        )

    user_repo = UserRepository(session)

    async with transactional(session):
        user = await user_repo.get_by_id(uid)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 禁止删除自己
        if user.uid == current_user["uid"]:
            raise HTTPException(status_code=400, detail="不能永久删除自己的账户")

        # 检查是否有进行中的审稿任务（仅针对审稿人角色）
        if user.role in [
            UserRole.REVIEWER.value,
            UserRole.ASSOCIATE_EDITOR.value,
            UserRole.EDITOR.value,
        ]:
            active_participations = await session.scalar(
                select(ManuscriptParticipant)
                .where(
                    ManuscriptParticipant.user_uid == uid,
                    ManuscriptParticipant.is_active == True,
                )
                .limit(1)
            )
            if active_participations:
                raise HTTPException(
                    status_code=400,
                    detail="该用户有进行中的审稿/编辑任务，请先处理或转移这些任务",
                )

        # 级联删除所有关联数据（按照外键依赖关系顺序删除）

        # 1. 删除 Manuscript 相关数据
        # 2.1 删除用户作为参与者关联的数据
        await session.execute(
            delete(ManuscriptParticipant).where(ManuscriptParticipant.user_uid == uid)
        )
        await session.execute(
            delete(ManuscriptParticipant).where(
                ManuscriptParticipant.assigned_by_uid == uid
            )
        )

        # 2.2 删除用户上传的稿件文件
        await session.execute(
            delete(ManuscriptFile).where(ManuscriptFile.uploaded_by_uid == uid)
        )

        # 2.3 删除用户提交的稿件版本
        await session.execute(
            delete(ManuscriptVersion).where(ManuscriptVersion.submitted_by_uid == uid)
        )

        # 2.4 删除用户作为作者的稿件（稿件主表）
        # 先获取该用户的所有稿件ID
        user_manuscripts = await session.execute(
            select(Manuscript.manuscript_id).where(Manuscript.author_uid == uid)
        )
        manuscript_ids = [row[0] for row in user_manuscripts.all()]

        if manuscript_ids:
            # 删除这些稿件关联的所有数据
            await session.execute(
                delete(ManuscriptFile).where(
                    ManuscriptFile.manuscript_id.in_(manuscript_ids)
                )
            )
            await session.execute(
                delete(ManuscriptParticipant).where(
                    ManuscriptParticipant.manuscript_id.in_(manuscript_ids)
                )
            )
            await session.execute(
                delete(ManuscriptVersion).where(
                    ManuscriptVersion.manuscript_id.in_(manuscript_ids)
                )
            )
            # 删除审稿意见
            await session.execute(
                delete(ReviewOpinion).where(
                    ReviewOpinion.manuscript_id.in_(manuscript_ids)
                )
            )
            # 删除决策记录
            await session.execute(
                delete(DecisionRecord).where(
                    DecisionRecord.manuscript_id.in_(manuscript_ids)
                )
            )
            # 最后删除稿件
            await session.execute(
                delete(Manuscript).where(Manuscript.manuscript_id.in_(manuscript_ids))
            )

        # 3. 删除审稿意见（用户作为审稿人）
        await session.execute(
            delete(ReviewOpinion).where(ReviewOpinion.reviewer_uid == uid)
        )

        # 4. 删除决策记录（用户作为决策者）
        await session.execute(
            delete(DecisionRecord).where(DecisionRecord.decided_by_uid == uid)
        )

        # 5. 删除编委会成员记录
        await session.execute(
            delete(EditorialBoard).where(EditorialBoard.user_uid == uid)
        )
        await session.execute(
            delete(EditorialBoard).where(EditorialBoard.appointed_by_uid == uid)
        )

        # 6. 删除邀请码相关记录
        await session.execute(
            delete(InvitationCode).where(InvitationCode.created_by_uid == uid)
        )
        await session.execute(
            delete(InvitationCodeUsage).where(InvitationCodeUsage.used_by_uid == uid)
        )

        # 7. 删除支付订单
        await session.execute(delete(PaymentOrder).where(PaymentOrder.uid == uid))

        # 8. 删除管理员操作日志（可选，保留作为审计记录）
        # await session.execute(delete(AdminLog).where(AdminLog.admin_uid == uid))

        # 9. 最后删除用户本身
        await session.delete(user)

    # 清理 Redis 会话
    try:
        token = await redis_service.get_token_by_user(uid)
        if token:
            await redis_service.set_user_offline(uid, token)
    except Exception:
        pass

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="永久删除用户",
        operation_object=f"用户ID: {uid}",
        operation_details=f"永久删除用户 {user.username} (邮箱: {user.email}) 及其所有关联数据",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    global_logger.warning(
        "AdminUsers", f"管理员 {current_user['username']} 永久删除了用户 {uid}"
    )

    return ApiResponse.success(data={"uid": uid}, message="用户已永久删除")
