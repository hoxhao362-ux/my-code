import sqlite3
import asyncio
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple

class Database:
    def __init__(self, db_path: str = "./journal.db"):
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self.pool = None
        
    async def connect(self):
        """建立数据库连接池"""
        # SQLite3不支持真正的连接池，这里使用单连接模式
        loop = asyncio.get_event_loop()
        self.conn = await loop.run_in_executor(None, sqlite3.connect, self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    async def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    async def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> sqlite3.Cursor:
        """执行SQL语句"""
        loop = asyncio.get_event_loop()
        if params:
            return await loop.run_in_executor(None, self.conn.execute, sql, params)
        else:
            return await loop.run_in_executor(None, self.conn.execute, sql)
    
    async def executemany(self, sql: str, params: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """批量执行SQL语句"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.conn.executemany, sql, params)
    
    async def commit(self):
        """提交事务"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.conn.commit)
    
    async def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """获取单行结果"""
        cursor = await self.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    async def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """获取所有结果"""
        cursor = await self.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def fetchval(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """获取单个值"""
        cursor = await self.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else None
    
    async def create_tables(self):
        """创建数据库表"""
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
                status TEXT NOT NULL DEFAULT 'pending',
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
        
        await self.commit()

# 创建全局数据库实例
db = Database()
