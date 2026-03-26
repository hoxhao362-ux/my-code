"""
安全认证相关依赖

提供 JWT 令牌解析、用户认证、权限校验等功能。
"""
from typing import Optional, Dict, Any, List, Union
from fastapi import Depends, HTTPException, status, Query, Header

from core.enums import UserRole
from utils.jwt import jwt_util
from service.redis_service import redis_service
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session
from database.repositories.user_repo import UserRepository
from utils.log import global_logger

async def get_token(
    token: Optional[str] = Query(None, description="访问令牌"),
    authorization: Optional[str] = Header(None, description="认证头")
) -> str:
    """
    获取认证令牌
    
    优先从查询参数 'token' 获取，其次从 'Authorization: Bearer <token>' 头获取。
    """
    if token:
        return token
    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer":
            return param
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未提供认证令牌",
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
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

async def get_reviewer_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取审稿人用户
    
    允许 role 为 'reviewer' 或 'admin' 的用户访问
    """
    if current_user["role"] not in ["reviewer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要审稿人权限"
        )
    return current_user

async def get_writer_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    获取作者用户
    
    允许 role 为 'writer', 'reviewer', 'admin' 的用户访问
    """
    if current_user["role"] not in ["writer", "reviewer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要作者权限"
        )
    return current_user


def require_role(required_roles: Union[str, List[str]]):
    """
    通用角色权限检查装饰器
    
    功能说明：
    1. 支持单个角色或角色列表
    2. 基于角色层级判断权限
    3. 返回依赖注入函数
    
    Args:
        required_roles: 所需角色（字符串或列表）
        
    Returns:
        Callable: FastAPI 依赖注入函数
        
    Example:
        @router.get("/admin-only")
        async def admin_only_endpoint(
            current_user: dict = Depends(require_role(["admin"]))
        ):
            pass
            
        @router.get("/editor-or-higher")
        async def editor_or_higher(
            current_user: dict = Depends(require_role(UserRole.EDITOR.value))
        ):
            pass
    """
    # 标准化为列表
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        current_role = current_user["role"]
        
        # 检查是否满足任一角色要求
        allowed = False
        for required_role in required_roles:
            if UserRole.has_permission(current_role, required_role):
                allowed = True
                break
        
        if not allowed:
            global_logger.warning(
                "Security", 
                f"权限不足 - uid: {current_user['uid']}, username: {current_user['username']}, "
                f"current_role: {current_role}, required_roles: {required_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色权限之一：{', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker


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
