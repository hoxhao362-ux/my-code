import traceback
import re
import asyncio
from typing import Dict, List, Optional

from utils.log import global_logger

class BaseManagedService:
    """
    第三方服务基类
    每个具体的第三方服务（如 DatabaseManager, RedisService）都应继承此类，
    并实现自己的连接与断开逻辑。
    """
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._initialized = False
        # 自动向全局管理器注册
        service_manager.register(self)

    async def start(self):
        """
        连接服务的定制化逻辑。由子类实现。
        """
        raise NotImplementedError(f"服务 {self.service_name} 未实现 start 方法")

    async def stop(self):
        """
        断开服务的定制化逻辑。由子类实现。
        """
        raise NotImplementedError(f"服务 {self.service_name} 未实现 stop 方法")
    
class ServiceManager:
    """
    第三方服务全局管理器（注册器）
    负责协调所有已注册服务的统一启动和关闭。
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.services: List[BaseManagedService] = []
        self._initialized = True

    def register(self, service: BaseManagedService):
        """
        注册一个被管理的服务单例
        """
        if service not in self.services:
            self.services.append(service)
            global_logger.debug("Service", f"服务单例已注册: {service.service_name}")

    async def start_all(self):
        """
        触发所有已注册服务的定制化启动计划
        """
        if not self.services:
            global_logger.warning("Service", "未检测到任何已注册的第三方服务单例")
            return

        global_logger.info("Service", f"正在并行启动 {len(self.services)} 个第三方服务...")
        
        # 并行执行所有服务的 start 方法
        # 注意：每个服务的 start 方法内部应包含自己的就绪检查逻辑
        tasks = [service.start() for service in self.services]
        await asyncio.gather(*tasks)
        
        global_logger.info("Service", "所有第三方服务启动计划执行完毕")

    async def stop_all(self):
        """
        安全关闭所有已注册的服务
        """
        if not self.services:
            return

        global_logger.info("Service", "正在关闭所有第三方服务...")
        
        # 逆序关闭服务
        for service in reversed(self.services):
            try:
                await service.stop()
            except Exception as e:
                global_logger.error("Service", f"关闭服务 {service.service_name} 时出错: {e}")
            
        global_logger.info("Service", "所有第三方服务已关闭")

# 全局服务管理器单例（注册器）
service_manager = ServiceManager()
