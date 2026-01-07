import redis.asyncio as redis
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

class RedisClient:
    """Redis客户端类，用于处理Redis连接和操作"""
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self, host: str = "localhost:6379", password: Optional[str] = None, db: int = 0):
        """连接到Redis服务器"""
        host, port = host.split(":") if ":" in host else (host, "6379")
        self.client = redis.Redis(
            host=host,
            port=int(port),
            password=password,
            db=db,
            decode_responses=True
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

# 创建全局Redis客户端实例
redis_client = RedisClient()
