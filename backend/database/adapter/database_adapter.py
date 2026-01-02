"""
数据库适配器 - 提供向后兼容的数据库接口
让现有代码无缝迁移到新的数据库架构
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

# 导入新的数据库服务
from database.service.database_service import DatabaseService, db_manager
from utils.database import Database as LegacyDatabase


class DatabaseAdapter:
    """数据库适配器 - 提供与原有Database类相同的接口"""
    
    def __init__(self, database_name: str = 'journal_submit'):
        self.database_name = database_name
        self.service: Optional[DatabaseService] = None
        self.logger = logging.getLogger(f"database.adapter.{database_name}")
    
    async def initialize(self):
        """初始化数据库服务"""
        if not db_manager._initialized:
            await db_manager.initialize_all()
        self.service = db_manager.get_service(self.database_name)
    
    async def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None):
        """执行SQL语句（兼容原有接口）"""
        if not self.service:
            await self.initialize()
        return await self.service.execute(sql, params)
    
    async def executemany(self, sql: str, params_list: List[Tuple[Any, ...]]):
        """批量执行SQL语句（兼容原有接口）"""
        if not self.service:
            await self.initialize()
        return await self.service.executemany(sql, params_list)
    
    async def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """获取单行结果（兼容原有接口）"""
        if not self.service:
            await self.initialize()
        return await self.service.fetchone(sql, params)
    
    async def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """获取所有结果（兼容原有接口）"""
        if not self.service:
            await self.initialize()
        return await self.service.fetchall(sql, params)
    
    async def fetchval(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """获取单个值（兼容原有接口）"""
        if not self.service:
            await self.initialize()
        return await self.service.fetchval(sql, params)
    
    async def commit(self):
        """提交事务（兼容原有接口，在新架构中已自动提交）"""
        # 新架构中每次操作都自动提交，此方法为空实现
        pass
    
    async def connect(self):
        """连接数据库（兼容原有接口）"""
        await self.initialize()
    
    async def close(self):
        """关闭数据库连接（兼容原有接口）"""
        # 新架构使用上下文管理，无需手动关闭
        pass
    
    # 向后兼容的属性
    @property
    def db_path(self) -> Path:
        """获取数据库路径（兼容原有接口）"""
        if not self.service:
            raise RuntimeError("数据库未初始化")
        return self.service.db_info.db_path
    
    @property
    def conn(self):
        """获取连接对象（兼容原有接口）"""
        # 新架构不使用持久连接，返回None保持兼容
        return None


class DatabaseManagerAdapter:
    """数据库管理器适配器"""
    
    def __init__(self):
        self.logger = logging.getLogger("database.manager.adapter")
        self.adapters: Dict[str, DatabaseAdapter] = {}
    
    def get_database(self, name: str) -> DatabaseAdapter:
        """获取数据库适配器"""
        if name not in self.adapters:
            self.adapters[name] = DatabaseAdapter(name)
        return self.adapters[name]
    
    async def add_database(self, name: str, db_path: Path):
        """添加数据库（兼容原有接口）"""
        # 在新架构中，数据库配置来自配置文件，此方法用于向后兼容
        self.logger.info(f"数据库 {name} 路径设置为: {db_path}")
    
    async def connect_all(self):
        """连接所有数据库"""
        if not db_manager._initialized:
            await db_manager.initialize_all()
        self.logger.info("所有数据库连接完成")
    
    async def create_all_tables(self):
        """创建所有数据库表"""
        if not db_manager._initialized:
            await db_manager.initialize_all()
        self.logger.info("所有数据库表创建完成")
    
    async def close_all(self):
        """关闭所有数据库"""
        self.logger.info("所有数据库连接已关闭")


# 全局数据库管理器适配器实例
db_manager_adapter = DatabaseManagerAdapter()

# 创建兼容的数据库实例
# 主要数据库（期刊投稿）
main_db = DatabaseAdapter('journal_submit')

# 用户账户数据库
user_db = DatabaseAdapter('user_account')

# 管理员日志数据库
admin_log_db = DatabaseAdapter('admin_log')

# 已删除文献数据库
deleted_journal_db = DatabaseAdapter('deleted_journal')

# 其他数据库
journal_info_db = DatabaseAdapter('journal_info')
review_opinion_db = DatabaseAdapter('review_opinion')


# 为了向后兼容，创建全局变量
# 这些将替换原有的db, db_manager等实例
db = main_db  # 主要的数据库实例
legacy_db_manager = db_manager_adapter  # 兼容的数据库管理器


async def get_db():
    """获取数据库实例（兼容性函数）"""
    return db


async def get_db_manager():
    """获取数据库管理器（兼容性函数）"""
    return legacy_db_manager