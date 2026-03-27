"""
管理中心相关 API 接口

包含系统统计、用户管理、邀请码管理等功能
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies as deps
from database.dependencies import get_db_session
from database.repositories.journal_repo import JournalRepository
from database.repositories.review_repo import ReviewRepository
from database.repositories.user_repo import UserRepository
from service.admin_log_service import admin_log_service
from utils.log import global_logger

# 创建管理中心路由
router = APIRouter(
    prefix="/admin",
    tags=["管理中心相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
    }
)


@router.get("/dashboard", summary="获取管理看板")
async def get_admin_dashboard(
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取管理系统看板数据
    
    Args:
        request: 请求对象
        current_user: 管理员用户信息
        session: 数据库会话
        
    Returns:
        dict: 管理看板统计数据
    """
    user_repo = UserRepository(session)
    journal_repo = JournalRepository(session)
    review_repo = ReviewRepository(session)

    total_users = await user_repo.count()
    user_roles = await user_repo.role_breakdown()
    total_journals = await journal_repo.count_all()
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看管理看板",
        operation_object="管理看板",
        operation_details="查询了管理系统看板数据",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    global_logger.info("Admin", f"管理员查看看板 - admin_uid: {current_user['uid']}")
    
    return {
        "total_users": total_users,
        "user_roles": user_roles,
        "total_journals": total_journals,
    }


@router.get("/statistics", summary="获取系统统计信息")
async def get_system_statistics(
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取系统统计信息，仅限管理员访问"""
    user_repo = UserRepository(session)
    journal_repo = JournalRepository(session)
    review_repo = ReviewRepository(session)

    total_users = await user_repo.count()
    user_roles = await user_repo.role_breakdown()
    total_journals = await journal_repo.count_all()
    journal_status = await journal_repo.status_breakdown()
    total_reviews = await review_repo.count_all_records()
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看系统统计",
        operation_object="系统统计信息",
        operation_details="查询了系统统计信息",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    global_logger.info("Admin", f"管理员查看系统统计 - admin_uid: {current_user['uid']}")
    
    return {
        "total_users": total_users,
        "user_roles": user_roles,
        "total_journals": total_journals,
        "journal_status": journal_status,
        "total_reviews": total_reviews,
    }


@router.get("/users", summary="用户管理列表")
async def admin_get_user_list(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """管理员获取用户列表"""
    repo = UserRepository(session)
    total = await repo.count()
    users = await repo.list_page(page, page_size)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "users": users
    }


@router.get("/invitations", summary="邀请码管理")
async def get_invitation_codes(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(deps.get_admin_user),
):
    """获取邀请码列表"""
    # TODO: 实现邀请码管理
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "invitations": []
    }


@router.post("/invitations", summary="创建邀请码")
async def create_invitation_code(
    role: str,
    max_uses: int = 1,
    description: str | None = None,
    expire_days: int | None = None,
    current_user: dict = Depends(deps.get_admin_user),
):
    """创建新的邀请码"""
    # TODO: 实现邀请码创建
    global_logger.info("Admin", f"创建邀请码 - admin_uid: {current_user['uid']}, role: {role}")
    
    return {"message": "邀请码创建成功"}
