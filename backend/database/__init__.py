"""
数据库模块 - 标准化数据库架构

提供基于配置驱动的数据库管理，包括：
- 配置管理 (database.config)
- 数据库服务 (database.service)
- 适配器层 (database.adapter)
"""
from database.config.database_config import DatabaseConfig, DatabaseInfo, db_config
from database.service.database_service import DatabaseService, DatabaseManager, db_manager
from database.adapter.database_adapter import (
    DatabaseAdapter, 
    DatabaseManagerAdapter, 
    main_db, 
    user_db, 
    admin_log_db, 
    deleted_journal_db,
    journal_info_db,
    review_opinion_db
)

__all__ = [
    # 配置
    'DatabaseConfig',
    'DatabaseInfo', 
    'db_config',
    
    # 服务
    'DatabaseService',
    'DatabaseManager',
    'db_manager',
    
    # 适配器
    'DatabaseAdapter',
    'DatabaseManagerAdapter',
    'main_db',
    'user_db', 
    'admin_log_db',
    'deleted_journal_db',
    'journal_info_db',
    'review_opinion_db'
]