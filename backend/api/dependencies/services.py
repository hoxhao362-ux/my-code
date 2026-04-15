"""
服务可用性检查依赖 (FastAPI Dependencies)

用于在前端调用 API 时，先保证服务正常的前提下正常工作。
"""
from fastapi import HTTPException
from database.service.database_service import db_manager
from service.redis_service import redis_service
from service.kafka_service import kafka_service
from service.elasticsearch_service import elasticsearch_service
from utils.log import global_logger

async def check_db_service():
    """检查数据库服务是否可用"""
    if not db_manager._initialized:
        global_logger.warning("Dependency", "数据库服务不可用")
        raise HTTPException(status_code=503, detail="数据库服务暂不可用，请稍后再试")
    return db_manager

async def check_redis_service():
    """检查 Redis 服务是否可用"""
    if not redis_service._initialized or not redis_service.client:
        global_logger.warning("Dependency", "Redis 服务不可用")
        raise HTTPException(status_code=503, detail="Redis 服务暂不可用，请稍后再试")
    
    try:
        await redis_service.client.ping()
    except Exception as e:
        global_logger.error("Dependency", f"Redis ping 失败: {e}")
        raise HTTPException(status_code=503, detail="Redis 服务连接异常，请稍后再试")
    return redis_service

async def check_kafka_service():
    """检查 Kafka 服务是否可用"""
    if not kafka_service.is_ready:
        global_logger.warning("Dependency", "Kafka 服务不可用")
        raise HTTPException(status_code=503, detail="消息队列服务暂不可用，请稍后再试")
    return kafka_service

async def check_es_service():
    """检查 Elasticsearch 服务是否可用"""
    if not elasticsearch_service._initialized or not elasticsearch_service.client:
        global_logger.warning("Dependency", "Elasticsearch 服务不可用")
        raise HTTPException(status_code=503, detail="搜索引擎服务暂不可用，请稍后再试")
    return elasticsearch_service
