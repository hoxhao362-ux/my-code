from typing import Generator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Query, Header, Request
from fastapi.security import OAuth2PasswordBearer

from utils.jwt import jwt_util
from utils.redis import redis_client
from utils.rate_limit import rate_limiter
from database import db_manager

# --- 认证与权限相关依赖 ---

# 可复用的OAuth2方案（可选，主要用于Swagger UI标准化认证头）
# 但由于前端使用查询参数，我们将使用自定义依赖。
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

async def get_token(
    token: Optional[str] = Query(None, description="访问令牌"),
    authorization: Optional[str] = Header(None, description="认证头")
) -> str:
    """
    从查询参数 'token' 或 'Authorization: Bearer <token>' 头中提取令牌。
    查询参数优先级更高，以支持现有前端。
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

async def get_current_user(token: str = Depends(get_token)) -> Dict[str, Any]:
    """
    从令牌获取当前用户。
    通过Redis（用于登出/过期）和JWT签名验证令牌。
    从数据库获取最新用户数据。
    """
    # 1. 检查Redis中的会话状态
    user_id = await redis_client.get_user_by_token(token)
    
    # 2. 如果Redis中不存在，尝试解码JWT（无状态回退，或者Redis键过期但JWT有效？）
    # 然而，user.py中的现有逻辑优先使用Redis但回退到JWT。
    # 但如果用户已登出，Redis键会被删除。所以如果不在Redis中，严格来说如果我们强制服务器端登出，这可能是无效会话。
    # 但user.py第186行说："如果不在Redis中，尝试从令牌解析"。
    # 为了安全起见，我们将保留此逻辑，但通常如果我们想要安全登出，我们应该要求Redis。
    # 目前，为了不破坏任何东西，我们将坚持现有的混合方法。
    
    token_payload = jwt_util.verify_token(token)
    if not token_payload:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_id:
        user_id = token_payload.get("uid")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 从数据库获取用户
    user_db = db_manager.get_service('user_account')
    user = await user_db.fetchone(
        "SELECT uid, username, email, role, is_verified FROM users WHERE uid = $1",
        (user_id,)
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 在Redis中刷新令牌过期时间
    await redis_client.refresh_token_expire(user_id, token)
    
    return dict(user)

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    # 如果我们有'is_active'字段，我们会在这里检查。
    # 现在，只需返回用户。
    return current_user

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    if current_user["role"] not in ["admin", "editor", "deputy_editor", "ea_ae"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

async def get_reviewer_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    if current_user["role"] not in ["reviewer", "admin", "editor", "deputy_editor", "ea_ae"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要审稿人权限"
        )
    return current_user

async def get_writer_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    if current_user["role"] not in ["writer", "reviewer", "admin", "editor", "deputy_editor", "ea_ae"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要作者权限"
        )
    return current_user

# --- 频率限制相关依赖 ---

async def rate_limit_check(request: Request, limit: int = 100, window_seconds: int = 3600):
    """频率限制依赖项
    
    Args:
        request: 请求对象
        limit: 时间窗口内允许的最大请求数
        window_seconds: 时间窗口大小（秒）
        
    Raises:
        HTTPException: 请求频率超过限制时抛出429异常
    """
    # 使用IP地址作为请求标识
    client_ip = request.client.host
    allowed, remaining = rate_limiter.check_rate(client_ip, limit, window_seconds)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="请求频率超过限制，请稍后再试",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    return {
        "client_ip": client_ip,
        "remaining": remaining,
        "limit": limit,
        "window_seconds": window_seconds
    }

async def login_rate_limit(request: Request):
    """登录接口频率限制（更严格）"""
    # 使用IP地址作为请求标识
    client_ip = request.client.host
    # 登录接口：1分钟内最多5次请求
    allowed, remaining = rate_limiter.check_rate(client_ip, 5, 60)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="登录请求过于频繁，请稍后再试",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    return {
        "client_ip": client_ip,
        "remaining": remaining,
        "limit": 5,
        "window_seconds": 60
    }

async def register_rate_limit(request: Request):
    """注册接口频率限制（更严格）"""
    # 使用IP地址作为请求标识
    client_ip = request.client.host
    # 注册接口：1小时内最多3次请求
    allowed, remaining = rate_limiter.check_rate(client_ip, 3, 3600)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="注册请求过于频繁，请稍后再试",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    return {
        "client_ip": client_ip,
        "remaining": remaining,
        "limit": 3,
        "window_seconds": 3600
    }
