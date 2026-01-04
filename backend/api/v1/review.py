from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from utils.jwt import jwt_util
from model.journal import JournalInfo
from model.user import LoginRequest, LoginResponse
# 获取数据库服务实例
from database import db_manager
journal_db = db_manager.get_service('journal_submit')

review_router = APIRouter(
    prefix="/review",
    tags=["审稿相关接口"],
)

@review_router.post("/login", summary="审稿人登录")
async def reviewer_login(request: LoginRequest):
    """审稿人登录接口"""
    # TODO: 实现审稿人登录逻辑
    ...

@review_router.get("/pending", summary="获取待审核文献列表")
async def get_pending_journals(token: str, page: int = 1, page_size: int = 10):
    """获取待审核的文献列表，仅限审稿人访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "reviewer" and user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询待审核文献总数
    total = await journal_db.fetchval(
        "SELECT COUNT(*) FROM journals WHERE status = 'pending'"
    )
    
    # 查询待审核文献列表
    journals = await journal_db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE status = 'pending' 
        ORDER BY create_time DESC 
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**journal)
        for journal in journals
    ]
    
    return {
        "total": total,
        "journals": journal_list
    }

@review_router.post("/review/{jid}", summary="审核文献")
async def review_journal(
    jid: int,
    token: str,
    result: str,
    comment: Optional[str] = None
):
    """审核文献，仅限审稿人访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "reviewer" and user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 检查结果有效性
    if result not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="审核结果无效，只能是approved或rejected")
    
    # 查询文献是否存在
    journal = await journal_db.fetchone(
        "SELECT * FROM journals WHERE jid = ?",
        (jid,)
    )
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查文献是否处于待审核状态
    if journal["status"] != "pending":
        raise HTTPException(status_code=400, detail="该文献已被审核")
    
    # 更新文献状态
    update_time = datetime.now().isoformat()
    await journal_db.execute(
        "UPDATE journals SET status = ?, update_time = ? WHERE jid = ?",
        (result, update_time, jid)
    )
    
    # 记录审核记录
    review_time = datetime.now().isoformat()
    await journal_db.execute(
        """
        INSERT INTO review_records (jid, reviewer_uid, review_time, result, comment)
        VALUES (?, ?, ?, ?, ?)
        """,
        (jid, user_info["uid"], review_time, result, comment)
    )
    
    return {
        "message": "审核成功",
        "result": result,
        "comment": comment
    }

@review_router.get("/history", summary="获取审核历史记录")
async def get_review_history(token: str, page: int = 1, page_size: int = 10):
    """获取当前审稿人的审核历史记录"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "reviewer" and user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询审核历史记录总数
    total = await journal_db.fetchval(
        "SELECT COUNT(*) FROM review_records WHERE reviewer_uid = ?",
        (user_info["uid"],)
    )
    
    # 查询审核历史记录
    review_records = await journal_db.fetchall(
        """
        SELECT rr.*, j.title, j.authors, j.status
        FROM review_records rr
        JOIN journals j ON rr.jid = j.jid
        WHERE rr.reviewer_uid = ?
        ORDER BY rr.review_time DESC
        LIMIT ? OFFSET ?
        """,
        (user_info["uid"], page_size, offset)
    )
    
    return {
        "total": total,
        "records": [dict(record) for record in review_records]
    }

@review_router.get("/statistics", summary="获取审核统计信息")
async def get_review_statistics(token: str):
    """获取审核统计信息，仅限审稿人访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "reviewer" and user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 查询总审核数
    total = await journal_db.fetchval(
        "SELECT COUNT(*) FROM review_records WHERE reviewer_uid = ?",
        (user_info["uid"],)
    )
    
    # 查询通过数
    approved = await journal_db.fetchval(
        "SELECT COUNT(*) FROM review_records WHERE reviewer_uid = ? AND result = 'approved'",
        (user_info["uid"],)
    )
    
    # 查询拒绝数
    rejected = await journal_db.fetchval(
        "SELECT COUNT(*) FROM review_records WHERE reviewer_uid = ? AND result = 'rejected'",
        (user_info["uid"],)
    )
    
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "approval_rate": approved / total if total > 0 else 0
    }

@review_router.get("/rejected", summary="获取被拒绝的文献列表")
async def get_rejected_journals(token: str, page: int = 1, page_size: int = 10):
    """获取被拒绝的文献列表，包含审核意见"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "reviewer" and user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询被拒绝文献总数
    total = await journal_db.fetchval(
        "SELECT COUNT(*) FROM journals WHERE status = 'rejected'"
    )
    
    # 查询被拒绝文献列表
    rejected_journals = await journal_db.fetchall(
        """
        SELECT j.*, rr.comment, rr.review_time
        FROM journals j
        JOIN review_records rr ON j.jid = rr.jid
        WHERE j.status = 'rejected'
        ORDER BY j.update_time DESC
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    return {
        "total": total,
        "journals": [dict(journal) for journal in rejected_journals]
    }
