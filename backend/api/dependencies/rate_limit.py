"""
频率限制相关依赖

提供基于 Redis 的分布式频率限制功能，支持多 Worker 进程。
"""

from fastapi import HTTPException, Request
from service.rate_limit_service import rate_limit_service
from utils.log import global_logger


async def rate_limit_check(request: Request, preset: str = "general"):
    """
    通用频率限制依赖项

    按预设策略检查请求频率，使用客户端 IP 作为标识。

    Args:
        request: 请求对象
        preset: 预设策略名称（general / login / register / upload / captcha）

    Raises:
        HTTPException: 请求频率超过限制时抛出 429 异常
    """
    # 使用 IP 地址作为请求标识
    client_ip = request.client.host if request.client else "unknown"

    allowed, count = await rate_limit_service.check(preset, client_ip)

    if not allowed:
        cfg = rate_limit_service.get_preset_config(preset)
        global_logger.warning(
            "RateLimit",
            f"频率限制拒绝访问 - 策略: {preset}, IP: {client_ip}, "
            f"累计: {count}/{cfg['max_attempts']}",
        )
        raise HTTPException(
            status_code=429,
            detail="请求频率超过限制，请稍后再试",
            headers={"X-RateLimit-Remaining": "0"},
        )

    cfg = rate_limit_service.get_preset_config(preset)
    return {
        "client_ip": client_ip,
        "remaining": cfg["max_attempts"] - count,
        "limit": cfg["max_attempts"],
        "window_seconds": cfg["window_seconds"],
    }


async def login_rate_limit(request: Request):
    """
    登录接口频率限制

    策略：1分钟内最多5次请求
    """
    return await rate_limit_check(request, preset="login")


async def register_rate_limit(request: Request):
    """
    注册接口频率限制

    策略：1小时内最多3次请求
    """
    return await rate_limit_check(request, preset="register")


async def upload_rate_limit(request: Request):
    """
    上传接口频率限制

    策略：1小时内最多10次请求
    """
    return await rate_limit_check(request, preset="upload")


async def captcha_rate_limit(request: Request):
    """
    验证码接口频率限制

    策略：1分钟内最多10次请求
    """
    return await rate_limit_check(request, preset="captcha")
