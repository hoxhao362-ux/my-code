from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from utils.database import db
from utils.jwt import jwt_util

admin_router = APIRouter(
    prefix="/admin",
    tags=["管理员相关接口"],
)

@admin_router.get("/users", summary="获取用户列表")
async def get_users(token: str, page: int = 1, page_size: int = 10, role: Optional[str] = None):
    """获取所有用户列表，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 构建查询条件
    where_clause = """
    WHERE 1=1
    """
    params = []
    
    if role:
        where_clause += " AND role = ?"
        params.append(role)
    
    # 查询用户总数
    count_sql = f"SELECT COUNT(*) FROM users {where_clause}"
    total = await db.fetchval(count_sql, tuple(params))
    
    # 查询用户列表
    users_sql = f"""
    SELECT uid, username, email, role, is_verified, create_time, last_login_time
    FROM users 
    {where_clause}
    ORDER BY create_time DESC 
    LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])
    users = await db.fetchall(users_sql, tuple(params))
    
    return {
        "total": total,
        "users": [dict(user) for user in users]
    }

@admin_router.put("/users/{uid}/role", summary="修改用户角色")
async def update_user_role(uid: int, token: str, role: str):
    """修改用户角色，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 检查角色有效性
    if role not in ["user", "reviewer", "admin"]:
        raise HTTPException(status_code=400, detail="角色无效，只能是user、reviewer或admin")
    
    # 检查用户是否存在
    user = await db.fetchone("SELECT * FROM users WHERE uid = ?", (uid,))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户角色
    await db.execute("UPDATE users SET role = ? WHERE uid = ?", (role, uid))
    await db.commit()
    
    return {
        "message": "用户角色更新成功",
        "uid": uid,
        "new_role": role
    }

@admin_router.delete("/users/{uid}", summary="删除用户")
async def delete_user(uid: int, token: str):
    """删除用户，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 检查用户是否存在
    user = await db.fetchone("SELECT * FROM users WHERE uid = ?", (uid,))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 删除用户的文献和审核记录
    await db.execute("DELETE FROM review_records WHERE reviewer_uid = ?", (uid,))
    await db.execute("DELETE FROM journals WHERE uid = ?", (uid,))
    await db.execute("DELETE FROM users WHERE uid = ?", (uid,))
    await db.commit()
    
    return {
        "message": "用户删除成功",
        "uid": uid
    }

@admin_router.get("/journals/all", summary="获取所有文献列表")
async def get_all_journals(token: str, page: int = 1, page_size: int = 10, status: Optional[str] = None):
    """获取所有文献列表，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 构建查询条件
    where_clause = """
    WHERE 1=1
    """
    params = []
    
    if status:
        where_clause += " AND status = ?"
        params.append(status)
    
    # 查询文献总数
    count_sql = f"SELECT COUNT(*) FROM journals {where_clause}"
    total = await db.fetchval(count_sql, tuple(params))
    
    # 查询文献列表
    journals_sql = f"""
    SELECT j.jid, j.title, j.authors, j.abstract, j.status, j.file_name, j.file_size, j.create_time, j.update_time, u.username as uploader
    FROM journals j
    JOIN users u ON j.uid = u.uid
    {where_clause}
    ORDER BY j.create_time DESC 
    LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])
    journals = await db.fetchall(journals_sql, tuple(params))
    
    return {
        "total": total,
        "journals": [dict(journal) for journal in journals]
    }

@admin_router.delete("/journals/{jid}", summary="删除文献")
async def admin_delete_journal(jid: int, token: str):
    """删除文献，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 查询文献
    journal = await db.fetchone(
        "SELECT file_hash, file_bucket, file_name FROM journals WHERE jid = ?",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 获取配置
    from main import global_config
    paper_dir = Path(global_config['global']['paper_dir'])
    
    # 删除文件
    file_ext = Path(journal["file_name"]).suffix
    file_path = paper_dir / journal["file_bucket"] / f"{journal['file_hash']}{file_ext}"
    if file_path.exists():
        file_path.unlink()
    
    # 删除审核记录
    await db.execute("DELETE FROM review_records WHERE jid = ?", (jid,))
    
    # 删除文献数据
    await db.execute("DELETE FROM journals WHERE jid = ?", (jid,))
    await db.commit()
    
    return {"message": "文献删除成功"}

@admin_router.get("/review-records", summary="获取所有审核记录")
async def get_all_review_records(token: str, page: int = 1, page_size: int = 10):
    """获取所有审核记录，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询审核记录总数
    total = await db.fetchval("SELECT COUNT(*) FROM review_records")
    
    # 查询审核记录
    review_records = await db.fetchall(
        """
        SELECT rr.*, j.title, u.username as reviewer_name
        FROM review_records rr
        JOIN journals j ON rr.jid = j.jid
        JOIN users u ON rr.reviewer_uid = u.uid
        ORDER BY rr.review_time DESC
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    return {
        "total": total,
        "records": [dict(record) for record in review_records]
    }

@admin_router.get("/statistics", summary="获取系统统计信息")
async def get_system_statistics(token: str):
    """获取系统统计信息，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 统计用户总数
    total_users = await db.fetchval("SELECT COUNT(*) FROM users")
    
    # 按角色统计用户
    user_roles = await db.fetchall(
        "SELECT role, COUNT(*) as count FROM users GROUP BY role"
    )
    
    # 统计文献总数
    total_journals = await db.fetchval("SELECT COUNT(*) FROM journals")
    
    # 按状态统计文献
    journal_status = await db.fetchall(
        "SELECT status, COUNT(*) as count FROM journals GROUP BY status"
    )
    
    # 统计审核记录总数
    total_reviews = await db.fetchval("SELECT COUNT(*) FROM review_records")
    
    return {
        "total_users": total_users,
        "user_roles": [dict(role) for role in user_roles],
        "total_journals": total_journals,
        "journal_status": [dict(status) for status in journal_status],
        "total_reviews": total_reviews
    }
