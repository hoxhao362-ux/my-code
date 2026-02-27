from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies as deps
from database.dependencies import get_db_session
from database.repositories.journal_repo import JournalRepository
from database.repositories.review_repo import ReviewRepository
from database.repositories.user_repo import UserRepository
from service.admin_log_service import admin_log_service

from .users import router as users_router
from .journals import router as journals_router
from .invitations import router as invitations_router

admin_router = APIRouter(
    prefix="/admin",
    tags=["管理员相关接口"],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
    }
)

admin_router.include_router(users_router)
admin_router.include_router(journals_router)
admin_router.include_router(invitations_router)

@admin_router.get("/statistics", summary="获取系统统计信息")
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
    
    return {
        "total_users": total_users,
        "user_roles": user_roles,
        "total_journals": total_journals,
        "journal_status": journal_status,
        "total_reviews": total_reviews,
    }
