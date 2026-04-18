"""
Redis 服务模块

用于处理 Redis 连接和操作。
"""

import asyncio
import os
from datetime import timedelta
from typing import Optional, Tuple

import redis.asyncio as redis
from core.config import config
from core.service_manager import BaseManagedService
from utils.log import global_logger


class RedisService(BaseManagedService):
    """
    Redis 服务管理类

    继承自 BaseManagedService，实现定制化的 Redis 启动和就绪检查计划。
    """

    def __init__(self):
        # 初始化父类，注册服务名为 'redis'
        super().__init__("redis")
        self.client: Optional[redis.Redis] = None

    async def start(self):
        """
        连接 Redis 服务
        """
        global_logger.info("Redis", "正在连接 Redis 服务...")

        try:
            env = config.get("global.global.env", "dev")
            host_key = f"redis.redis.redis_host_{env}"
            host = config.get(host_key, "localhost")
            port = int(config.get("redis.redis.redis_port", 6379))
            password = config.get("redis.redis.redis_password")
            db = int(config.get("redis.redis.redis_db", 0))

            if (
                password is None
                or (isinstance(password, float) and password != password)
                or password in ("", "${REDIS_PWD}")
            ):
                password = os.environ.get("REDIS_PWD") or None
            if not password:
                global_logger.warning(
                    "Redis",
                    "Redis 密码为空：容器若使用 --requirepass，请在 .env 中设置 REDIS_PWD 或与 TOML 中 redis_password 一致",
                )

            retry_count = 0
            max_retries = 30
            while retry_count < max_retries:
                try:
                    await self.connect(host=host, port=port, password=password, db=db)
                    self._initialized = True
                    global_logger.info(
                        "Redis", f"Redis 服务就绪并连接成功: {host}:{port}"
                    )
                    return
                except Exception as e:
                    retry_count += 1
                    if retry_count % 5 == 0 or retry_count == 1:
                        global_logger.warning(
                            "Redis",
                            f"Redis 连接失败，重试中 ({retry_count}/{max_retries}): {e}",
                        )
                    if retry_count >= max_retries:
                        raise
                    await asyncio.sleep(1)

        except Exception as e:
            global_logger.error("Redis", f"Redis 连接失败: {e}")
            raise

    async def stop(self):
        """
        关闭 Redis 连接
        """
        global_logger.info("Redis", "正在关闭 Redis 连接...")
        try:
            await self.close()
            self._initialized = False
        except Exception as e:
            global_logger.error("Redis", f"关闭 Redis 失败: {e}")

    async def connect(
        self, host: str, port: int, password: Optional[str] = None, db: int = 0
    ):
        """连接到Redis服务器"""
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        # 测试连接
        await self.client.ping()

    async def close(self):
        """关闭Redis连接"""
        if self.client:
            await self.client.close()
            self.client = None

    async def set_user_online(
        self, user_id: int, token: str, expire_time: int = 3600 * 24
    ):
        """设置用户在线状态"""
        if not self.client:
            return False

        # 存储用户token，设置过期时间
        await self.client.setex(
            f"user:online:{user_id}", timedelta(seconds=expire_time), token
        )

        # 存储token对应的用户信息
        await self.client.setex(
            f"token:{token}", timedelta(seconds=expire_time), str(user_id)
        )

        return True

    async def set_user_offline(self, user_id: int, token: str):
        """设置用户离线状态"""
        if not self.client:
            return False

        # 删除用户在线状态和token信息
        await self.client.delete(f"user:online:{user_id}")
        await self.client.delete(f"token:{token}")

        return True

    async def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        if not self.client:
            return False

        return await self.client.exists(f"user:online:{user_id}") > 0

    async def get_user_by_token(self, token: str) -> Optional[int]:
        """根据token获取用户ID"""
        if not self.client:
            return None

        user_id = await self.client.get(f"token:{token}")
        return int(user_id) if user_id else None

    async def get_token_by_user(self, user_id: int) -> Optional[str]:
        """根据用户ID获取token"""
        if not self.client:
            return None

        return await self.client.get(f"user:online:{user_id}")

    async def refresh_token_expire(
        self, user_id: int, token: str, expire_time: int = 3600 * 24
    ):
        """刷新token的过期时间"""
        if not self.client:
            return False

        # 更新用户token过期时间
        await self.client.setex(
            f"user:online:{user_id}", timedelta(seconds=expire_time), token
        )

        # 更新token对应的用户信息过期时间
        await self.client.setex(
            f"token:{token}", timedelta(seconds=expire_time), str(user_id)
        )

        return True

    async def increment_rate_limit(
        self,
        key_prefix: str,
        identifier: str,
        max_attempts: int = 5,
        window_seconds: int = 3600,
    ) -> Tuple[bool, int]:
        """
        通用的频率限制方法，使用 Redis INCR + EXPIRE 原子操作。

        使用 Lua 脚本确保 INCR 和 EXPIRE 操作的原子性，避免高并发下的竞态条件。

        Args:
            key_prefix: 限制类型前缀（如 "login", "register"）
            identifier: 限制对象标识（如 IP 地址）
            max_attempts: 时间窗口内最大尝试次数
            window_seconds: 时间窗口（秒）

        Returns:
            Tuple[bool, int]: (是否允许本次操作, 当前累计尝试次数)
        """
        if not self.client:
            return False, 0

        redis_key = f"rate_limit:{key_prefix}:{identifier}"

        # 使用 Lua 脚本确保 INCR + EXPIRE 的原子性
        lua_script = """
        local current = redis.call('INCR', KEYS[1])
        if current == 1 then
            redis.call('EXPIRE', KEYS[1], ARGV[1])
        end
        return current
        """
        current_count = await self.client.eval(lua_script, 1, redis_key, window_seconds)

        allowed = current_count <= max_attempts
        return allowed, current_count

    async def set_login_limit(
        self, ip_address: str, max_attempts: int = 5, expire_time: int = 3600
    ) -> Tuple[bool, int]:
        """
        [DEPRECATED] 设置登录次数限制

        请使用 increment_rate_limit 方法代替，该方法使用 Redis 原子操作避免竞态条件。

        Args:
            ip_address: IP 地址
            max_attempts: 最大尝试次数
            expire_time: 过期时间（秒）

        Returns:
            Tuple[bool, int]: (是否允许, 当前尝试次数)
        """
        global_logger.warning(
            "Redis", "set_login_limit 已废弃，请使用 increment_rate_limit"
        )
        return await self.increment_rate_limit(
            "login", ip_address, max_attempts, expire_time
        )

    async def get_login_attempts(self, ip_address: str) -> int:
        """获取登录尝试次数"""
        if not self.client:
            return 0

        attempts = await self.client.get(f"rate_limit:login:{ip_address}")
        return int(attempts) if attempts else 0

    # ============ JWT 密钥轮换 ============

    async def init_jwt_keys(self, default_key: str) -> None:
        """
        初始化 JWT 密钥：启动时若 Redis 中无密钥，则用配置中的 secret_key 初始化。
        Args:
            default_key: 配置文件中的默认密钥
        """
        # 检查 Redis 中是否已有当前密钥
        current = await self.client.get("jwt:key:current")
        if not current:
            await self.client.set("jwt:key:current", default_key)
            global_logger.info("RedisService", "JWT 密钥已从配置初始化到 Redis")

    async def get_current_jwt_key(self) -> str:
        """获取当前有效的 JWT 签发密钥"""
        key = await self.client.get("jwt:key:current")
        if not key:
            # 兜底：从配置自动回填，避免服务完全不可用
            from core.config import config

            default_key = config["global.global.secret_key"]
            await self.client.set("jwt:key:current", default_key)
            global_logger.warning(
                "RedisService", "Redis 中缺少 JWT 密钥，已从配置自动回填"
            )
            return default_key
        return key

    async def get_previous_jwt_key(self) -> Optional[str]:
        """获取上一代 JWT 密钥（用于验证旧 token 的过渡期）"""
        return await self.client.get("jwt:key:previous")

    async def rotate_jwt_key(self) -> str:
        """
        执行 JWT 密钥轮换：当前密钥 → previous，生成新随机密钥 → current。
        Returns:
            新生成的当前密钥
        """
        import secrets

        current_key = await self.client.get("jwt:key:current")
        new_key = secrets.token_urlsafe(48)  # 生成 64 字符随机密钥

        # 使用 pipeline 确保原子性
        pipe = self.client.pipeline()
        if current_key:
            # 旧密钥保留 24 小时，覆盖 token 最大有效期
            pipe.set("jwt:key:previous", current_key, ex=86400)
        pipe.set("jwt:key:current", new_key)
        await pipe.execute()

        global_logger.info("RedisService", "JWT 密钥轮换完成")
        return new_key


# 创建全局 Redis 服务实例
redis_service = RedisService()
