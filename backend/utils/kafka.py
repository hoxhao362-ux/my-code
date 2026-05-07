"""
Kafka 服务工具类 - 统一管理 Kafka 服务的生命周期与消息生产

本模块提供了基于 kafka-python 的 Kafka 服务管理，主要功能包括：
1. 管理 Kafka 服务进程的启动与停止（通过外部脚本）。
2. 提供全局单例的 Kafka 生产者实例。
3. 封装消息发送接口，支持 JSON 序列化。
4. 深度集成项目全局日志与配置系统。

主要类：
- KafkaService: 继承自 BaseManagedService，负责 Kafka 服务的全生命周期管理。
"""
import asyncio
import json
import traceback
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable

from core.config import config
from core.service_manager import BaseManagedService
from utils.log import global_logger


class KafkaService(BaseManagedService):
    """
    Kafka 服务管理类
    
    继承自 BaseManagedService，实现定制化的 Kafka 启动和停止逻辑，
    并作为全局单例提供消息生产能力。
    """
    
    def __init__(self):
        # 初始化父类，注册服务名为 'kafka'
        super().__init__("kafka")
        self.producer: Optional[KafkaProducer] = None
        self._initialized = False

    async def start(self):
        """
        定制化启动计划：
        1. 从配置读取启动脚本路径。
        2. 启动 Kafka 服务进程
        3. 循环尝试连接 Kafka Broker，直到成功或超时。
        """
        global_logger.info("Kafka", "执行 Kafka 定制化启动计划...")
        
        # 1. 获取配置
        exe_path = config["global.global.kafka_service_path"]
        # 注意：这里假设 args 是列表，如果为空则为空列表
        args_config = config.get("global.global.kafka_service_args", [])
        args = await self._check_args(args_config)
        
        host = config["global.global.kafka_host"]
        port = config["global.global.kafka_port"]
        bootstrap_servers = f"{host}:{port}"
        
        # 2. 启动进程
        # 构建启动命令
        cmd_parts = [f'"{exe_path}"']
        for k, v in args.items():
            cmd_parts.append(f'{k} "{v}"')
            
        start_cmd = " ".join(cmd_parts)
        global_logger.info("Kafka", f"正在启动 Kafka 服务: {start_cmd}")
        
        try:
            # 创建进程
            # 注意：如果启动脚本是阻塞式的（如直接运行 kafka-server-start.bat），
            # create_subprocess_shell 会返回一个正在运行的进程对象。
            # 如果脚本是启动后退出的（如使用 start 命令），进程对象会很快结束。
            # 这里的逻辑兼容两种情况，关键在于后续的连接检查。
            await self._create_process(start_cmd)
            
            # 3. 就绪检查与连接初始化
            retry_count = 0
            max_retries = 30  # Kafka 启动可能较慢，给予较多重试机会
            
            while retry_count < max_retries:
                try:
                    # 尝试初始化 Producer 来验证连接
                    # kafka-python 的 Producer 初始化会尝试连接 bootstrap_servers
                    self.producer = KafkaProducer(
                        bootstrap_servers=bootstrap_servers,
                        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                        # 设置较短的连接超时，以便快速重试
                        request_timeout_ms=2000,
                        api_version_auto_timeout_ms=2000
                    )
                    
                    # 尝试获取一下集群元数据以确保真正连接成功
                    self.producer.bootstrap_connected()
                    
                    self._initialized = True
                    global_logger.info("Kafka", f"Kafka 服务就绪并连接成功: {bootstrap_servers}")
                    return
                    
                except (NoBrokersAvailable, KafkaError) as e:
                    retry_count += 1
                    if retry_count % 5 == 0:
                        global_logger.warning("Kafka", f"等待 Kafka 就绪 ({retry_count}/{max_retries})...")
                    
                    if retry_count >= max_retries:
                        global_logger.error("Kafka", f"Kafka 服务启动超时，无法连接到: {bootstrap_servers}")
                        raise RuntimeError(f"Kafka 服务启动失败: {e}")
                    
                    # 等待后重试
                    await asyncio.sleep(2)
                except Exception as e:
                    global_logger.error("Kafka", f"Kafka 连接检查发生未知错误: {e}")
                    # 不立即抛出，继续重试
                    retry_count += 1
                    await asyncio.sleep(2)
                    
        except Exception as e:
            global_logger.error("Kafka", f"定制启动计划执行失败: {e}")
            traceback.print_exc()
            raise

    async def stop(self):
        """
        定制化关闭计划：
        1. 关闭 Producer 连接。
        2. 执行停止脚本安全关闭 Kafka 服务。
        """
        global_logger.info("Kafka", "正在执行 Kafka 安全关闭计划...")
        
        try:
            # 1. 关闭 Producer
            if self.producer:
                self.producer.close()
                self.producer = None
                self._initialized = False
                global_logger.info("Kafka", "Kafka Producer 已关闭")
            
            # 2. 执行停止脚本
            stop_path = config.get("global.global.kafka_stop_path")
            if stop_path:
                global_logger.info("Kafka", f"执行停止脚本: {stop_path}")
                stop_process = await asyncio.create_subprocess_shell(
                    f'"{stop_path}"',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                # 等待停止脚本执行完成
                stdout, stderr = await stop_process.communicate()
                
                if stop_process.returncode != 0:
                    err_msg = stderr.decode('gbk', errors='ignore')
                    global_logger.warning("Kafka", f"Kafka 停止脚本返回非零状态: {err_msg}")
                else:
                    global_logger.info("Kafka", "Kafka 服务停止指令已发送")
            else:
                # 如果没有配置停止脚本，且之前启动的进程还在运行，尝试终止它
                if self.process and self.process.returncode is None:
                    global_logger.warning("Kafka", "未配置停止脚本，尝试直接终止 Kafka 进程...")
                    self.process.terminate()
                    await self.process.wait()
                    global_logger.info("Kafka", "Kafka 进程已终止")
                    
        except Exception as e:
            global_logger.error("Kafka", f"关闭 Kafka 失败: {e}")
            traceback.print_exc()

    async def send_message(self, topic: str, data: Dict[str, Any]) -> bool:
        """
        发送消息到指定主题
        
        Args:
            topic: 消息主题
            data: 消息内容（字典格式，会自动序列化为 JSON）
            
        Returns:
            bool: 发送是否成功（注意：kafka-python send 是异步的，这里只代表请求已入队）
        """
        if not self._initialized or not self.producer:
            global_logger.error("Kafka", "尝试发送消息但 Kafka 服务未就绪")
            return False
            
        try:
            # send 方法是异步的，返回一个 Future
            future = self.producer.send(topic, value=data)
            
            # 定义回调函数处理结果
            def on_send_success(record_metadata):
                global_logger.debug("Kafka", f"消息发送成功: topic={record_metadata.topic} partition={record_metadata.partition} offset={record_metadata.offset}")
                
            def on_send_error(ex):
                global_logger.error("Kafka", f"消息发送失败: {ex}")
                
            # 添加回调
            future.add_callback(on_send_success)
            future.add_errback(on_send_error)
            
            # 只要成功调用 send 并入队，就视为暂时的“成功”
            # 实际发送结果由回调处理
            return True
            
        except Exception as e:
            global_logger.error("Kafka", f"发送消息异常: {e}")
            return False

# 创建全局 Kafka 服务实例
# 实例化时会自动调用 service_manager.register(self)
kafka_service = KafkaService()
