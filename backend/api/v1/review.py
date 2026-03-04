from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.jwt import jwt_util
from service.redis_service import redis_service
from model.journal import JournalInfo
from model.user import LoginRequest, LoginResponse
from api import dependencies as deps
from database.dependencies import get_db_session
from database.orm.models.journal import Journal, ReviewRecord
from database.orm.models.user import User
from database.repositories.journal_repo import JournalRepository
from database.repositories.review_repo import ReviewRepository
from database.repositories.user_repo import UserRepository
from database.uow import transactional

review_router = APIRouter(
    prefix="/review",
    tags=["审稿相关接口"],
)

@review_router.post("/login", summary="审稿人登录", response_model=LoginResponse)
async def reviewer_login(
    request: LoginRequest,
    req: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """审稿人登录接口 - 支持reviewer及以上角色登录"""
    # 获取客户端IP
    client_ip = req.client.host if req.client else "unknown"
    
    # 检查登录频率限制
    allowed, attempts = await redis_service.set_login_limit(client_ip, max_attempts=5, expire_time=3600)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"登录请求过于频繁，请稍后再试。当前尝试次数：{attempts}/5"
        )
    
    user_repo = UserRepository(session)
    user = await user_repo.get_by_username(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not jwt_util.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户角色权限（reviewer及以上角色才能登录审核系统）
    allowed_roles = ["reviewer", "admin"]
    if user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="该用户没有审核权限，需要使用reviewer及以上角色的账号登录")
    
    # 更新最后登录时间
    async with transactional(session):
        user.last_login_time = datetime.now().isoformat()
    
    # 生成token
    token = jwt_util.create_access_token({
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    })
    
    # 设置用户在线状态
    expire_time = 3600 * 24 * 30 if request.is_remember else 3600
    await redis_service.set_user_online(
        user_id=user.uid,
        token=token,
        expire_time=expire_time
    )
    
    return LoginResponse(
        login_time=datetime.now(),
        is_remember=request.is_remember,
        token=token,
        message="审稿人登录成功"
    )

@review_router.get("/pending", summary="获取待审核文献列表")
async def get_pending_journals(
    page: int = 1, 
    page_size: int = 10,
    current_user: dict = Depends(deps.get_reviewer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取待审核的文献列表，仅限审稿人访问"""
    # 查询待审核文献总数
    journal_repo = JournalRepository(session)
    total = await journal_repo.count_by_status("pending")
    rows = await journal_repo.list_by_status_page("pending", page, page_size)
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**dict(row))
        for row in rows
    ]
    
    return {
        "total": total,
        "journals": journal_list
    }

@review_router.post("/review/{jid}", summary="审核文献")
async def review_journal(
    jid: int,
    result: str,
    comment: Optional[str] = None,
    current_user: dict = Depends(deps.get_reviewer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """审核文献，仅限审稿人访问"""
    # 检查结果有效性
    if result not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="审核结果无效，只能是approved或rejected")
    
    # 查询文献是否存在
    journal = await session.scalar(select(Journal).where(Journal.jid == jid).with_for_update())
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查文献是否处于待审核状态
    if journal.status != "pending":
        raise HTTPException(status_code=400, detail="该文献已被审核")
    
    review_repo = ReviewRepository(session)
    async with transactional(session):
        journal.status = result
        journal.update_time = datetime.now().isoformat()

        review_repo.add_review_record(
            ReviewRecord(
                jid=jid,
                reviewer_uid=current_user["uid"],
                review_time=datetime.now().isoformat(),
                result=result,
                comment=comment,
            )
        )
    
    return {
        "message": "审核成功",
        "result": result,
        "comment": comment
    }

@review_router.get("/history", summary="获取审核历史记录")
async def get_review_history(
    page: int = 1, 
    page_size: int = 10,
    current_user: dict = Depends(deps.get_reviewer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取当前审稿人的审核历史记录"""
    # 查询审核历史记录总数
    review_repo = ReviewRepository(session)
    total = await review_repo.count_by_reviewer(current_user["uid"])
    rows = await review_repo.list_history_page(current_user["uid"], page, page_size)
    
    return {
        "total": total,
        "records": [dict(r) for r in rows],
    }

@review_router.get("/statistics", summary="获取审核统计信息")
async def get_review_statistics(
    current_user: dict = Depends(deps.get_reviewer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取审核统计信息，仅限审稿人访问"""
    # 查询总审核数
    review_repo = ReviewRepository(session)
    total = await review_repo.count_by_reviewer(current_user["uid"])
    approved = await review_repo.count_by_reviewer_and_result(current_user["uid"], "approved")
    rejected = await review_repo.count_by_reviewer_and_result(current_user["uid"], "rejected")
    
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "approval_rate": (approved / total) if total > 0 else 0,
    }

@review_router.get("/rejected", summary="获取被拒绝的文献列表")
async def get_rejected_journals(
    page: int = 1, 
    page_size: int = 10,
    current_user: dict = Depends(deps.get_reviewer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取被拒绝的文献列表，包含审核意见"""
    # 查询被拒绝文献总数
    review_repo = ReviewRepository(session)
    total = await review_repo.count_rejected_journals()
    rows = await review_repo.list_rejected_journals_page(page, page_size)
    
    return {
        "total": total,
        "journals": [dict(r) for r in rows],
    }
