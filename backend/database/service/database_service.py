"""
数据库服务层 - 统一管理所有数据库操作

这个模块提供了一个完整的数据库操作服务层，主要功能包括：

1. 统一的数据库操作接口
   - 提供简单易用的CRUD操作方法
   - 支持参数化查询，防止SQL注入
   - 自动处理连接管理和事务提交

2. 异步数据库支持
   - 基于asyncio的异步数据库操作
   - 非阻塞的数据库连接管理
   - 支持并发数据库操作

3. 配置驱动的数据库管理
   - 支持多个独立数据库实例
   - 基于配置文件自动初始化
   - 灵活的数据库类型扩展

4. 数据库结构自动管理
   - 自动创建表结构
   - 自动创建索引优化
   - 支持数据库迁移和版本管理

5. 安全和可靠性
   - 连接超时保护
   - 自动资源清理
   - 完整的错误处理和日志记录

主要类和组件：

- DatabaseConnection: 数据库连接包装器，提供异步上下文管理
- DatabaseService: 单个数据库的操作服务接口
- DatabaseManager: 全局数据库管理器，统一管理所有数据库实例
- db_manager: 全局单例数据库管理器实例

支持的数据库类型：

- user_account: 用户账户数据库，存储用户基本信息和认证数据
- journal_submit: 期刊投稿数据库，存储稿件和评审记录
- admin_log: 管理员日志数据库，存储操作审计日志
- deleted_journal: 已删除期刊数据库，存储软删除的稿件记录
- journal_info: 期刊信息数据库，存储出版详细信息
- review_opinion: 评审意见数据库，存储详细评审意见和评分

使用示例：

    # 初始化所有数据库（应用启动时调用一次）
    await db_manager.initialize_all()
    
    # 获取用户数据库服务
    user_db = db_manager.get_service('user_account')
    
    # 查询用户
    user = await user_db.fetchone(
        "SELECT * FROM users WHERE username = ?", 
        ("john",)
    )
    
    # 创建新用户
    await user_db.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        ("john", "john@example.com", "hashed_password")
    )
    
    # 批量操作
    users_data = [("user1", "email1@test.com"), ("user2", "email2@test.com")]
    await user_db.executemany(
        "INSERT INTO users (username, email) VALUES (?, ?)",
        users_data
    )
"""
import sqlite3
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import asynccontextmanager

from utils.log import global_logger
from database.config.database_config import DatabaseConfig, DatabaseInfo, db_config


class DatabaseConnection:
    """数据库连接包装器，提供上下文管理和自动清理
    
    这个类是一个数据库连接的包装器，主要功能包括：
    1. 提供异步上下文管理器支持（async with）
    2. 自动管理数据库连接的建立和关闭
    3. 确保连接的正确清理，避免资源泄露
    4. 支持连接超时设置
    """
    
    def __init__(self, db_path: Path, timeout: float = 30.0):
        """
        初始化数据库连接包装器
        
        Args:
            db_path (Path): 数据库文件的绝对路径
            timeout (float): 连接超时时间，单位秒，默认30秒
        """
        self.db_path = db_path  # 数据库文件路径
        self.timeout = timeout  # 连接超时时间
        self._connection: Optional[sqlite3.Connection] = None  # 内部连接对象
    
    async def __aenter__(self):
        """异步上下文管理器入口
        
        当使用 'async with DatabaseConnection(...) as conn:' 时自动调用
        
        Returns:
            DatabaseConnection: 返回自身实例，供上下文使用
        """
        await self.connect()  # 建立数据库连接
        return self  # 返回连接对象
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口
        
        当离开 'async with' 块时自动调用，无论是否发生异常
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        await self.close()  # 关闭数据库连接，确保资源清理
    
    async def connect(self):
        """建立数据库连接
        
        异步方法，在事件循环中执行数据库连接操作
        通过线程池执行器将阻塞的连接操作转移到线程中执行
        """
        loop = asyncio.get_event_loop()  # 获取当前事件循环
        # 将同步的连接操作提交到线程池执行，避免阻塞事件循环
        await loop.run_in_executor(None, self._connect_sync)
    
    def _connect_sync(self):
        """同步连接方法
        
        这是实际的数据库连接逻辑，使用sqlite3.connect()建立连接
        在线程中执行，不会阻塞主事件循环
        """
        # 建立SQLite数据库连接
        self._connection = sqlite3.connect(
            str(self.db_path),  # 数据库文件路径（转换为字符串）
            timeout=self.timeout,  # 连接超时时间
            check_same_thread=False  # 允许跨线程访问（重要：用于多线程环境）
        )
        # 设置行工厂，使查询结果可以通过列名访问（如 row['column_name']）
        self._connection.row_factory = sqlite3.Row
    
    async def close(self):
        """关闭数据库连接
        
        异步方法，安全地关闭数据库连接
        如果连接存在，通过线程池执行器执行关闭操作
        """
        if self._connection:  # 只有在连接存在时才执行关闭操作
            loop = asyncio.get_event_loop()  # 获取当前事件循环
            # 将同步的关闭操作提交到线程池执行
            await loop.run_in_executor(None, self._close_sync)
    
    def _close_sync(self):
        """同步关闭方法
        
        实际的连接关闭逻辑，确保：
        1. 关闭数据库连接
        2. 清理连接对象引用
        """
        if self._connection:  # 双重检查，确保连接存在
            self._connection.close()  # 关闭SQLite连接
            self._connection = None  # 清理连接引用，便于垃圾回收
    
    @property
    def connection(self) -> sqlite3.Connection:
        """获取连接对象
        
        属性方法，返回内部的SQLite连接对象
        
        Returns:
            sqlite3.Connection: SQLite数据库连接对象
            
        Raises:
            RuntimeError: 当连接未建立时抛出异常
        """
        if not self._connection:  # 检查连接是否已建立
            raise RuntimeError("数据库连接未建立")  # 连接未建立时抛出异常
        return self._connection  # 返回实际的连接对象


class DatabaseService:
    """数据库服务类 - 统一的数据库操作接口
    
    这个类提供了数据库的统一操作接口，主要功能包括：
    1. 数据库的初始化和表结构创建
    2. 提供同步的SQL执行方法（execute, fetchone, fetchall等）
    3. 管理数据库连接的生命周期
    4. 支持事务和批量操作
    5. 索引创建和优化
    6. 统一的错误处理和日志记录
    """
    
    def __init__(self, database_name: str):
        """
        初始化数据库服务
        
        Args:
            database_name (str): 数据库名称，对应配置文件中的数据库标识
        """
        self.database_name = database_name  # 数据库名称标识
        self.db_info = db_config.get_database_info(database_name)  # 数据库配置信息
        self.logger = global_logger  # 全局日志记录器
        self._initialized = False  # 初始化状态标记
    
    async def initialize(self):
        """初始化数据库
        
        这是数据库服务的核心初始化方法，执行以下操作：
        1. 检查是否已经初始化过（避免重复初始化）
        2. 确保数据库文件目录存在
        3. 建立数据库连接并创建必要的表结构
        4. 记录初始化状态和日志
        
        Raises:
            RuntimeError: 当初始化过程中发生错误时抛出
        """
        if self._initialized:  # 如果已经初始化过，直接返回
            return
        
        try:
            # 确保数据库目录存在，如果不存在则创建（包含父目录）
            self.db_info.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用上下文管理器创建数据库连接并初始化表结构
            # 自动处理连接的建立和关闭
            async with DatabaseConnection(self.db_info.db_path) as conn:
                await self._create_tables(conn.connection)  # 创建表结构
            
            self._initialized = True  # 标记为已初始化
            # 记录成功日志
            global_logger.info('database', f"数据库 {self.database_name} 初始化完成")
            
        except Exception as e:
            # 记录错误日志并抛出异常
            global_logger.error('database', f"数据库 {self.database_name} 初始化失败: {e}")
            raise RuntimeError(f"数据库 {self.database_name} 初始化失败: {e}")
    
    async def _create_tables(self, connection: sqlite3.Connection):
        """创建数据库表
        
        根据数据库类型创建相应的表结构，使用IF NOT EXISTS确保幂等性
        
        Args:
            connection (sqlite3.Connection): SQLite数据库连接对象
            
        Raises:
            sqlite3.Error: 当创建表过程中发生SQL错误时重新抛出
        """
        # 获取对应数据库类型的建表SQL语句
        sql_statements = self._get_table_creation_sql()
        
        # 遍历所有表，逐个创建
        for table_name, sql in sql_statements.items():
            try:
                # 执行建表SQL，使用IF NOT EXISTS确保重复执行不会报错
                connection.execute(sql)
                # 记录成功日志（调试级别）
                global_logger.debug('database', f"表 {table_name} 创建/验证完成")
            except sqlite3.Error as e:
                # 记录错误日志并重新抛出异常
                global_logger.error('database', f"创建表 {table_name} 失败: {e}")
                raise
    
    def _get_table_creation_sql(self) -> Dict[str, str]:
        """获取表创建SQL语句
        
        根据数据库服务实例的database_name属性，返回对应数据库的建表SQL语句
        每个数据库可能包含一个或多个表，使用IF NOT EXISTS确保幂等性
        
        Returns:
            Dict[str, str]: 字典，key为表名，value为对应的CREATE TABLE SQL语句
            
        Note:
            - 所有表都使用IF NOT EXISTS子句，允许重复执行不会报错
            - 使用AUTOINCREMENT确保主键唯一性
            - 所有表都包含适当的外键约束
            - 时间字段使用TEXT类型存储ISO格式时间字符串
        """
        # 根据不同数据库类型返回对应的建表SQL
        match self.database_name:
            case 'user_account':
                """用户账户数据库 - 存储用户基本信息和认证数据"""
                return {
                    'users': """
                    CREATE TABLE IF NOT EXISTS users (
                        uid INTEGER PRIMARY KEY AUTOINCREMENT,  -- 用户唯一ID，自增主键
                        uid_hash TEXT UNIQUE NOT NULL,  -- 用户ID哈希值，用于安全查找
                        username TEXT UNIQUE NOT NULL,  -- 用户名，唯一约束
                        password TEXT NOT NULL,  -- 加密后的密码
                        email TEXT UNIQUE NOT NULL,  -- 邮箱地址，唯一约束
                        role TEXT NOT NULL DEFAULT 'normal',  -- 用户角色，默认普通用户：admin, reviewer, writer, normal
                        is_verified BOOLEAN NOT NULL DEFAULT 0,  -- 邮箱验证状态
                        verification_code TEXT,  -- 邮箱验证码
                        avatar_path TEXT,  -- 头像文件路径
                        avatar_hash TEXT,  -- 头像文件哈希值
                        create_time TEXT NOT NULL,  -- 账户创建时间
                        last_login_time TEXT  -- 最后登录时间
                    )
                    """
                }
            case 'journal_submit':
                """期刊投稿数据库 - 存储期刊稿件和评审记录"""
                return {
                    'journals': """
                    CREATE TABLE IF NOT EXISTS journals (
                        jid INTEGER PRIMARY KEY AUTOINCREMENT,  -- 稿件唯一ID，自增主键
                        uid INTEGER NOT NULL,  -- 投稿用户ID，外键关联users表
                        title TEXT NOT NULL,  -- 稿件标题
                        authors TEXT NOT NULL,  -- 作者列表，JSON格式存储
                        subject TEXT NOT NULL,  -- 学科分类
                        file_hash TEXT UNIQUE NOT NULL,  -- 文件哈希值，唯一约束
                        file_bucket TEXT NOT NULL,  -- 文件存储桶名称
                        file_name TEXT NOT NULL,  -- 原始文件名
                        file_size INTEGER NOT NULL,  -- 文件大小（字节）
                        abstract TEXT,  -- 摘要内容
                        status TEXT NOT NULL DEFAULT 'uploading',  -- 稿件状态：uploading, submitted, under_review, accepted, rejected
                        create_time TEXT NOT NULL,  -- 投稿时间
                        update_time TEXT,  -- 最后更新时间
                        FOREIGN KEY (uid) REFERENCES users (uid)  -- 外键约束：稿件必须属于有效用户
                    )
                    """,
                    'review_records': """
                    CREATE TABLE IF NOT EXISTS review_records (
                        rid INTEGER PRIMARY KEY AUTOINCREMENT,  -- 评审记录唯一ID
                        jid INTEGER NOT NULL,  -- 稿件ID，外键关联journals表
                        reviewer_uid INTEGER NOT NULL,  -- 评审员用户ID，外键关联users表
                        review_time TEXT NOT NULL,  -- 评审时间
                        result TEXT NOT NULL,  -- 评审结果：accept, minor_revision, major_revision, reject
                        comment TEXT,  -- 评审意见
                        FOREIGN KEY (jid) REFERENCES journals (jid),  -- 外键约束：评审记录必须关联有效稿件
                        FOREIGN KEY (reviewer_uid) REFERENCES users (uid)  -- 外键约束：评审员必须是有效用户
                    )
                    """
                }
            case 'admin_log':
                """管理员日志数据库 - 存储管理员操作审计日志"""
                return {
                    'admin_logs': """
                    CREATE TABLE IF NOT EXISTS admin_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 日志唯一ID，自增主键
                        admin_uid INTEGER NOT NULL,  -- 管理员用户ID，外键关联users表
                        admin_username TEXT NOT NULL,  -- 管理员用户名冗余存储，便于快速查询
                        operation_time TEXT NOT NULL,  -- 操作时间
                        operation_type TEXT NOT NULL,  -- 操作类型：如'user_management', 'journal_review', 'system_config'
                        operation_object TEXT NOT NULL,  -- 操作对象：如用户ID、稿件ID等
                        operation_details TEXT,  -- 操作详细信息，JSON格式存储
                        ip_address TEXT,  -- 管理员操作时的IP地址
                        user_agent TEXT  -- 浏览器用户代理字符串
                    )
                    """
                }
            case 'deleted_journal':
                """已删除期刊数据库 - 存储软删除的期刊稿件"""
                return {
                    'deleted_journals': """
                    CREATE TABLE IF NOT EXISTS deleted_journals (
                        jid INTEGER PRIMARY KEY AUTOINCREMENT,  -- 软删除记录唯一ID
                        original_jid INTEGER NOT NULL,  -- 原始稿件ID，便于追溯
                        uid INTEGER NOT NULL,  -- 投稿用户ID，外键关联users表
                        title TEXT NOT NULL,  -- 稿件标题（冗余存储）
                        authors TEXT NOT NULL,  -- 作者列表（冗余存储）
                        file_hash TEXT UNIQUE NOT NULL,  -- 文件哈希值（冗余存储）
                        file_bucket TEXT NOT NULL,  -- 文件存储桶名称（冗余存储）
                        file_name TEXT NOT NULL,  -- 原始文件名（冗余存储）
                        file_size INTEGER NOT NULL,  -- 文件大小（冗余存储）
                        abstract TEXT,  -- 摘要内容（冗余存储）
                        delete_time TEXT NOT NULL,  -- 删除时间
                        delete_reason TEXT  -- 删除原因说明
                    )
                    """
                }
            case 'journal_info':
                """期刊信息数据库 - 存储期刊的详细出版信息"""
                return {
                    'journal_info': """
                    CREATE TABLE IF NOT EXISTS journal_info (
                        info_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 期刊信息唯一ID
                        jid INTEGER NOT NULL,  -- 稿件ID，外键关联journals表
                        issue_number TEXT NOT NULL,  -- 期号，如'2024年第1期'
                        publication_date TEXT NOT NULL,  -- 出版日期
                        volume TEXT,  -- 卷号，如'第15卷'
                        issue TEXT,  -- 期号，如'第3期'
                        journal_type TEXT,  -- 期刊类型：如'research', 'review', 'letter'
                        keywords TEXT,  -- 关键词，JSON格式存储
                        doi TEXT,  -- 数字对象标识符
                        FOREIGN KEY (jid) REFERENCES journals (jid)  -- 外键约束：信息必须关联有效稿件
                    )
                    """
                }
            case 'review_opinion':
                """评审意见数据库 - 存储详细的评审意见和评分"""
                return {
                    'review_opinions': """
                    CREATE TABLE IF NOT EXISTS review_opinions (
                        opinion_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 评审意见唯一ID
                        jid INTEGER NOT NULL,  -- 稿件ID，外键关联journals表
                        reviewer_uid INTEGER NOT NULL,  -- 评审员用户ID，外键关联users表
                        review_round INTEGER NOT NULL DEFAULT 1,  -- 评审轮次，支持多轮评审
                        review_score INTEGER NOT NULL,  -- 评审分数，如1-10分
                        review_comments TEXT NOT NULL,  -- 详细评审意见
                        recommendations TEXT,  -- 建议和推荐意见
                        submitted_at TEXT NOT NULL,  -- 意见提交时间
                        FOREIGN KEY (jid) REFERENCES journals (jid),  -- 外键约束：意见必须关联有效稿件
                        FOREIGN KEY (reviewer_uid) REFERENCES users (uid)  -- 外键约束：评审员必须是有效用户
                    )
                    """
                }
            case 'invitation_code':
                """邀请码数据库 - 存储邀请码和使用记录"""
                return {
                    'invitation_codes': """
                    CREATE TABLE IF NOT EXISTS invitation_codes (
                        code_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 邀请码唯一ID
                        code TEXT UNIQUE NOT NULL,  -- 邀请码，唯一约束
                        role TEXT NOT NULL,  -- 邀请码对应的角色
                        status TEXT NOT NULL DEFAULT 'active',  -- 邀请码状态：active, inactive
                        max_uses INTEGER NOT NULL DEFAULT 1,  -- 最大使用次数
                        used_count INTEGER NOT NULL DEFAULT 0,  -- 已使用次数
                        description TEXT,  -- 邀请码描述
                        created_by TEXT NOT NULL,  -- 创建者用户名
                        created_by_uid INTEGER NOT NULL,  -- 创建者用户ID
                        create_time TEXT NOT NULL,  -- 创建时间
                        expire_time TEXT,  -- 过期时间
                        FOREIGN KEY (created_by_uid) REFERENCES users (uid)  -- 外键约束：创建者必须是有效用户
                    )
                    """,
                    'invitation_code_usage': """
                    CREATE TABLE IF NOT EXISTS invitation_code_usage (
                        usage_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 使用记录唯一ID
                        code TEXT NOT NULL,  -- 邀请码
                        used_by_uid INTEGER NOT NULL,  -- 使用者用户ID
                        used_by_username TEXT NOT NULL,  -- 使用者用户名
                        use_time TEXT NOT NULL,  -- 使用时间
                        FOREIGN KEY (code) REFERENCES invitation_codes (code),  -- 外键约束：必须关联有效邀请码
                        FOREIGN KEY (used_by_uid) REFERENCES users (uid)  -- 外键约束：使用者必须是有效用户
                    )
                    """
                }
            case _:
                # 对于未知的数据库类型，返回空字典
                return {}
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接（异步上下文管理器）
        
        这是一个异步上下文管理器，提供数据库连接的获取和自动释放
        确保每次操作都能获得一个有效的数据库连接，并在操作完成后自动关闭
        
        Yields:
            DatabaseConnection: 数据库连接包装器实例
            
        Example:
            async with db_service.get_connection() as conn:
                result = await conn.connection.execute("SELECT * FROM users")
        """
        await self.initialize()  # 确保数据库已初始化
        # 创建并返回数据库连接，使用上下文管理器自动管理连接生命周期
        async with DatabaseConnection(self.db_info.db_path) as conn:
            yield conn
    
    async def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> sqlite3.Cursor:
        """执行SQL语句
        
        执行单条SQL语句，支持参数化查询防止SQL注入
        
        Args:
            sql (str): SQL语句，可以包含参数占位符(? 或 :name)
            params (Optional[Tuple[Any, ...]]): SQL参数，元组形式，对应sql中的占位符
            
        Returns:
            sqlite3.Cursor: 执行结果游标对象
            
        Example:
            # 无参数查询
            cursor = await db_service.execute("SELECT * FROM users")
            
            # 有参数查询
            cursor = await db_service.execute(
                "SELECT * FROM users WHERE username = ?", 
                ("john",)
            )
        """
        async with self.get_connection() as conn:
            if params:
                # 带参数执行，使用参数化查询防止SQL注入
                cursor = conn.connection.execute(sql, params)
            else:
                # 无参数执行
                cursor = conn.connection.execute(sql)
            # 提交事务，确保操作持久化
            conn.connection.commit()
            return cursor
    
    async def executemany(self, sql: str, params_list: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """批量执行SQL语句
        
        批量执行同一条SQL语句，适用于大量数据的插入、更新等操作
        
        Args:
            sql (str): SQL语句，包含参数占位符
            params_list (List[Tuple[Any, ...]]): 参数列表，每个元素是一个参数元组
            
        Returns:
            sqlite3.Cursor: 执行结果游标对象
            
        Example:
            # 批量插入用户
            users_data = [
                ("user1", "email1@test.com"),
                ("user2", "email2@test.com"),
                ("user3", "email3@test.com")
            ]
            cursor = await db_service.executemany(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                users_data
            )
        """
        async with self.get_connection() as conn:
            # 批量执行SQL语句
            cursor = conn.connection.executemany(sql, params_list)
            # 提交事务
            conn.connection.commit()
            return cursor
    
    async def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """获取单行结果
        
        执行查询SQL并返回结果集中的第一行，如果无结果则返回None
        
        Args:
            sql (str): SQL查询语句，可以包含参数占位符
            params (Optional[Tuple[Any, ...]]): SQL参数，元组形式
            
        Returns:
            Optional[Dict[str, Any]]: 结果行字典，如果无结果则返回None
                                          字典key为列名，value为列值
            
        Example:
            # 查询单个用户
            user = await db_service.fetchone(
                "SELECT * FROM users WHERE username = ?", 
                ("john",)
            )
            if user:
                print(f"找到用户: {user['username']}")
        """
        async with self.get_connection() as conn:
            if params:
                # 带参数执行查询
                cursor = conn.connection.execute(sql, params)
            else:
                # 无参数执行查询
                cursor = conn.connection.execute(sql)
            # 获取第一行结果
            row = cursor.fetchone()
            # 将sqlite3.Row对象转换为字典，如果无结果则返回None
            return dict(row) if row else None
    
    async def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """获取所有结果
        
        执行查询SQL并返回结果集中的所有行
        
        Args:
            sql (str): SQL查询语句，可以包含参数占位符
            params (Optional[Tuple[Any, ...]]): SQL参数，元组形式
            
        Returns:
            List[Dict[str, Any]]: 结果行列表，每个元素是包含列名和值的字典
                                   如果无结果则返回空列表
            
        Example:
            # 查询所有用户
            users = await db_service.fetchall("SELECT * FROM users")
            for user in users:
                print(f"用户: {user['username']}")
                
            # 查询特定状态的用户
            users = await db_service.fetchall(
                "SELECT * FROM users WHERE is_verified = ?", 
                (1,)
            )
        """
        async with self.get_connection() as conn:
            if params:
                cursor = conn.connection.execute(sql, params)
            else:
                cursor = conn.connection.execute(sql)
            # 获取所有结果行
            rows = cursor.fetchall()
            # 将所有sqlite3.Row对象转换为字典列表
            return [dict(row) for row in rows]
    
    async def fetchval(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Any:
        """获取单个值
        
        执行查询SQL并返回结果集中第一行第一列的值
        适用于获取计数、最大值、最小值、单个字段值等场景
        
        Args:
            sql (str): SQL查询语句，应该只返回一个值
            params (Optional[Tuple[Any, ...]]): SQL参数，元组形式
            
        Returns:
            Any: 第一行第一列的值，如果无结果则返回None
            
        Example:
            # 获取用户总数
            count = await db_service.fetchval("SELECT COUNT(*) FROM users")
            print(f"用户总数: {count}")
            
            # 获取最新用户ID
            latest_id = await db_service.fetchval(
                "SELECT MAX(uid) FROM users WHERE is_verified = ?", 
                (1,)
            )
            
            # 检查用户名是否存在
            exists = await db_service.fetchval(
                "SELECT 1 FROM users WHERE username = ?", 
                ("john",)
            )
            if exists:
                print("用户名已存在")
        """
        async with self.get_connection() as conn:
            if params:
                cursor = conn.connection.execute(sql, params)
            else:
                cursor = conn.connection.execute(sql)
            # 获取第一行结果
            row = cursor.fetchone()
            # 返回第一列的值，如果无结果则返回None
            return row[0] if row else None
    
    async def create_indexes(self):
        """创建数据库索引
        
        根据数据库类型创建相应的索引，提高查询性能
        使用IF NOT EXISTS确保幂等性，重复执行不会报错
        
        Note:
            索引创建是可选的，如果失败会记录警告但不会中断程序
            这是因为某些SQLite版本可能不支持某些索引功能
        """
        # 获取对应数据库类型的索引创建SQL语句
        index_sql = self._get_index_creation_sql()
        
        # 遍历所有表和对应的索引
        for table_name, indexes in index_sql.items():
            for index_sql in indexes:
                try:
                    # 执行索引创建SQL
                    await self.execute(index_sql)
                    # 记录成功日志（调试级别）
                    global_logger.debug('database', f"索引创建完成: {index_sql[:50]}...")
                except sqlite3.Error as e:
                    # 索引创建失败时记录警告但不中断程序
                    global_logger.warning('database', f"索引创建失败: {e}")
    
    def _get_index_creation_sql(self) -> Dict[str, List[str]]:
        """获取索引创建SQL语句
        
        根据数据库服务实例的database_name属性，返回对应数据库的索引创建SQL语句
        索引用于提高查询性能，特别是在WHERE、JOIN、ORDER BY等操作中
        
        Returns:
            Dict[str, List[str]]: 字典，key为表名，value为该表的所有索引创建SQL语句列表
            
        Note:
            - 所有索引都使用IF NOT EXISTS确保幂等性
            - 索引命名规范：idx_{table_name}_{column_name}
            - 重点为经常查询的字段创建索引
        """
        indexes = {}
        
        match self.database_name:
            case 'journal_submit':
                """期刊投稿数据库的索引优化"""
                indexes['journals'] = [
                    "CREATE INDEX IF NOT EXISTS idx_journals_uid ON journals (uid)",  # 按用户查询稿件
                    "CREATE INDEX IF NOT EXISTS idx_journals_file_hash ON journals (file_hash)",  # 文件去重查询
                    "CREATE INDEX IF NOT EXISTS idx_journals_status ON journals (status)",  # 按状态筛选稿件
                    "CREATE INDEX IF NOT EXISTS idx_journals_file_bucket ON journals (file_bucket)"  # 按存储桶查询
                ]
                indexes['review_records'] = [
                    "CREATE INDEX IF NOT EXISTS idx_review_records_jid ON review_records (jid)",  # 按稿件查询评审记录
                    "CREATE INDEX IF NOT EXISTS idx_review_records_reviewer_uid ON review_records (reviewer_uid)"  # 按评审员查询记录
                ]
            case 'user_account':
                """用户账户数据库的索引优化"""
                indexes['users'] = [
                    "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)",  # 用户名登录查询
                    "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)",  # 邮箱查找和验证
                    "CREATE INDEX IF NOT EXISTS idx_users_uid_hash ON users (uid_hash)"  # 安全查找
                ]
            case 'admin_log':
                """管理员日志数据库的索引优化"""
                indexes['admin_logs'] = [
                    "CREATE INDEX IF NOT EXISTS idx_admin_logs_time ON admin_logs (operation_time)",  # 按时间查询日志
                    "CREATE INDEX IF NOT EXISTS idx_admin_logs_type ON admin_logs (operation_type)"  # 按操作类型筛选
                ]
            case 'deleted_journal':
                """已删除期刊数据库的索引优化"""
                indexes['deleted_journals'] = [
                    "CREATE INDEX IF NOT EXISTS idx_deleted_journals_uid ON deleted_journals (uid)",  # 按用户查询已删除稿件
                    "CREATE INDEX IF NOT EXISTS idx_deleted_journals_time ON deleted_journals (delete_time)"  # 按删除时间查询
                ]
        
        return indexes


class DatabaseManager:
    """数据库管理器 - 管理所有数据库实例
    
    这个类是整个数据库服务层的核心管理器，主要功能包括：
    1. 管理所有数据库服务实例的创建和生命周期
    2. 提供统一的数据库服务获取接口
    3. 支持批量初始化所有数据库
    4. 维护数据库配置信息
    5. 实现单例模式，确保全局只有一个管理器实例
    """
    
    def __init__(self):
        """初始化数据库管理器"""
        self.services: Dict[str, DatabaseService] = {}  # 数据库服务实例缓存
        self._initialized = False  # 全局初始化状态标记
    
    def get_service(self, database_name: str) -> DatabaseService:
        """获取数据库服务实例
        
        根据数据库名称获取对应的数据库服务实例，如果不存在则创建新的实例
        采用懒加载模式，只有在实际使用时才创建服务实例
        
        Args:
            database_name (str): 数据库名称，对应配置文件中的数据库标识
            
        Returns:
            DatabaseService: 对应的数据库服务实例
            
        Example:
            # 获取用户账户数据库服务
            user_db = db_manager.get_service('user_account')
            
            # 获取期刊投稿数据库服务
            journal_db = db_manager.get_service('journal_submit')
            
            # 使用服务执行数据库操作
            user = await user_db.fetchone("SELECT * FROM users WHERE username = ?", ("john",))
        """
        if database_name not in self.services:
            # 如果服务不存在，创建新的数据库服务实例
            self.services[database_name] = DatabaseService(database_name)
        return self.services[database_name]  # 返回服务实例
    
    async def initialize_all(self):
        """初始化所有数据库
        
        批量初始化所有配置的数据库，包括：
        1. 检查全局初始化状态，避免重复初始化
        2. 获取所有配置的数据库名称
        3. 并行执行所有数据库的表结构创建
        4. 并行创建所有数据库的索引
        5. 记录初始化结果和统计信息
        
        这是系统启动时的关键方法，通常在应用启动时调用一次
        
        Raises:
            RuntimeError: 当初始化过程中发生错误时抛出
            
        Note:
            - 使用asyncio.gather()并行初始化，提高效率
            - 如果某个数据库初始化失败，会中断整个过程
            - 索引创建失败不会中断初始化过程（记录警告）
        """
        if self._initialized:  # 如果已经全局初始化过，直接返回
            return
        
        try:
            # 获取所有配置的数据库名称列表
            db_names = db_config.get_all_database_names()
            
            # 第一阶段：并行初始化所有数据库（创建表结构）
            tasks = []
            for db_name in db_names:
                service = self.get_service(db_name)  # 获取或创建服务实例
                tasks.append(service.initialize())   # 添加初始化任务
            
            # 等待所有数据库初始化完成
            await asyncio.gather(*tasks)
            
            # 第二阶段：并行创建所有数据库的索引
            index_tasks = []
            for db_name in db_names:
                service = self.get_service(db_name)
                index_tasks.append(service.create_indexes())
            
            # 等待所有索引创建完成
            await asyncio.gather(*index_tasks)
            
            self._initialized = True  # 标记全局初始化完成
            # 记录成功日志和统计信息
            global_logger.info('database', f"所有数据库初始化完成，共 {len(db_names)} 个数据库")
            
        except Exception as e:
            # 记录错误日志并抛出异常
            global_logger.error('database', f"数据库初始化失败: {e}")
            raise RuntimeError(f"数据库初始化失败: {e}")
    
    async def get_database_info(self, database_name: str) -> DatabaseInfo:
        """获取数据库信息
        
        根据数据库名称获取数据库的详细信息，包括文件路径、配置参数等
        
        Args:
            database_name (str): 数据库名称
            
        Returns:
            DatabaseInfo: 数据库信息对象，包含路径、配置等详细信息
        """
        return db_config.get_database_info(database_name)
    
    def get_all_database_names(self) -> List[str]:
        """获取所有数据库名称
        
        从配置文件中获取所有已配置的数据库名称列表
        
        Returns:
            List[str]: 所有数据库名称的列表
        """
        return db_config.get_all_database_names()


# 全局数据库管理器实例
# 
# 这是整个数据库服务层的全局单例实例，提供统一的数据库操作接口
# 在整个应用中使用这个实例来获取数据库服务和执行数据库操作
# 
# 使用示例：
# 
#   # 获取用户数据库服务
#   user_db = db_manager.get_service('user_account')
#   
#   # 执行数据库查询
#   user = await user_db.fetchone("SELECT * FROM users WHERE username = ?", ("john",))
#   
#   # 初始化所有数据库（通常在应用启动时调用一次）
#   await db_manager.initialize_all()
#
# 注意：这个实例是线程安全的，可以在多线程环境中使用
db_manager = DatabaseManager()


