import sqlite3
import asyncio
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple

class Database:
    def __init__(self, db_path: str = "./journal.db"):
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self.conn = None
        
    async def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> sqlite3.Cursor:
        """执行SQL语句"""
        loop = asyncio.get_event_loop()
        
        def _execute():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            if params:
                cursor = conn.execute(sql, params)
            else:
                cursor = conn.execute(sql)
            conn.commit()
            conn.close()
            return cursor
        
        return await loop.run_in_executor(None, _execute)
    
    async def executemany(self, sql: str, params: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """批量执行SQL语句"""
        loop = asyncio.get_event_loop()
        
        def _executemany():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.executemany(sql, params)
            conn.commit()
            conn.close()
            return cursor
        
        return await loop.run_in_executor(None, _executemany)
    
    async def commit(self):
        """提交事务"""
        # 由于每次执行SQL都已自动提交，此方法不再需要
        pass
    
    async def connect(self):
        """建立数据库连接"""
        # SQLite3不支持真正的连接池，这里使用单连接模式
        # 但由于线程安全问题，我们不再使用全局连接
        pass
    
    async def close(self):
        """关闭数据库连接"""
        # 由于每次执行SQL都创建新连接，此方法不再需要
        pass
    
    async def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """获取单行结果"""
        loop = asyncio.get_event_loop()
        
        def _fetchone():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            if params:
                cursor = conn.execute(sql, params)
            else:
                cursor = conn.execute(sql)
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        
        return await loop.run_in_executor(None, _fetchone)
    
    async def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """获取所有结果"""
        loop = asyncio.get_event_loop()
        
        def _fetchall():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            if params:
                cursor = conn.execute(sql, params)
            else:
                cursor = conn.execute(sql)
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        
        return await loop.run_in_executor(None, _fetchall)
    
    async def fetchval(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """获取单个值"""
        loop = asyncio.get_event_loop()
        
        def _fetchval():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            if params:
                cursor = conn.execute(sql, params)
            else:
                cursor = conn.execute(sql)
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        
        return await loop.run_in_executor(None, _fetchval)
    
    async def create_tables(self, table_type: str = "main"):
        """创建数据库表"""
        if table_type == "main":
            # 创建用户表
            await self.execute("""
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
            """)
            
            # 创建文献表，优化存储结构
            await self.execute("""
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
            """)
            
            # 创建索引，提升查询性能
            await self.execute("CREATE INDEX IF NOT EXISTS idx_journals_uid ON journals (uid)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_journals_file_hash ON journals (file_hash)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_journals_status ON journals (status)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_journals_file_bucket ON journals (file_bucket)")
            
            # 创建用户索引，提升查询性能
            await self.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_users_uid_hash ON users (uid_hash)")
            
            # 创建审核记录表
            await self.execute("""
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
            """)
            
            # 创建审核记录索引
            await self.execute("CREATE INDEX IF NOT EXISTS idx_review_records_jid ON review_records (jid)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_review_records_reviewer_uid ON review_records (reviewer_uid)")
        elif table_type == "admin_log":
            # 创建管理员操作日志表
            await self.execute("""
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
            """)
            
            # 创建索引，提升查询性能
            await self.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_time ON admin_logs (operation_time)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_type ON admin_logs (operation_type)")
        elif table_type == "deleted_journal":
            # 创建已删除文献表
            await self.execute("""
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
            """)
            
            # 创建索引，提升查询性能
            await self.execute("CREATE INDEX IF NOT EXISTS idx_deleted_journals_uid ON deleted_journals (uid)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_deleted_journals_time ON deleted_journals (delete_time)")
        
        await self.commit()

class DatabaseManager:
    """数据库管理器，用于管理多个数据库实例"""
    def __init__(self):
        self.databases = {}
    
    def add_database(self, name: str, db_path: Path):
        """添加数据库实例"""
        self.databases[name] = Database(db_path)
    
    def get_database(self, name: str) -> Database:
        """获取数据库实例"""
        return self.databases.get(name)
    
    async def connect_all(self):
        """连接所有数据库"""
        for db_instance in self.databases.values():
            await db_instance.connect()
    
    async def close_all(self):
        """关闭所有数据库"""
        for db_instance in self.databases.values():
            await db_instance.close()
    
    async def create_all_tables(self):
        """创建所有数据库表"""
        # 创建主数据库表
        if self.databases.get("main"):
            await self.databases["main"].create_tables("main")
        # 创建管理员日志表
        if self.databases.get("admin_log"):
            await self.databases["admin_log"].create_tables("admin_log")
        # 创建已删除文献表
        if self.databases.get("deleted_journal"):
            await self.databases["deleted_journal"].create_tables("deleted_journal")

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

# 兼容旧代码，保留db实例
db = Database()
