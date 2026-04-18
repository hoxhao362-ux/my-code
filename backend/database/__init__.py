"""
数据库模块 - 标准化数据库架构

提供基于配置驱动的数据库管理，包括：
- 数据库服务 (database.service)
- ORM 模型 (database.orm)
- 仓储层 (database.repositories)
"""

from database.service.database_service import DatabaseManager, db_manager

__all__ = [
    # 服务
    "DatabaseManager",
    "db_manager",
]
