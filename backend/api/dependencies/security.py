"""
安全认证相关依赖

提供 JWT 令牌解析、用户认证、权限校验等功能。
"""
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Header

from core.enums import UserRole
from utils.jwt import jwt_util
from service.redis_service import redis_service
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session
from database.repositories.user_repo import UserRepository
from utils.log import global_logger

async def get_token(
    authorization: Optional[str] = Header(None, description="认证头 Authorization: Bearer <token>")
) -> str:
    """
    获取认证令牌
    
    仅从 'Authorization: Bearer <token>' 请求头获取，不再支持 query parameter 传递（安全考虑）。
    """
    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer" and param and param.strip():
            return param.strip()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未提供认证令牌，请在请求头中添加 Authorization: Bearer <token>",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(
    token: str = Depends(get_token),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    获取当前登录用户
    
    1. 尝试从 Redis 获取会话信息
    2. 验证 JWT 令牌有效性
    3. 从数据库查询用户最新信息
    4. 刷新 Redis 中的令牌过期时间
    """
    # 1. 检查Redis中的会话状态
    user_id = await redis_service.get_user_by_token(token)
    
    # 2. 验证JWT令牌
    token_payload = jwt_util.verify_token(token)
    if not token_payload:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 如果Redis中没有（可能过期），使用JWT中的uid
    if not user_id:
        user_id = token_payload.get("uid")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 从数据库获取用户（ORM 查询）
    repo = UserRepository(session)
    user = await repo.get_public_fields_by_id(int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. 在Redis中刷新令牌过期时间
    await redis_service.refresh_token_expire(user_id, token)
    
    return dict(user)

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    获取当前活跃用户
    
    可以在此扩展用户状态检查逻辑（如是否被封禁）
    """
    return current_user

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取管理员用户
    
    仅限 role='admin' 的用户访问
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

async def get_reviewer_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取审稿人用户
    
    允许 reviewer 及以上角色访问
    """
    if not UserRole.has_permission(current_user["role"], UserRole.REVIEWER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要审稿人权限"
        )
    return current_user

async def get_writer_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    [DEPRECATED] 获取作者用户
    
    此函数已废弃，请使用 get_author_user 代替
    旧角色名 'writer' 已统一为 'author' (UserRole.AUTHOR)
    
    允许 author 及以上角色访问
    """
    if not UserRole.has_permission(current_user["role"], UserRole.AUTHOR.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要作者权限"
        )
    return current_user


async def get_editor_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取编辑用户
    
    允许 editor 及以上角色访问（editor, admin）
    """
    if not UserRole.has_permission(current_user["role"], UserRole.EDITOR.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要编辑权限"
        )
    return current_user


async def get_associate_editor_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取副编辑用户
    
    允许 associate_editor 及以上角色访问
    """
    if not UserRole.has_permission(current_user["role"], UserRole.ASSOCIATE_EDITOR.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要副编辑权限"
        )
    return current_user


async def get_ea_ae_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取编辑助理用户
    
    允许 ea_ae 及以上角色访问
    """
    if not UserRole.has_permission(current_user["role"], UserRole.EA_AE.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要编辑助理权限"
        )
    return current_user


async def get_author_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取作者用户
    
    允许 author 及以上角色访问
    """
    if not UserRole.has_permission(current_user["role"], UserRole.AUTHOR.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要作者权限"
        )
    return current_user
