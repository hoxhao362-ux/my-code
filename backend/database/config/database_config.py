"""
[DEPRECATED] 数据库配置管理模块

本模块已废弃，这是 SQLite 遗留配置。

废弃原因：
1. 项目已迁移至 PostgreSQL
2. 数据库配置已统一通过 database.toml 和 ORM 模块管理
3. 新的数据库服务使用 database/service/database_service.py

如需数据库配置，请参考：
- configs/database.toml - 数据库连接配置
- database/orm/session.py - SQLAlchemy 会话管理
- database/service/database_service.py - 数据库服务管理

废弃日期：2026-03-26
保留原因：向后兼容（部分旧代码可能仍在引用）
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.log import global_logger
from utils.file import load_toml


@dataclass
class DatabaseInfo:
    """数据库信息配置"""
    name: str
    file_name: str
    db_type: str = "postgreSQL"
    description: str = ""
    tables: Optional[List[str]] = None
    auto_create: bool = True
    backup_enabled: bool = True
    db_path: Optional[Path] = None

class DatabaseConfig:
    """数据库配置管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent.parent.parent / "configs"
        self.configs = {}
        self.global_config = {}
        self.database_config = {}
        self._load_configs()
    
    def _load_configs(self):
        """加载配置文件"""
        try:
            # 加载全局配置
            global_config_path = self.config_dir / "global.toml"
            self.global_config = load_toml(global_config_path)
            global_logger.info('database', f"加载全局配置文件: {global_config_path}")
                
            # 加载数据库配置
            database_config_path = self.config_dir / "database.toml"
            self.database_config = load_toml(database_config_path)
            global_logger.info('database', f"加载数据库配置文件: {database_config_path}")
                    
        except Exception as e:
            global_logger.error('database', f"加载数据库配置文件失败: {e}")
            raise RuntimeError(f"加载数据库配置文件失败: {e}")
    
    def get_database_config(self) -> Dict[str, DatabaseInfo]:
        """获取所有数据库配置信息"""
        if not self.configs:
            self.configs = self._parse_database_configs()
        return self.configs
    
    def _parse_database_configs(self) -> Dict[str, DatabaseInfo]:
        """解析数据库配置文件"""
        configs = {}
        
        # 获取数据库目录
        database_dir = Path(self.database_config.get('database', {}).get('database_dir', './database'))
        
        # 从database.toml解析数据库配置
        files_config = self.database_config.get('files', {})
        
        # 用户账户数据库
        configs['user_account'] = DatabaseInfo(
            name='user_account',
            file_name=files_config.get('user_account_db', 'user_account.db'),
            description='用户账户信息数据库',
            tables=['users'],
            auto_create=True,
            backup_enabled=True
        )
        
        # 期刊投稿数据库
        configs['journal_submit'] = DatabaseInfo(
            name='journal_submit',
            file_name=files_config.get('journal_submit_db', 'journal_submit.db'),
            description='期刊投稿信息数据库',
            tables=['journals', 'review_records'],
            auto_create=True,
            backup_enabled=True
        )
        
        # 期刊信息数据库
        configs['journal_info'] = DatabaseInfo(
            name='journal_info',
            file_name=files_config.get('journal_info_db', 'journal_info.db'),
            description='期刊期数、内容信息数据库',
            tables=['journal_info'],
            auto_create=True,
            backup_enabled=True
        )
        
        # 审稿意见数据库
        configs['review_opinion'] = DatabaseInfo(
            name='review_opinion',
            file_name=files_config.get('review_opinion_db', 'review_opinion.db'),
            description='审稿意见数据库',
            tables=['review_opinions'],
            auto_create=True,
            backup_enabled=True
        )
        
        # 管理员操作日志数据库
        configs['admin_log'] = DatabaseInfo(
            name='admin_log',
            file_name=files_config.get('admin_log_db', 'admin_log.db'),
            description='管理员操作日志数据库',
            tables=['admin_logs'],
            auto_create=True,
            backup_enabled=True
        )
        
        # 已删除文献数据库
        configs['deleted_journal'] = DatabaseInfo(
            name='deleted_journal',
            file_name=files_config.get('deleted_journal_db', 'deleted_journal.db'),
            description='已删除文献信息数据库',
            tables=['deleted_journals'],
            auto_create=True,
            backup_enabled=True
        )
        
        # 邀请码数据库
        configs['invitation_code'] = DatabaseInfo(
            name='invitation_code',
            file_name=files_config.get('invitation_code_db', 'invitation_code.db'),
            description='邀请码管理数据库',
            tables=['invitation_codes', 'invitation_code_usage'],
            auto_create=True,
            backup_enabled=True
        )

        # 支付订单数据库
        configs['payment_order'] = DatabaseInfo(
            name='payment_order',
            file_name=files_config.get('payment_order_db', 'payment_order.db'),
            description='支付订单信息数据库',
            tables=['payment_orders'],
            auto_create=True,
            backup_enabled=True
        )
        
        # 为每个数据库添加完整路径
        for db_info in configs.values():
            db_info.db_path = database_dir / db_info.file_name
        
        return configs
    
    def get_database_path(self, database_name: str) -> Path:
        """获取数据库文件路径"""
        configs: dict[str, DatabaseInfo] = self.get_database_config()
        if database_name not in configs:
            raise ValueError(f"未找到数据库配置: {database_name}")
        
        db_path = configs[database_name].db_path
        
        if db_path is None:
            raise ValueError(f"数据库 {database_name} 配置中未指定路径")
        return db_path
    
    def get_database_info(self, database_name: str) -> DatabaseInfo:
        """获取数据库详细信息"""
        configs: dict[str, DatabaseInfo] = self.get_database_config()
        if database_name not in configs:
            raise ValueError(f"未找到数据库配置: {database_name}")
        return configs[database_name]
    
    def get_all_database_names(self) -> List[str]:
        """获取所有数据库名称"""
        return list(self.get_database_config().keys())


# 全局配置实例
db_config = DatabaseConfig()