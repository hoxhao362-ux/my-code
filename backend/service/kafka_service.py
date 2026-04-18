"""
Kafka 服务模块

统一管理 Kafka 服务的生命周期与消息生产/消费。
基于 aiokafka 实现完全异步的 Producer 和 Consumer。
"""

import asyncio
import json
import traceback
from typing import Any, Callable, Dict, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError
from core.config import config
from core.service_manager import BaseManagedService
from utils.log import global_logger


class KafkaService(BaseManagedService):
    """
    Kafka 服务管理类

    继承自 BaseManagedService，实现定制化的 Kafka 启动和停止逻辑，
    并作为全局单例提供消息生产和消费能力。

    特性：
    - 完全异步的 Producer 和 Consumer
    - 支持多 topic 消息处理器注册
    - 自动管理消费循环任务
    - 消息重试机制与死信队列支持
    """

    # 重试配置
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1  # 秒

    def __init__(self):
        # 初始化父类，注册服务名为 'kafka'
        super().__init__("kafka")

        # Producer 相关
        self._producer: Optional[AIOKafkaProducer] = None

        # Consumer 相关
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._handlers: Dict[str, Callable] = {}  # topic -> handler 映射
        self._consume_task: Optional[asyncio.Task] = None

        # 配置
        self._bootstrap_servers: str = ""

        # 消费统计
        self._consume_stats: Dict[str, Dict[str, int]] = {}

    async def start(self):
        """
        连接 Kafka 服务（实现 BaseManagedService 接口）

        1. 初始化 AIOKafkaProducer
        2. 如果有注册的消息处理器，初始化 AIOKafkaConsumer 并启动消费循环
        """
        global_logger.info("Kafka", "正在连接 Kafka 服务...")

        env = config.get("global.global.env", "dev")
        host_key = f"kafka.kafka.kafka_host_{env}"
        host = config.get(host_key, "localhost")
        port = config.get("kafka.kafka.kafka_port", 9092)
        self._bootstrap_servers = f"{host}:{port}"

        try:
            # 就绪检查与连接初始化
            retry_count = 0
            max_retries = 30  # Kafka 启动可能较慢，给予较多重试机会

            while retry_count < max_retries:
                try:
                    # 初始化 AIOKafkaProducer
                    self._producer = AIOKafkaProducer(
                        bootstrap_servers=self._bootstrap_servers,
                        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                        request_timeout_ms=5000,
                        retry_backoff_ms=100,
                    )

                    # 启动 Producer
                    await self._producer.start()

                    self._initialized = True
                    global_logger.info(
                        "Kafka",
                        f"Kafka Producer 就绪并连接成功: {self._bootstrap_servers}",
                    )

                    # 如果有注册的 handler，启动 Consumer
                    if self._handlers:
                        await self._start_consumer()

                    return

                except (KafkaConnectionError, KafkaError) as e:
                    retry_count += 1
                    if retry_count % 5 == 0:
                        global_logger.warning(
                            "Kafka", f"等待 Kafka 就绪 ({retry_count}/{max_retries})..."
                        )

                    if retry_count >= max_retries:
                        global_logger.error(
                            "Kafka", f"Kafka 服务连接超时: {self._bootstrap_servers}"
                        )
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

    async def _start_consumer(self):
        """
        启动消费者和消费循环
        """
        if not self._handlers:
            return

        topics = list(self._handlers.keys())
        global_logger.info("Kafka", f"正在启动 Consumer，订阅主题: {topics}")

        try:
            self._consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self._bootstrap_servers,
                group_id=config.get(
                    "kafka.kafka.consumer_group_id", "journal-platform-group"
                ),
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=False,  # 关闭自动提交，改为手动提交
            )

            await self._consumer.start()

            # 用 asyncio.create_task 启动消费循环
            self._consume_task = asyncio.create_task(self._consume_loop())

            global_logger.info("Kafka", "Kafka Consumer 启动成功，消费循环已开始")

        except Exception as e:
            global_logger.error("Kafka", f"启动 Consumer 失败: {e}")

    async def _consume_loop(self):
        """
        消费循环 - 从 Kafka 拉取消息并分发给对应的 handler
        支持重试机制和死信队列
        """
        global_logger.info("Kafka", "消费循环开始运行...")

        try:
            async for msg in self._consumer:
                topic = msg.topic
                value = msg.value

                global_logger.debug(
                    "Kafka",
                    f"收到消息: topic={topic}, partition={msg.partition}, offset={msg.offset}",
                )

                # 初始化该 topic 的统计信息
                if topic not in self._consume_stats:
                    self._consume_stats[topic] = {"success": 0, "failed": 0, "dlq": 0}

                # 查找对应的 handler
                handler = self._handlers.get(topic)
                if not handler:
                    global_logger.warning("Kafka", f"未注册的 topic handler: {topic}")
                    await self._consumer.commit()
                    continue

                # 重试机制处理消息
                success = await self._process_message_with_retry(topic, value, handler)

                if success:
                    self._consume_stats[topic]["success"] += 1
                else:
                    self._consume_stats[topic]["failed"] += 1

                # 手动提交偏移量
                await self._consumer.commit()

        except asyncio.CancelledError:
            global_logger.info("Kafka", "消费循环被取消")
        except Exception as e:
            global_logger.error("Kafka", f"消费循环异常: {e}")

    async def _process_message_with_retry(
        self, topic: str, value: Any, handler: Callable
    ) -> bool:
        """
        处理消息，支持重试机制

        Args:
            topic: 消息主题
            value: 消息内容
            handler: 消息处理器

        Returns:
            bool: 处理是否成功
        """
        success = False
        last_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                # 支持同步和异步 handler
                if asyncio.iscoroutinefunction(handler):
                    await handler(value)
                else:
                    handler(value)
                success = True
                break
            except Exception as e:
                last_error = e
                delay = self.BASE_RETRY_DELAY * (2 ** (attempt - 1))
                global_logger.warning(
                    "Kafka", f"消息处理失败 (topic={topic}, 第{attempt}次重试): {e}"
                )
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(delay)

        if not success:
            # 重试耗尽，发送到死信队列
            await self._send_to_dlq(topic, value, last_error)

        return success

    async def _send_to_dlq(self, topic: str, value: Any, error: Exception):
        """
        将消息发送到死信队列

        Args:
            topic: 原始消息主题
            value: 消息内容
            error: 导致失败的异常
        """
        dlq_topic = f"{topic}.dlq"

        # 构造死信消息，包含原始消息和错误信息
        dlq_message = {
            "original_topic": topic,
            "original_message": value,
            "error": str(error),
            "error_type": type(error).__name__,
            "retry_count": self.MAX_RETRIES,
        }

        try:
            await self.send_message(dlq_topic, dlq_message)
            self._consume_stats[topic]["dlq"] += 1
            global_logger.error("Kafka", f"消息重试耗尽，已发送到死信队列: {dlq_topic}")
        except Exception as e:
            global_logger.error("Kafka", f"发送到死信队列失败: {e}")

    def get_consume_stats(self) -> Dict[str, Dict[str, int]]:
        """
        获取消费统计信息

        Returns:
            Dict: 各 topic 的消费统计
        """
        return self._consume_stats.copy()

    async def stop(self):
        """
        关闭 Kafka 连接（实现 BaseManagedService 接口）
        """
        global_logger.info("Kafka", "正在关闭 Kafka 连接...")

        try:
            # 1. 取消消费任务
            if self._consume_task and not self._consume_task.done():
                self._consume_task.cancel()
                try:
                    await self._consume_task
                except asyncio.CancelledError:
                    pass
                self._consume_task = None
                global_logger.info("Kafka", "消费循环已停止")

            # 2. 关闭 Consumer
            if self._consumer:
                await self._consumer.stop()
                self._consumer = None
                global_logger.info("Kafka", "Kafka Consumer 已关闭")

            # 3. 关闭 Producer
            if self._producer:
                await self._producer.stop()
                self._producer = None
                self._initialized = False
                global_logger.info("Kafka", "Kafka Producer 已关闭")

        except Exception as e:
            global_logger.error("Kafka", f"关闭 Kafka 失败: {e}")
            traceback.print_exc()

    def register_handler(self, topic: str, handler: Callable):
        """
        注册消息处理器

        注意：应在 start() 调用之前注册 handler，否则需要手动重启 consumer

        Args:
            topic: 消息主题
            handler: 处理函数，接收消息内容（dict）作为参数
                     可以是同步函数或异步函数
        """
        self._handlers[topic] = handler
        global_logger.info("Kafka", f"已注册消息处理器: topic={topic}")

    def unregister_handler(self, topic: str):
        """
        注销消息处理器

        Args:
            topic: 消息主题
        """
        if topic in self._handlers:
            del self._handlers[topic]
            global_logger.info("Kafka", f"已注销消息处理器: topic={topic}")

    async def send_message(self, topic: str, data: Dict[str, Any]) -> bool:
        """
        发送消息到指定主题（异步）

        Args:
            topic: 消息主题
            data: 消息内容（字典格式，会自动序列化为 JSON）

        Returns:
            bool: 发送是否成功
        """
        if not self._initialized or not self._producer:
            global_logger.error("Kafka", "尝试发送消息但 Kafka 服务未就绪")
            return False

        try:
            # 异步发送消息并等待确认
            record_metadata = await self._producer.send_and_wait(topic, value=data)

            global_logger.debug(
                "Kafka",
                f"消息发送成功: topic={record_metadata.topic} "
                f"partition={record_metadata.partition} offset={record_metadata.offset}",
            )

            return True

        except Exception as e:
            global_logger.error("Kafka", f"发送消息异常: {e}")
            return False

    async def send_message_nowait(self, topic: str, data: Dict[str, Any]) -> bool:
        """
        发送消息到指定主题（不等待确认，更高吞吐量）

        Args:
            topic: 消息主题
            data: 消息内容（字典格式，会自动序列化为 JSON）

        Returns:
            bool: 消息是否已入队
        """
        if not self._initialized or not self._producer:
            global_logger.error("Kafka", "尝试发送消息但 Kafka 服务未就绪")
            return False

        try:
            # 发送但不等待确认
            await self._producer.send(topic, value=data)
            return True

        except Exception as e:
            global_logger.error("Kafka", f"发送消息异常: {e}")
            return False

    @property
    def is_ready(self) -> bool:
        """检查服务是否就绪"""
        return self._initialized and self._producer is not None


# 创建全局 Kafka 服务实例
kafka_service = KafkaService()
