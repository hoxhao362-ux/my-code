"""
频率限制相关依赖

提供基于IP的请求频率限制功能。
"""
from fastapi import Request, HTTPException
from service.rate_limit_service import rate_limit_service

async def rate_limit_check(request: Request, limit: int = 100, window_seconds: int = 3600):
    """
    通用频率限制依赖项
    
    Args:
        request: 请求对象
        limit: 时间窗口内允许的最大请求数
        window_seconds: 时间窗口大小（秒）
        
    Raises:
        HTTPException: 请求频率超过限制时抛出429异常
    """
    # 使用IP地址作为请求标识
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = rate_limit_service.check_rate(client_ip, limit, window_seconds)
    
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
    """
    登录接口频率限制
    
    策略：1分钟内最多5次请求
    """
    return await rate_limit_check(request, limit=5, window_seconds=60)

async def register_rate_limit(request: Request):
    """
    注册接口频率限制
    
    策略：1小时内最多3次请求
    """
    return await rate_limit_check(request, limit=3, window_seconds=3600)
