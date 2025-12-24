from fastapi import HTTPException, Depends, Request
from utils.rate_limit import rate_limiter
from utils.jwt import jwt_util

async def get_current_user(request: Request):
    """获取当前用户信息"""
    token = request.query_params.get("token")
    if not token:
        # 尝试从Authorization头获取token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise HTTPException(status_code=401, detail="未提供token")
    
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    return user_info

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
