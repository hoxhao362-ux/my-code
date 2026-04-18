"""
频率限制服务模块

基于 Redis 的分布式频率限制服务。
所有频率限制统一通过 Redis 原子操作实现，支持多 Worker 进程。
"""
from typing import Dict, Tuple

from service.redis_service import redis_service
from utils.log import global_logger


class RateLimitService:
    """
    基于 Redis 的分布式频率限制服务

    通过委托 redis_service.increment_rate_limit() 实现，
    使用 Lua 脚本原子操作确保多 Worker 进程下的计数一致性。
    """

    # 预设策略配置
    PRESETS: Dict[str, Dict[str, int]] = {
        "general": {"max_attempts": 100, "window_seconds": 3600},
        "login": {"max_attempts": 5, "window_seconds": 60},
        "register": {"max_attempts": 3, "window_seconds": 3600},
        "upload": {"max_attempts": 10, "window_seconds": 3600},
        "captcha": {"max_attempts": 10, "window_seconds": 60},
    }

    async def check(self, preset: str, identifier: str) -> Tuple[bool, int]:
        """
        按预设策略检查频率限制

        自动递增计数器并判断是否超限。首次请求时在 Redis 中创建键并设置过期时间。

        Args:
            preset: 预设策略名称（general / login / register / upload / captcha）
            identifier: 限制对象标识（如 IP 地址、用户 ID）

        Returns:
            Tuple[bool, int]: (是否允许本次操作, 当前累计次数)

        Raises:
            ValueError: 预设策略不存在时抛出
        """
        if preset not in self.PRESETS:
            raise ValueError(
                f"未知的频率限制预设策略: {preset}，"
                f"可选值: {', '.join(self.PRESETS.keys())}"
            )

        cfg = self.PRESETS[preset]
        allowed, count = await redis_service.increment_rate_limit(
            key_prefix=preset,
            identifier=identifier,
            max_attempts=cfg["max_attempts"],
            window_seconds=cfg["window_seconds"],
        )

        if not allowed:
            global_logger.warning(
                "RateLimit",
                f"频率限制触发 - 策略: {preset}, 标识: {identifier}, "
                f"累计: {count}/{cfg['max_attempts']}, 窗口: {cfg['window_seconds']}s"
            )

        return allowed, count

    async def check_custom(
        self,
        key_prefix: str,
        identifier: str,
        max_attempts: int,
        window_seconds: int,
    ) -> Tuple[bool, int]:
        """
        自定义参数的频率限制检查

        当预设策略无法满足需求时，可使用自定义参数。

        Args:
            key_prefix: 限制类型前缀（如 "password_reset"）
            identifier: 限制对象标识（如 IP 地址）
            max_attempts: 时间窗口内最大尝试次数
            window_seconds: 时间窗口（秒）

        Returns:
            Tuple[bool, int]: (是否允许本次操作, 当前累计次数)
        """
        allowed, count = await redis_service.increment_rate_limit(
            key_prefix=key_prefix,
            identifier=identifier,
            max_attempts=max_attempts,
            window_seconds=window_seconds,
        )

        if not allowed:
            global_logger.warning(
                "RateLimit",
                f"频率限制触发 - 自定义前缀: {key_prefix}, 标识: {identifier}, "
                f"累计: {count}/{max_attempts}, 窗口: {window_seconds}s"
            )

        return allowed, count

    def get_preset_config(self, preset: str) -> Dict[str, int]:
        """
        获取预设策略配置

        Args:
            preset: 预设策略名称

        Returns:
            Dict[str, int]: 包含 max_attempts 和 window_seconds 的配置字典
        """
        if preset not in self.PRESETS:
            raise ValueError(
                f"未知的频率限制预设策略: {preset}，"
                f"可选值: {', '.join(self.PRESETS.keys())}"
            )
        return self.PRESETS[preset].copy()


# 创建全局频率限制服务实例
rate_limit_service = RateLimitService()
