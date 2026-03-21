import traceback
import re
import asyncio
from typing import Dict, List, Optional

from utils.log import global_logger

class BaseManagedService:
    """
    第三方服务基类
    每个具体的第三方服务（如 DatabaseManager, RedisClient）都应继承此类，
    并实现自己的定制化启动计划。
    """
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.process: Optional[asyncio.subprocess.Process] = None
        # 自动向全局管理器注册
        service_manager.register(self)

    async def start(self):
        """
        启动服务的定制化计划。由子类实现。
        """
        raise NotImplementedError(f"服务 {self.service_name} 未实现 start 方法")

    async def stop(self):
        """
        停止服务的定制化计划。由子类实现。
        """
        raise NotImplementedError(f"服务 {self.service_name} 未实现 stop 方法")

    async def _create_process(self, cmd: str, shell: bool = True, log_output: bool = False) -> asyncio.subprocess.Process:
        """
        创建异步子进程的辅助方法
        :param cmd: 启动命令
        :param shell: 是否使用 shell
        :param log_output: 是否在后台自动读取并记录日志（避免长期运行进程的缓冲区阻塞）
        """
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.process = process
            
            if log_output:
                # 启动后台任务读取输出，防止输出缓冲区满导致进程阻塞
                asyncio.create_task(self._read_stream(process.stdout, "STDOUT"))
                asyncio.create_task(self._read_stream(process.stderr, "STDERR"))
                
            return process
        except Exception as e:
            traceback.print_exc()
            global_logger.error("Service", f"创建服务 {self.service_name} 进程失败: {e}")
            raise

    async def _read_stream(self, stream: asyncio.StreamReader, stream_type: str):
        """
        异步读取子进程流并输出到日志
        """
        if not stream:
            return
        while True:
            try:
                line = await stream.readline()
                if not line:
                    break
                
                # 尝试多种编码解码
                try:
                    text = line.decode('utf-8', errors='ignore').strip()
                except Exception:
                    text = line.decode('gbk', errors='ignore').strip()
                    
                if text:
                    if stream_type == "STDERR":
                        global_logger.warning(self.service_name, text)
                    else:
                        global_logger.debug(self.service_name, text)
            except Exception as e:
                global_logger.error(self.service_name, f"读取进程日志异常 ({stream_type}): {e}")
                break
    
    async def _check_args(self, args: List[str]) -> dict[str, str]:
        """
        检查服务启动参数是否为空
        """
        if len(args) % 2 != 0:
            raise ValueError(f"服务 {self.service_name} 启动参数必须是键值对")
        return dict(zip(args[::2], args[1::2]))
    
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
