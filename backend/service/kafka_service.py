"""
Kafka 服务模块

统一管理 Kafka 服务的生命周期与消息生产。
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
        连接 Kafka 服务
        """
        global_logger.info("Kafka", "正在连接 Kafka 服务...")
        
        env = config.get("global.global.env", "dev")
        host_key = f"kafka.kafka.kafka_host_{env}"
        host = config.get(host_key, "localhost")
        port = config.get("kafka.kafka.kafka_port", 9092)
        bootstrap_servers = f"{host}:{port}"
        
        try:
            # 就绪检查与连接初始化
            retry_count = 0
            max_retries = 30  # Kafka 启动可能较慢，给予较多重试机会
            
            while retry_count < max_retries:
                try:
                    # 尝试初始化 Producer 来验证连接
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
                        global_logger.error("Kafka", f"Kafka 服务连接超时: {bootstrap_servers}")
                        raise RuntimeError(f"Kafka 服务连接失败: {e}")
                    
                    # 等待后重试
                    await asyncio.sleep(2)
                except Exception as e:
                    global_logger.error("Kafka", f"Kafka 连接检查发生未知错误: {e}")
                    # 不立即抛出，继续重试
                    retry_count += 1
                    await asyncio.sleep(2)
                    
        except Exception as e:
            global_logger.error("Kafka", f"连接 Kafka 失败: {e}")
            traceback.print_exc()
            raise

    async def stop(self):
        """
        关闭 Kafka 连接
        """
        global_logger.info("Kafka", "正在关闭 Kafka 连接...")
        
        try:
            # 1. 关闭 Producer
            if self.producer:
                self.producer.close()
                self.producer = None
                self._initialized = False
                global_logger.info("Kafka", "Kafka Producer 已关闭")
                    
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
            
            return True
            
        except Exception as e:
            global_logger.error("Kafka", f"发送消息异常: {e}")
            return False

# 创建全局 Kafka 服务实例
kafka_service = KafkaService()
