"""
数据库模块 - 标准化数据库架构

提供基于配置驱动的数据库管理，包括：
- 配置管理 (database.config) - [DEPRECATED] SQLite 遗留配置
- 数据库服务 (database.service)
- ORM 模型 (database.orm)
- 仓储层 (database.repositories)

注意：database.config.database_config 已废弃，请使用 ORM 模块。
"""
# [DEPRECATED] 以下导入保留用于向后兼容，新代码不应使用
from database.config.database_config import DatabaseConfig, DatabaseInfo, db_config
from database.service.database_service import DatabaseManager, db_manager

__all__ = [
    # [DEPRECATED] 配置 - SQLite 遗留，建议不再使用
    'DatabaseConfig',
    'DatabaseInfo', 
    'db_config',
    
    # 服务
    'DatabaseManager',
    'db_manager'
]
