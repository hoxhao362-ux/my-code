from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime

from database import db_manager

# 获取数据库服务实例
user_db = db_manager.get_service('user_account')
journal_db = db_manager.get_service('journal_submit')
deleted_journal_db = db_manager.get_service('deleted_journal')
from utils.jwt import jwt_util
from utils.admin_log import record_admin_log

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
    total = await user_db.fetchval(count_sql, tuple(params))
    
    # 查询用户列表
    users_sql = f"""
    SELECT uid, username, email, role, is_verified, create_time, last_login_time
    FROM users 
    {where_clause}
    ORDER BY create_time DESC 
    LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])
    users = await user_db.fetchall(users_sql, tuple(params))
    
    return {
        "total": total,
        "users": [dict(user) for user in users]
    }

@admin_router.put("/users/{uid}/role", summary="修改用户角色")
async def update_user_role(uid: int, token: str, role: str, request: Request):
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
    user = await user_db.fetchone("SELECT * FROM users WHERE uid = ?", (uid,))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户角色
    await user_db.execute("UPDATE users SET role = ? WHERE uid = ?", (role, uid))
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="修改用户角色",
        operation_object=f"用户ID: {uid}",
        operation_details=f"将用户角色从 {user['role']} 修改为 {role}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "message": "用户角色更新成功",
        "uid": uid,
        "new_role": role
    }

@admin_router.delete("/users/{uid}", summary="删除用户")
async def delete_user(uid: int, token: str, request: Request):
    """删除用户，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 检查用户是否存在
    user = await user_db.fetchone("SELECT * FROM users WHERE uid = ?", (uid,))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 删除用户的文献和审核记录
    await journal_db.execute("DELETE FROM review_records WHERE reviewer_uid = ?", (uid,))
    await journal_db.execute("DELETE FROM journals WHERE uid = ?", (uid,))
    await user_db.execute("DELETE FROM users WHERE uid = ?", (uid,))
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="删除用户",
        operation_object=f"用户ID: {uid}",
        operation_details=f"删除用户 {user['username']} (邮箱: {user['email']})",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "message": "用户删除成功",
        "uid": uid
    }

@admin_router.get("/journals/all", summary="获取所有文献列表")
async def get_all_journals(token: str, page: int = 1, page_size: int = 10, status: Optional[str] = None, request: Request = None):
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
    total = await journal_db.fetchval(count_sql, tuple(params))
    
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
    journals = await journal_db.fetchall(journals_sql, tuple(params))
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="查看所有文献",
        operation_object=f"页码: {page}, 每页条数: {page_size}, 状态: {status if status else '全部'}",
        operation_details=f"查询了所有文献，共 {total} 条",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "total": total,
        "journals": [dict(journal) for journal in journals]
    }

@admin_router.delete("/journals/{jid}", summary="删除文献")
async def admin_delete_journal(jid: int, token: str, request: Request):
    """删除文献（软删除），仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 查询文献
    journal = await journal_db.fetchone(
        "SELECT jid, uid, title, authors, abstract, file_hash, file_bucket, file_name, file_size FROM journals WHERE jid = ?",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 软删除：将文献状态改为deleted
    await journal_db.execute(
        "UPDATE journals SET status = 'deleted', update_time = ? WHERE jid = ?",
        (datetime.now().isoformat(), jid)
    )
    
    # 将已删除文献信息添加到已删除文献表
    await deleted_journal_db.execute(
        """
        INSERT INTO deleted_journals (
            original_jid, uid, title, authors, abstract, file_hash, 
            file_bucket, file_name, file_size, delete_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            journal["jid"],
            journal["uid"],
            journal["title"],
            journal["authors"],
            journal["abstract"],
            journal["file_hash"],
            journal["file_bucket"],
            journal["file_name"],
            journal["file_size"],
            datetime.now().isoformat()
        )
    )
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="删除文献",
        operation_object=f"文献ID: {jid}",
        operation_details=f"将文献 {journal['title']} 标记为已删除",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "文献删除成功"}

@admin_router.get("/review-records", summary="获取所有审核记录")
async def get_all_review_records(token: str, page: int = 1, page_size: int = 10, request: Request = None):
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
    total = await journal_db.fetchval("SELECT COUNT(*) FROM review_records")
    
    # 查询审核记录
    review_records = await journal_db.fetchall(
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
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="查看审核记录",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了所有审核记录，共 {total} 条",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "total": total,
        "records": [dict(record) for record in review_records]
    }

@admin_router.get("/statistics", summary="获取系统统计信息")
async def get_system_statistics(token: str, request: Request = None):
    """获取系统统计信息，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
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
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="查看系统统计",
        operation_object="系统统计信息",
        operation_details="查询了系统统计信息",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "total_users": total_users,
        "user_roles": [dict(role) for role in user_roles],
        "total_journals": total_journals,
        "journal_status": [dict(status) for status in journal_status],
        "total_reviews": total_reviews
    }


@admin_router.get("/journals/deleted", summary="获取已删除文献列表")
async def get_deleted_journals(token: str, page: int = 1, page_size: int = 10, request: Request = None):
    """获取所有已删除文献列表，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 从主数据库查询已删除文献
    # 查询文献总数
    total = await journal_db.fetchval("SELECT COUNT(*) FROM journals WHERE status = 'deleted'")
    
    # 查询文献列表
    journals = await journal_db.fetchall(
        """
        SELECT j.jid, j.title, j.authors, j.abstract, j.status, j.file_name, j.file_size, j.create_time, j.update_time, u.username as uploader
        FROM journals j
        JOIN users u ON j.uid = u.uid
        WHERE j.status = 'deleted'
        ORDER BY j.update_time DESC 
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="查看已删除文献",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了已删除文献，共 {total} 条",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "total": total,
        "journals": [dict(journal) for journal in journals]
    }


@admin_router.delete("/journals/deleted/{jid}", summary="彻底删除文献")
async def permanently_delete_journal(jid: int, token: str, request: Request):
    """彻底删除已删除文献，仅限管理员访问"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查权限
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此接口")
    
    # 查询文献
    journal = await journal_db.fetchone(
        "SELECT jid, uid, title, file_hash, file_bucket, file_name FROM journals WHERE jid = ? AND status = 'deleted'",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="已删除文献不存在")
    
    # 获取配置
    from main import global_config
    paper_dir = Path(global_config['global']['paper_dir'])
    
    # 删除文件
    file_ext = Path(journal["file_name"]).suffix
    file_path = paper_dir / journal["file_bucket"] / f"{journal['file_hash']}{file_ext}"
    if file_path.exists():
        file_path.unlink()
    
    # 删除审核记录
    await journal_db.execute("DELETE FROM review_records WHERE jid = ?", (jid,))
    
    # 从主表中彻底删除文献
    await journal_db.execute("DELETE FROM journals WHERE jid = ?", (jid,))
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=user_info["uid"],
        admin_username=user_info["username"],
        operation_type="彻底删除文献",
        operation_object=f"文献ID: {jid}",
        operation_details=f"彻底删除了文献 {journal['title']}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "文献彻底删除成功"}
