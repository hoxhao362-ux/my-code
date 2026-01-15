from fastapi import APIRouter, Depends, Request
from database import db_manager
from utils.admin_log import record_admin_log
from core import dependencies as deps

from .users import router as users_router
from .journals import router as journals_router
from .invitations import router as invitations_router

user_db = db_manager.get_service('user_account')
journal_db = db_manager.get_service('journal_submit')

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
    current_user: dict = Depends(deps.get_admin_user)
):
    """获取系统统计信息，仅限管理员访问"""
    # 统计用户总数
    total_users = await user_db.fetchval("SELECT COUNT(*) FROM users")
    
    # 按角色统计用户
    user_roles = await user_db.fetchall(
        "SELECT role, COUNT(*) as count FROM users GROUP BY role"
    )
    
    # 统计文献总数
    total_journals = await journal_db.fetchval("SELECT COUNT(*) FROM journals")
    
    # 按状态统计文献
    journal_status = await journal_db.fetchall(
        "SELECT status, COUNT(*) as count FROM journals GROUP BY status"
    )
    
    # 统计审核记录总数
    total_reviews = await journal_db.fetchval("SELECT COUNT(*) FROM review_records")
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看系统统计",
        operation_object="系统统计信息",
        operation_details="查询了系统统计信息",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "total_users": total_users,
        "user_roles": [dict(role) for role in user_roles],
        "total_journals": total_journals,
        "journal_status": [dict(status) for status in journal_status],
        "total_reviews": total_reviews
    }
