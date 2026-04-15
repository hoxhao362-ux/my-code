"""
Redis 服务模块

用于处理 Redis 连接和操作。
"""
import asyncio
import os
from typing import Optional
from datetime import timedelta

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

            if password is None or (isinstance(password, float) and password != password) or password in ("", "${REDIS_PWD}"):
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
                    await self.connect(
                        host=host,
                        port=port,
                        password=password,
                        db=db
                    )
                    self._initialized = True
                    global_logger.info("Redis", f"Redis 服务就绪并连接成功: {host}:{port}")
                    return
                except Exception as e:
                    retry_count += 1
                    if retry_count % 5 == 0 or retry_count == 1:
                        global_logger.warning("Redis", f"Redis 连接失败，重试中 ({retry_count}/{max_retries}): {e}")
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

    async def connect(self, host: str, port: int, password: Optional[str] = None, db: int = 0):
        """连接到Redis服务器"""
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        # 测试连接
        await self.client.ping()
    
    async def close(self):
        """关闭Redis连接"""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def set_user_online(self, user_id: int, token: str, expire_time: int = 3600 * 24):
        """设置用户在线状态"""
        if not self.client:
            return False
        
        # 存储用户token，设置过期时间
        await self.client.setex(
            f"user:online:{user_id}",
            timedelta(seconds=expire_time),
            token
        )
        
        # 存储token对应的用户信息
        await self.client.setex(
            f"token:{token}",
            timedelta(seconds=expire_time),
            str(user_id)
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
    
    async def refresh_token_expire(self, user_id: int, token: str, expire_time: int = 3600 * 24):
        """刷新token的过期时间"""
        if not self.client:
            return False
        
        # 更新用户token过期时间
        await self.client.setex(
            f"user:online:{user_id}",
            timedelta(seconds=expire_time),
            token
        )
        
        # 更新token对应的用户信息过期时间
        await self.client.setex(
            f"token:{token}",
            timedelta(seconds=expire_time),
            str(user_id)
        )
        
        return True
    
    async def set_login_limit(self, ip_address: str, max_attempts: int = 5, expire_time: int = 3600):
        """设置登录次数限制"""
        if not self.client:
            return False, 0
        
        key = f"login:limit:{ip_address}"
        attempts = await self.client.get(key)
        
        if attempts:
            attempts = int(attempts) + 1
        else:
            attempts = 1
        
        await self.client.setex(
            key,
            timedelta(seconds=expire_time),
            str(attempts)
        )
        
        return attempts <= max_attempts, attempts
    
    async def get_login_attempts(self, ip_address: str) -> int:
        """获取登录尝试次数"""
        if not self.client:
            return 0
        
        attempts = await self.client.get(f"login:limit:{ip_address}")
        return int(attempts) if attempts else 0

# 创建全局 Redis 服务实例
redis_service = RedisService()
