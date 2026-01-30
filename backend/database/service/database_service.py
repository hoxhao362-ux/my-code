"""
数据库服务层 - 统一管理所有数据库操作 (PostgreSQL 原生版)

本模块提供了基于 asyncpg 的数据库操作适配层，主要功能包括：
1. 统一的异步数据库操作接口（execute, fetchone, fetchall 等）。
2. 基于连接池的高性能并发处理。
3. 自动化表结构与索引管理。
4. 深度集成项目全局日志与配置系统。

主要类：
- DatabaseConnection: 数据库连接包装器，适配 asyncpg。
- DatabaseService: 逻辑数据库操作服务，负责具体表的操作。
- DatabaseManager: 全局数据库管理器，维护连接池与服务生命周期。
"""
import asyncio
import asyncpg
import os
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import asynccontextmanager

from utils.log import global_logger
from core.config import config
from core.service_manager import BaseManagedService
from database.config.database_config import db_config


class DatabaseConnection:
    """
    数据库连接包装器
    用于在 asyncpg 连接池之上提供统一的连接持有对象。
    """
    
    def __init__(self, connection: asyncpg.Connection):
        """
        初始化连接包装器
        
        Args:
            connection: asyncpg 的原始连接对象
        """
        self._connection = connection
    
    @property
    def connection(self) -> asyncpg.Connection:
        """获取原始 asyncpg 连接对象"""
        return self._connection


class DatabaseService:
    """
    数据库服务类
    提供面向具体逻辑数据库（如 user_account）的统一操作接口。
    """
    
    def __init__(self, database_name: str, manager: 'DatabaseManager'):
        """
        初始化数据库服务
        
        Args:
            database_name: 数据库名称标识
            manager: 全局数据库管理器实例
        """
        self.database_name = database_name
        self.manager = manager
        self.logger = global_logger
        self._initialized = False

    @property
    def pool(self) -> asyncpg.Pool:
        """动态获取连接池，支持延迟初始化"""
        if not self.manager.pool:
            raise RuntimeError(f"数据库连接池尚未就绪，无法执行 {self.database_name} 的操作。请确保在 lifespan 启动后再调用数据库。")
        return self.manager.pool
    
    async def initialize(self):
        """
        初始化数据库环境
        包括验证连接池状态及执行表结构同步。
        """
        if self._initialized:
            return
        
        try:
            async with self.pool.acquire() as conn:
                await self._create_tables(conn)
            
            self._initialized = True
            global_logger.info('database', f"数据库服务 {self.database_name} 表结构同步完成")
            
        except Exception as e:
            global_logger.error('database', f"数据库服务 {self.database_name} 初始化失败: {e}")
            raise RuntimeError(f"数据库服务 {self.database_name} 初始化失败") from e
    
    async def _create_tables(self, connection: asyncpg.Connection):
        """执行建表逻辑"""
        sql_statements = self._get_table_creation_sql()
        
        for table_name, sql in sql_statements.items():
            try:
                await connection.execute(sql)
                global_logger.debug('database', f"表 {table_name} 状态验证成功")
            except Exception as e:
                global_logger.error('database', f"创建/验证表 {table_name} 失败: {e}")
                raise
    
    def _get_table_creation_sql(self) -> Dict[str, str]:
        """获取 PostgreSQL 语法的建表 SQL 字典"""
        match self.database_name:
            case 'user_account':
                return {
                    'users': """
                    CREATE TABLE IF NOT EXISTS users (
                        uid SERIAL PRIMARY KEY,
                        uid_hash TEXT UNIQUE NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        role TEXT NOT NULL DEFAULT 'normal',
                        is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                        verification_code TEXT,
                        avatar_path TEXT,
                        avatar_hash TEXT,
                        create_time TEXT NOT NULL,
                        last_login_time TEXT
                    )
                    """
                }
            case 'journal_submit':
                return {
                    'journals': """
                    CREATE TABLE IF NOT EXISTS journals (
                        jid BIGSERIAL PRIMARY KEY,
                        uid INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        authors TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        file_hash TEXT UNIQUE NOT NULL,
                        file_bucket TEXT NOT NULL,
                        file_name TEXT NOT NULL,
                        file_size BIGINT NOT NULL,
                        abstract TEXT,
                        status TEXT NOT NULL DEFAULT 'uploading',
                        create_time TEXT NOT NULL,
                        update_time TEXT
                    )
                    """,
                    'review_records': """
                    CREATE TABLE IF NOT EXISTS review_records (
                        rid BIGSERIAL PRIMARY KEY,
                        jid BIGINT NOT NULL,
                        reviewer_uid INTEGER NOT NULL,
                        review_time TEXT NOT NULL,
                        result TEXT NOT NULL,
                        comment TEXT,
                        FOREIGN KEY (jid) REFERENCES journals (jid),
                        FOREIGN KEY (reviewer_uid) REFERENCES users (uid)
                    )
                    """
                }
            case 'admin_log':
                return {
                    'admin_logs': """
                    CREATE TABLE IF NOT EXISTS admin_logs (
                        log_id SERIAL PRIMARY KEY,
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
            case 'deleted_journal':
                return {
                    'deleted_journals': """
                    CREATE TABLE IF NOT EXISTS deleted_journals (
                        jid SERIAL PRIMARY KEY,
                        original_jid INTEGER NOT NULL,
                        uid INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        authors TEXT NOT NULL,
                        file_hash TEXT UNIQUE NOT NULL,
                        file_bucket TEXT NOT NULL,
                        file_name TEXT NOT NULL,
                        file_size BIGINT NOT NULL,
                        abstract TEXT,
                        delete_time TEXT NOT NULL,
                        delete_reason TEXT
                    )
                    """
                }
            case 'journal_info':
                return {
                    'journal_info': """
                    CREATE TABLE IF NOT EXISTS journal_info (
                        info_id SERIAL PRIMARY KEY,
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
            case 'review_opinion':
                return {
                    'review_opinions': """
                    CREATE TABLE IF NOT EXISTS review_opinions (
                        opinion_id SERIAL PRIMARY KEY,
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
            case 'invitation_code':
                return {
                    'invitation_codes': """
                    CREATE TABLE IF NOT EXISTS invitation_codes (
                        code_id SERIAL PRIMARY KEY,
                        code TEXT UNIQUE NOT NULL,
                        role TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active',
                        max_uses INTEGER NOT NULL DEFAULT 1,
                        used_count INTEGER NOT NULL DEFAULT 0,
                        description TEXT,
                        created_by TEXT NOT NULL,
                        created_by_uid INTEGER NOT NULL,
                        create_time TEXT NOT NULL,
                        expire_time TEXT,
                        FOREIGN KEY (created_by_uid) REFERENCES users (uid)
                    )
                    """,
                    'invitation_code_usage': """
                    CREATE TABLE IF NOT EXISTS invitation_code_usage (
                        usage_id SERIAL PRIMARY KEY,
                        code TEXT NOT NULL,
                        used_by_uid INTEGER NOT NULL,
                        used_by_username TEXT NOT NULL,
                        use_time TEXT NOT NULL,
                        FOREIGN KEY (used_by_uid) REFERENCES users (uid)
                    )
                    """
                }
            case _:
                return {}
    
    @asynccontextmanager
    async def get_connection(self):
        """
        获取数据库连接上下文
        
        Yields:
            DatabaseConnection: 连接包装器
        """
        async with self.pool.acquire() as conn:
            yield DatabaseConnection(conn)
    
    async def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> str:
        """
        执行命令（INSERT/UPDATE/DELETE）
        
        Args:
            sql: 原生 PostgreSQL SQL 语句（使用 $1, $2 占位符）
            params: 参数元组
            
        Returns:
            str: 命令执行状态字符串（如 "UPDATE 1"）
        """
        async with self.pool.acquire() as conn:
            if params:
                return await conn.execute(sql, *params)
            else:
                return await conn.execute(sql)
    
    async def executemany(self, sql: str, params_list: List[Tuple[Any, ...]]) -> str:
        """
        批量执行命令
        
        Args:
            sql: 原生 PostgreSQL SQL 语句
            params_list: 参数元组列表
        """
        async with self.pool.acquire() as conn:
            return await conn.executemany(sql, params_list)
    
    async def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """
        查询单行记录
        
        Args:
            sql: 原生 PostgreSQL SQL 语句
            params: 参数元组
            
        Returns:
            Optional[Dict]: 记录字典，无结果返回 None
        """
        async with self.pool.acquire() as conn:
            if params:
                row = await conn.fetchrow(sql, *params)
            else:
                row = await conn.fetchrow(sql)
            return dict(row) if row else None
    
    async def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """
        查询多行记录
        
        Args:
            sql: 原生 PostgreSQL SQL 语句
            params: 参数元组
            
        Returns:
            List[Dict]: 记录字典列表
        """
        async with self.pool.acquire() as conn:
            if params:
                rows = await conn.fetch(sql, *params)
            else:
                rows = await conn.fetch(sql)
            return [dict(row) for row in rows]
    
    async def fetchval(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """
        查询单个标量值
        
        Args:
            sql: 原生 PostgreSQL SQL 语句
            params: 参数元组
            
        Returns:
            Any: 查询到的值
        """
        async with self.pool.acquire() as conn:
            if params:
                return await conn.fetchval(sql, *params)
            else:
                return await conn.fetchval(sql)
    
    async def create_indexes(self):
        """执行索引同步计划"""
        index_sql = self._get_index_creation_sql()
        for table_name, indexes in index_sql.items():
            for sql in indexes:
                try:
                    await self.execute(sql)
                    global_logger.debug('database', f"索引同步完成: {sql[:50]}...")
                except Exception as e:
                    global_logger.warning('database', f"索引创建跳过: {e}")
    
    def _get_index_creation_sql(self) -> Dict[str, List[str]]:
        """获取索引创建 SQL 字典"""
        indexes = {}
        match self.database_name:
            case 'journal_submit':
                indexes['journals'] = [
                    "CREATE INDEX IF NOT EXISTS idx_journals_uid ON journals (uid)",
                    "CREATE INDEX IF NOT EXISTS idx_journals_file_hash ON journals (file_hash)",
                    "CREATE INDEX IF NOT EXISTS idx_journals_status ON journals (status)"
                ]
                indexes['review_records'] = [
                    "CREATE INDEX IF NOT EXISTS idx_review_records_jid ON review_records (jid)",
                    "CREATE INDEX IF NOT EXISTS idx_review_records_reviewer_uid ON review_records (reviewer_uid)"
                ]
            case 'user_account':
                indexes['users'] = [
                    "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)",
                    "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)"
                ]
        return indexes


class DatabaseManager(BaseManagedService):
    """
    数据库全局管理器
    实现 BaseManagedService 接口，负责连接池的生命周期与服务分发。
    """
    
    def __init__(self):
        super().__init__("database")
        self.services: Dict[str, DatabaseService] = {}
        self.pool: Optional[asyncpg.Pool] = None
        self._initialized = False
    
    async def start(self):
        """定制化启动：环境变量配置 -> 进程启动 -> 连接池初始化 -> 结构同步"""
        global_logger.info("Database", "启动数据库托管服务...")
        
        exe_path = config["global.global.database_service_path"]
        args = await self._check_args(config["global.global.database_service_args"])
        db_dir = config["global.global.database_dir"]
        
        os.environ["PGDATA"] = db_dir
        
        cmd_parts = [f'"{exe_path}"', "start"]
        for k, v in args.items():
            cmd_parts.append(f'{k} "{v}"')
        
        start_cmd = " ".join(cmd_parts)
        
        try:
            process = await self._create_process(start_cmd)
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                err_msg = stderr.decode('gbk', errors='ignore')
                if "already running" not in err_msg and "另一个进程正在使用" not in err_msg:
                    global_logger.error("Database", f"PostgreSQL 进程启动异常: {err_msg}")
            
            await self.initialize_all()
            
        except Exception as e:
            global_logger.error("Database", f"数据库服务启动失败: {e}")
            raise

    async def stop(self):
        """安全关闭计划"""
        global_logger.info("Database", "安全关闭数据库服务...")
        
        exe_path = config["global.global.database_service_path"]
        db_dir = config["global.global.database_dir"]
        
        stop_cmd = f'"{exe_path}" stop -D "{db_dir}" -m fast'
        try:
            await self.close_all()
            process = await asyncio.create_subprocess_shell(
                stop_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            global_logger.info("Database", "PostgreSQL 进程已安全退出")
        except Exception as e:
            global_logger.error("Database", f"数据库关闭异常: {e}")

    async def _init_pool(self):
        """初始化连接池（含重试检查机制）"""
        if self.pool:
            return
            
        try:
            host = config["global.global.database_host"]
            port = config["global.global.database_port"]
            user = config["global.global.database_user"]
            password = config.get("global.global.database_password")
            database = config["global.global.database_name"]
            
            if password is None or (isinstance(password, float) and password != password):
                password = None

            retry_count = 0
            max_retries = 30
            while retry_count < max_retries:
                try:
                    self.pool = await asyncpg.create_pool(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        min_size=5,
                        max_size=20,
                        command_timeout=60
                    )
                    global_logger.info('database', f"PostgreSQL 连接池就绪: {host}:{port}/{database}")
                    return
                except (ConnectionRefusedError, asyncpg.PostgresError):
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    await asyncio.sleep(1)
                    
        except Exception as e:
            global_logger.error('database', f"无法建立数据库连接池: {e}")
            raise RuntimeError("数据库连接池初始化失败") from e

    def get_service(self, database_name: str) -> DatabaseService:
        """
        分发逻辑数据库服务
        支持在连接池就绪前获取服务实例（延迟初始化）。
        """
        if database_name not in self.services:
            self.services[database_name] = DatabaseService(database_name, self)
        return self.services[database_name]
    
    async def initialize_all(self):
        """全量初始化：池初始化 -> 表结构同步 -> 索引同步"""
        if self._initialized:
            return
        
        try:
            await self._init_pool()
            db_names = db_config.get_all_database_names()
            
            for db_name in db_names:
                service = self.get_service(db_name)
                await service.initialize()
            
            for db_name in db_names:
                service = self.get_service(db_name)
                await service.create_indexes()
            
            self._initialized = True
            global_logger.info('database', f"全量数据库环境初始化成功 (PostgreSQL)")
            
        except Exception as e:
            global_logger.error('database', f"数据库环境初始化失败: {e}")
            raise RuntimeError("数据库环境初始化失败") from e

    async def close_all(self):
        """彻底清理资源"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self._initialized = False
            global_logger.info('database', "数据库连接池已销毁")


# 全局单例管理器
db_manager = DatabaseManager()
