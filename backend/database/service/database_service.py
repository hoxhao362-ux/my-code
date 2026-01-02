"""
数据库服务层 - 统一管理所有数据库操作
基于配置驱动的数据库管理器，支持事务、连接池、自动创建等功能
"""
import sqlite3
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import asynccontextmanager

from utils.log import global_logger
from database.config.database_config import DatabaseConfig, DatabaseInfo, db_config


class DatabaseConnection:
    """数据库连接包装器，提供上下文管理和自动清理"""
    
    def __init__(self, db_path: Path, timeout: float = 30.0):
        self.db_path = db_path
        self.timeout = timeout
        self._connection: Optional[sqlite3.Connection] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def connect(self):
        """建立数据库连接"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._connect_sync)
    
    def _connect_sync(self):
        """同步连接方法"""
        self._connection = sqlite3.connect(
            str(self.db_path),
            timeout=self.timeout,
            check_same_thread=False
        )
        self._connection.row_factory = sqlite3.Row
    
    async def close(self):
        """关闭数据库连接"""
        if self._connection:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._close_sync)
    
    def _close_sync(self):
        """同步关闭方法"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @property
    def connection(self) -> sqlite3.Connection:
        """获取连接对象"""
        if not self._connection:
            raise RuntimeError("数据库连接未建立")
        return self._connection


class DatabaseService:
    """数据库服务类 - 统一的数据库操作接口"""
    
    def __init__(self, database_name: str):
        self.database_name = database_name
        self.db_info = db_config.get_database_info(database_name)
        self.logger = global_logger
        self._initialized = False
    
    async def initialize(self):
        """初始化数据库"""
        if self._initialized:
            return
        
        try:
            # 确保数据库目录存在
            self.db_info.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建数据库连接并初始化表
            async with DatabaseConnection(self.db_info.db_path) as conn:
                await self._create_tables(conn.connection)
            
            self._initialized = True
            global_logger.info('database', f"数据库 {self.database_name} 初始化完成")
            
        except Exception as e:
            global_logger.error('database', f"数据库 {self.database_name} 初始化失败: {e}")
            raise RuntimeError(f"数据库 {self.database_name} 初始化失败: {e}")
    
    async def _create_tables(self, connection: sqlite3.Connection):
        """创建数据库表"""
        sql_statements = self._get_table_creation_sql()
        
        for table_name, sql in sql_statements.items():
            try:
                connection.execute(sql)
                global_logger.debug('database', f"表 {table_name} 创建/验证完成")
            except sqlite3.Error as e:
                global_logger.error('database', f"创建表 {table_name} 失败: {e}")
                raise
    
    def _get_table_creation_sql(self) -> Dict[str, str]:
        """获取表创建SQL语句"""
        # 这里根据不同数据库类型返回对应的建表SQL
        if self.database_name == 'user_account':
            return {
                'users': """
                CREATE TABLE IF NOT EXISTS users (
                    uid INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid_hash TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_verified BOOLEAN NOT NULL DEFAULT 0,
                    verification_code TEXT,
                    avatar_path TEXT,
                    avatar_hash TEXT,
                    create_time TEXT NOT NULL,
                    last_login_time TEXT
                )
                """
            }
        elif self.database_name == 'journal_submit':
            return {
                'journals': """
                CREATE TABLE IF NOT EXISTS journals (
                    jid INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    file_hash TEXT UNIQUE NOT NULL,
                    file_bucket TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    abstract TEXT,
                    status TEXT NOT NULL DEFAULT 'uploading',
                    create_time TEXT NOT NULL,
                    update_time TEXT,
                    FOREIGN KEY (uid) REFERENCES users (uid)
                )
                """,
                'review_records': """
                CREATE TABLE IF NOT EXISTS review_records (
                    rid INTEGER PRIMARY KEY AUTOINCREMENT,
                    jid INTEGER NOT NULL,
                    reviewer_uid INTEGER NOT NULL,
                    review_time TEXT NOT NULL,
                    result TEXT NOT NULL,
                    comment TEXT,
                    FOREIGN KEY (jid) REFERENCES journals (jid),
                    FOREIGN KEY (reviewer_uid) REFERENCES users (uid)
                )
                """
            }
        elif self.database_name == 'admin_log':
            return {
                'admin_logs': """
                CREATE TABLE IF NOT EXISTS admin_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_uid INTEGER NOT NULL,
                    admin_username TEXT NOT NULL,
                    operation_time TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    operation_object TEXT NOT NULL,
                    operation_details TEXT,
                    ip_address TEXT,
                    user_agent TEXT
                )
                """
            }
        elif self.database_name == 'deleted_journal':
            return {
                'deleted_journals': """
                CREATE TABLE IF NOT EXISTS deleted_journals (
                    jid INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_jid INTEGER NOT NULL,
                    uid INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    file_hash TEXT UNIQUE NOT NULL,
                    file_bucket TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    abstract TEXT,
                    delete_time TEXT NOT NULL,
                    delete_reason TEXT
                )
                """
            }
        elif self.database_name == 'journal_info':
            return {
                'journal_info': """
                CREATE TABLE IF NOT EXISTS journal_info (
                    info_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jid INTEGER NOT NULL,
                    issue_number TEXT NOT NULL,
                    publication_date TEXT NOT NULL,
                    volume TEXT,
                    issue TEXT,
                    journal_type TEXT,
                    keywords TEXT,
                    doi TEXT,
                    FOREIGN KEY (jid) REFERENCES journals (jid)
                )
                """
            }
        elif self.database_name == 'review_opinion':
            return {
                'review_opinions': """
                CREATE TABLE IF NOT EXISTS review_opinions (
                    opinion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jid INTEGER NOT NULL,
                    reviewer_uid INTEGER NOT NULL,
                    review_round INTEGER NOT NULL DEFAULT 1,
                    review_score INTEGER NOT NULL,
                    review_comments TEXT NOT NULL,
                    recommendations TEXT,
                    submitted_at TEXT NOT NULL,
                    FOREIGN KEY (jid) REFERENCES journals (jid),
                    FOREIGN KEY (reviewer_uid) REFERENCES users (uid)
                )
                """
            }
        else:
            return {}
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接（异步上下文管理器）"""
        await self.initialize()
        async with DatabaseConnection(self.db_info.db_path) as conn:
            yield conn
    
    async def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> sqlite3.Cursor:
        """执行SQL语句"""
        async with self.get_connection() as conn:
            if params:
                cursor = conn.connection.execute(sql, params)
            else:
                cursor = conn.connection.execute(sql)
            conn.connection.commit()
            return cursor
    
    async def executemany(self, sql: str, params_list: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """批量执行SQL语句"""
        async with self.get_connection() as conn:
            cursor = conn.connection.executemany(sql, params_list)
            conn.connection.commit()
            return cursor
    
    async def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """获取单行结果"""
        async with self.get_connection() as conn:
            if params:
                cursor = conn.connection.execute(sql, params)
            else:
                cursor = conn.connection.execute(sql)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    async def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """获取所有结果"""
        async with self.get_connection() as conn:
            if params:
                cursor = conn.connection.execute(sql, params)
            else:
                cursor = conn.connection.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def fetchval(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """获取单个值"""
        async with self.get_connection() as conn:
            if params:
                cursor = conn.connection.execute(sql, params)
            else:
                cursor = conn.connection.execute(sql)
            row = cursor.fetchone()
            return row[0] if row else None
    
    async def create_indexes(self):
        """创建索引"""
        index_sql = self._get_index_creation_sql()
        for table_name, indexes in index_sql.items():
            for index_sql in indexes:
                try:
                    await self.execute(index_sql)
                    global_logger.debug('database', f"索引创建完成: {index_sql[:50]}...")
                except sqlite3.Error as e:
                    global_logger.warning('database', f"索引创建失败: {e}")
    
    def _get_index_creation_sql(self) -> Dict[str, List[str]]:
        """获取索引创建SQL语句"""
        indexes = {}
        
        if self.database_name == 'journal_submit':
            indexes['journals'] = [
                "CREATE INDEX IF NOT EXISTS idx_journals_uid ON journals (uid)",
                "CREATE INDEX IF NOT EXISTS idx_journals_file_hash ON journals (file_hash)",
                "CREATE INDEX IF NOT EXISTS idx_journals_status ON journals (status)",
                "CREATE INDEX IF NOT EXISTS idx_journals_file_bucket ON journals (file_bucket)"
            ]
            indexes['review_records'] = [
                "CREATE INDEX IF NOT EXISTS idx_review_records_jid ON review_records (jid)",
                "CREATE INDEX IF NOT EXISTS idx_review_records_reviewer_uid ON review_records (reviewer_uid)"
            ]
        elif self.database_name == 'user_account':
            indexes['users'] = [
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)",
                "CREATE INDEX IF NOT EXISTS idx_users_uid_hash ON users (uid_hash)"
            ]
        elif self.database_name == 'admin_log':
            indexes['admin_logs'] = [
                "CREATE INDEX IF NOT EXISTS idx_admin_logs_time ON admin_logs (operation_time)",
                "CREATE INDEX IF NOT EXISTS idx_admin_logs_type ON admin_logs (operation_type)"
            ]
        elif self.database_name == 'deleted_journal':
            indexes['deleted_journals'] = [
                "CREATE INDEX IF NOT EXISTS idx_deleted_journals_uid ON deleted_journals (uid)",
                "CREATE INDEX IF NOT EXISTS idx_deleted_journals_time ON deleted_journals (delete_time)"
            ]
        
        return indexes


class DatabaseManager:
    """数据库管理器 - 管理所有数据库实例"""
    
    def __init__(self):
        self.services: Dict[str, DatabaseService] = {}
        self._initialized = False
    
    def get_service(self, database_name: str) -> DatabaseService:
        """获取数据库服务实例"""
        if database_name not in self.services:
            self.services[database_name] = DatabaseService(database_name)
        return self.services[database_name]
    
    async def initialize_all(self):
        """初始化所有数据库"""
        if self._initialized:
            return
        
        try:
            # 获取所有数据库配置
            db_names = db_config.get_all_database_names()
            
            # 并行初始化所有数据库
            tasks = []
            for db_name in db_names:
                service = self.get_service(db_name)
                tasks.append(service.initialize())
            
            await asyncio.gather(*tasks)
            
            # 创建索引
            index_tasks = []
            for db_name in db_names:
                service = self.get_service(db_name)
                index_tasks.append(service.create_indexes())
            
            await asyncio.gather(*index_tasks)
            
            self._initialized = True
            global_logger.info('database', f"所有数据库初始化完成，共 {len(db_names)} 个数据库")
            
        except Exception as e:
            global_logger.error('database', f"数据库初始化失败: {e}")
            raise RuntimeError(f"数据库初始化失败: {e}")
    
    async def get_database_info(self, database_name: str) -> DatabaseInfo:
        """获取数据库信息"""
        return db_config.get_database_info(database_name)
    
    def get_all_database_names(self) -> List[str]:
        """获取所有数据库名称"""
        return db_config.get_all_database_names()


# 全局数据库管理器实例
db_manager = DatabaseManager()


