import asyncio
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

import redis.asyncio as redis

from core.config import config
from core.service_manager import BaseManagedService
from utils.log import global_logger

class RedisClient(BaseManagedService):
    """Redis 客户端类，用于处理 Redis 连接和操作。
    
    继承自 BaseManagedService，实现定制化的 Redis 启动和就绪检查计划。
    """
    def __init__(self):
        # 初始化父类，注册服务名为 'redis'
        super().__init__("redis")
        self.client: Optional[redis.Redis] = None
    
    async def start(self):
        """
        定制化启动计划：
        1. 从配置读取 redis-server 路径和参数
        2. 启动 Redis 进程
        3. 尝试连接并进行 PING 检查
        """
        global_logger.info("Redis", "执行 Redis 定制化启动计划...")
        
        # 1. 获取配置
        exe_path = config["global.global.redis_service_path"]
        args = await self._check_args(config["global.global.redis_service_args"])
        
        # 2. 启动进程
        cmd_parts = [f'"{exe_path}"']
        for k, v in args.items():
            cmd_parts.append(f'{k} "{v}"')
            
        start_cmd = " ".join(cmd_parts)
        global_logger.info("Redis", f"正在启动 Redis: {start_cmd}")
        
        try:
            # 创建进程
            await self._create_process(start_cmd)
            
            # 3. 就绪检查与连接
            host = config["global.global.redis_host"]
            port = config["global.global.redis_port"]
            password = config.get("global.global.redis_password")
            db = config.get("global.global.redis_db", 0)
            
            # 处理 TOML 中的 nan 值
            if password is None or (isinstance(password, float) and password != password):
                password = None

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
                    global_logger.info("Redis", "Redis 服务就绪并连接成功")
                    return
                except Exception:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    await asyncio.sleep(1)
                    
        except Exception as e:
            global_logger.error("Redis", f"定制启动计划执行失败: {e}")
            raise

    async def stop(self):
        """
        定制化关闭计划：
        终止进程并关闭客户端连接
        """
        global_logger.info("Redis", "正在执行 Redis 安全关闭计划...")
        try:
            # 关闭连接
            await self.close()
            
            # 终止进程
            if self.process and self.process.returncode is None:
                self.process.terminate()
                await self.process.wait()
                global_logger.info("Redis", "Redis 进程已终止")
        except Exception as e:
            global_logger.error("Redis", f"关闭 Redis 失败: {e}")

    async def connect(self, host: str, port: int, password: Optional[str] = None, db: int = 0):
        """连接到Redis服务器"""
        self.client = redis.Redis(
            host=host,
            port=port,
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
