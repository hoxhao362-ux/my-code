from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
from datetime import datetime

from utils.jwt import jwt_util
from utils.redis import redis_client
from utils.admin_log import record_admin_log
from model.user import LoginRequest, LoginResponse
from database import db_manager
from core import dependencies as deps

user_db = db_manager.get_service('user_account')
journal_db = db_manager.get_service('journal_submit')

router = APIRouter(tags=["管理员-用户管理"])

@router.post("/login", summary="管理员登录")
async def admin_login(request: LoginRequest):
    """管理员登录接口"""
    # 从数据库查询用户
    user = await user_db.fetchone(
        "SELECT uid, password, role, email FROM users WHERE username = ?",
        (request.username,)
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查角色是否为管理员
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="非管理员账号，无权登录")
    
    # 验证密码
    if not jwt_util.verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 更新最后登录时间
    last_login_time = datetime.now().isoformat()
    await user_db.execute(
        "UPDATE users SET last_login_time = ? WHERE uid = ?",
        (last_login_time, user["uid"])
    )

    # 生成JWT token
    token = jwt_util.create_access_token({
        "uid": user["uid"],
        "username": request.username,
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
        message="登录成功"
    )

@router.get("/users", summary="获取用户列表")
async def get_users(
    page: int = 1, 
    page_size: int = 10, 
    role: Optional[str] = None,
    current_user: dict = Depends(deps.get_admin_user)
):
    """获取所有用户列表，仅限管理员访问"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 构建查询条件
    where_clause = "WHERE 1=1"
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

@router.put("/users/{uid}/role", summary="修改用户角色")
async def update_user_role(
    uid: int, 
    role: str, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user)
):
    """修改用户角色，仅限管理员访问"""
    # 检查角色有效性
    if role not in ["normal", "writer", "reviewer", "admin"]:
        raise HTTPException(status_code=400, detail="角色无效")
    
    # 检查用户是否存在
    user = await user_db.fetchone("SELECT * FROM users WHERE uid = ?", (uid,))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户角色
    await user_db.execute("UPDATE users SET role = ? WHERE uid = ?", (role, uid))
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
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

@router.delete("/users/{uid}", summary="删除用户")
async def delete_user(
    uid: int, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user)
):
    """删除用户，仅限管理员访问"""
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
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
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
