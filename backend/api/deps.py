from typing import Generator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Query, Header
from fastapi.security import OAuth2PasswordBearer

from utils.jwt import jwt_util
from utils.redis import redis_client
from database import db_manager

# Reusable OAuth2 scheme (optional, mostly for Swagger UI if we wanted to standard Auth header)
# But since frontend uses query param, we'll stick to custom dependency.
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

async def get_token(
    token: Optional[str] = Query(None, description="Access Token"),
    authorization: Optional[str] = Header(None, description="Authorization Header")
) -> str:
    """
    Extract token from Query param 'token' OR 'Authorization: Bearer <token>' header.
    Query param takes precedence to support existing frontend.
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
    Get current user from token.
    Validates token via Redis (for logout/expiry) and JWT signature.
    Fetches latest user data from DB.
    """
    # 1. Check Redis for session status
    user_id = await redis_client.get_user_by_token(token)
    
    # 2. If not in Redis, try to decode JWT (stateless fallback, or if Redis key expired but JWT valid?)
    # However, existing logic in user.py prefers Redis but falls back to JWT.
    # But if user logged out, Redis key is deleted. So if not in Redis, strictly speaking it might be invalid session if we enforce server-side logout.
    # But user.py line 186 says: "If not in Redis, try to parse from token".
    # We will keep this logic to be safe, but generally if we want secure logout, we should require Redis.
    # For now, let's stick to the existing hybrid approach to not break anything.
    
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

    # 3. Fetch user from DB
    user_db = db_manager.get_service('user_account')
    user = await user_db.fetchone(
        "SELECT uid, username, email, role, is_verified FROM users WHERE uid = ?",
        (user_id,)
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Refresh token expire time in Redis
    await redis_client.refresh_token_expire(user_id, token)
    
    return dict(user)

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    # If we had an 'is_active' field, we would check it here.
    # For now, just return the user.
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
