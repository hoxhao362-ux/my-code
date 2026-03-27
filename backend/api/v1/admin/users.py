from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
from datetime import datetime

from utils.jwt import jwt_util
from service.redis_service import redis_service
from service.admin_log_service import admin_log_service
from model.user import LoginRequest, LoginResponse
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies as deps
from database.dependencies import get_db_session
from database.orm.models.journal import Journal, ReviewRecord
from database.orm.models.user import User
from database.repositories.user_repo import UserRepository
from database.uow import transactional
from model.response import ApiResponse

router = APIRouter(tags=["管理员-用户管理"])

@router.post("/login", summary="管理员登录")
async def admin_login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """管理员登录接口"""
    # 从数据库查询用户
    user_repo = UserRepository(session)
    user = await user_repo.get_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查角色是否为管理员
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="非管理员账号，无权登录")
    
    # 验证密码
    if not jwt_util.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 更新最后登录时间
    async with transactional(session):
        user.last_login_time = datetime.now().isoformat()

    # 生成JWT token
    token = jwt_util.create_access_token({
        "uid": user.uid,
        "username": request.username,
        "email": user.email,
        "role": user.role,
    })
    
    # 设置用户在线状态
    expire_time = 3600 * 24 * 30 if request.is_remember else 3600
    await redis_service.set_user_online(user_id=user.uid, token=token, expire_time=expire_time)

    return ApiResponse.success(data={
        "login_time": datetime.now().isoformat(),
        "is_remember": request.is_remember,
        "token": token,
    }, message="登录成功")

@router.get("/users", summary="获取用户列表")
async def get_users(
    page: int = 1, 
    page_size: int = 10, 
    role: Optional[str] = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有用户列表，仅限管理员访问"""
    user_repo = UserRepository(session)
    total = await user_repo.count(role=role)
    users = await user_repo.list_page(page=page, page_size=page_size, role=role)
    
    return ApiResponse.success(data={
        "total": total,
        "users": users,
    })

@router.put("/users/{uid}/role", summary="修改用户角色")
async def update_user_role(
    uid: int, 
    role: str, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """修改用户角色，仅限管理员访问"""
    # 检查角色有效性
    if role not in ["normal", "writer", "reviewer", "admin"]:
        raise HTTPException(status_code=400, detail="角色无效")
    
    user_repo = UserRepository(session)
    async with transactional(session):
        user = await user_repo.get_by_id(uid)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        old_role = user.role
        user.role = role
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="修改用户角色",
        operation_object=f"用户ID: {uid}",
        operation_details=f"将用户角色从 {old_role} 修改为 {role}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    return ApiResponse.success(data={
        "uid": uid,
        "new_role": role
    }, message="用户角色更新成功")

@router.delete("/users/{uid}", summary="删除用户")
async def delete_user(
    uid: int, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """删除用户，仅限管理员访问"""
    user_repo = UserRepository(session)
    async with transactional(session):
        user = await user_repo.get_by_id(uid)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        await session.execute(delete(ReviewRecord).where(ReviewRecord.reviewer_uid == uid))
        await session.execute(delete(Journal).where(Journal.uid == uid))
        await session.execute(delete(User).where(User.uid == uid))
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="删除用户",
        operation_object=f"用户ID: {uid}",
        operation_details=f"删除用户 {user.username} (邮箱: {user.email})",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    return ApiResponse.success(data={"uid": uid}, message="用户删除成功")
