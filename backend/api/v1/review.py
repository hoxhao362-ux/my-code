from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime

from utils.jwt import jwt_util
from utils.redis import redis_client
from model.journal import JournalInfo
from model.user import LoginRequest, LoginResponse
# 获取数据库服务实例
from database import db_manager
user_db = db_manager.get_service('user_account')
journal_db = db_manager.get_service('journal_submit')

review_router = APIRouter(
    prefix="/review",
    tags=["审稿相关接口"],
)

@review_router.post("/login", summary="审稿人登录", response_model=LoginResponse)
async def reviewer_login(request: LoginRequest, req: Request):
    """审稿人登录接口 - 支持reviewer及以上角色登录"""
    # 获取客户端IP
    client_ip = req.client.host
    
    # 检查登录频率限制
    allowed, attempts = await redis_client.set_login_limit(client_ip, max_attempts=5, expire_time=3600)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"登录请求过于频繁，请稍后再试。当前尝试次数：{attempts}/5"
        )
    
    # 检查用户是否存在
    user = await user_db.fetchone(
        "SELECT * FROM users WHERE username = ?",
        (request.username,)
    )
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not jwt_util.verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户角色权限（reviewer及以上角色才能登录审核系统）
    allowed_roles = ["reviewer", "admin"]
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="该用户没有审核权限，需要使用reviewer及以上角色的账号登录")
    
    # 更新最后登录时间
    last_login_time = datetime.now().isoformat()
    await user_db.execute(
        "UPDATE users SET last_login_time = ? WHERE uid = ?",
        (last_login_time, user["uid"])
    )
    
    # 生成token
    token = jwt_util.create_access_token({
        "uid": user["uid"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    })
    
    # 设置用户在线状态
    expire_time = 3600 * 24 * 30 if request.is_remember else 3600
    await redis_client.set_user_online(
        user_id=user["uid"],
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
