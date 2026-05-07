"""
[DEPRECATED] 审稿相关API接口

本模块已废弃，请勿在新代码中使用。
- 登录功能已迁移至 auth.py
- 审稿功能已迁移至 reviews.py
- Journal 模型已统一为 Manuscript 模型

废弃日期：2026-03-26
保留原因：向后兼容
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.journal import JournalInfo
from api import dependencies as deps
from database.dependencies import get_db_session
from database.orm.models.journal import Journal, ReviewRecord
from database.repositories.journal_repo import JournalRepository
from database.repositories.review_repo import ReviewRepository
from database.uow import transactional

review_router = APIRouter(
    prefix="/review",
    tags=["[已废弃] 审稿相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
)

# ========== 已废弃的登录接口 ==========
# 以下登录端点已废弃，请使用 POST /api/v1/auth/login 代替
# 符合角色要求的用户均可通过统一登录接口登录

# @review_router.post("/login", summary="审稿人登录", response_model=LoginResponse)
# async def reviewer_login(...) 已移除 - 请使用 auth.py 中的登录接口

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
