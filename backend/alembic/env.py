"""
Alembic 迁移环境配置

本文件配置 Alembic 迁移环境，支持异步 PostgreSQL 连接。
数据库连接字符串从项目配置系统动态获取。
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ============================================================================
# 添加项目根目录到 Python 路径
# ============================================================================
# 获取当前文件所在目录 (backend/alembic/)
current_dir = Path(__file__).parent
# 获取 backend 目录
backend_dir = current_dir.parent
# 添加到 Python 路径
sys.path.insert(0, str(backend_dir))

# ============================================================================
# 导入项目配置和 ORM Base
# ============================================================================
from core.config import config as app_config
from database.orm import Base
from database.orm import models  # 确保所有模型已注册到 Base.metadata

# ============================================================================
# Alembic 配置对象
# ============================================================================
config = context.config

# ============================================================================
# 配置日志（如果配置文件存在）
# ============================================================================
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ============================================================================
# 目标元数据（用于迁移）
# ============================================================================
target_metadata = Base.metadata


# ============================================================================
# 数据库连接字符串构建函数
# ============================================================================
def get_database_url() -> str:
    """
    从项目配置系统构建数据库连接 URL
    
    返回格式: postgresql+asyncpg://user:password@host:port/database
    """
    # 获取环境
    env = app_config.get("global.global.env", "dev")
    
    # 根据环境选择主机
    host_key = f"database.database.database_host_{env}"
    host = app_config.get(host_key, "localhost")
    
    # 获取其他连接参数
    port = int(app_config.get("database.database.database_port", 5432))
    user = app_config.get("database.database.database_user", "postgres")
    database = app_config.get("database.database.database_name", "journal_platform")
    
    # 获取密码（优先从环境变量，其次从配置）
    password = app_config.get("database.database.database_password")
    if password is None or (isinstance(password, str) and "${" in password):
        password = os.environ.get("PG_PWD")
    
    # 构建 URL
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )
    
    return str(url)


def get_sync_database_url() -> str:
    """
    获取同步版本的数据库连接 URL（用于离线模式）
    
    返回格式: postgresql://user:password@host:port/database
    """
    async_url = get_database_url()
    # 将异步驱动替换为同步驱动
    return async_url.replace("postgresql+asyncpg", "postgresql")


# ============================================================================
# 离线模式迁移
# ============================================================================
def run_migrations_offline() -> None:
    """
    离线模式运行迁移
    
    在离线模式下，Alembic 直接生成 SQL 脚本而不需要连接到数据库。
    适用于生成 SQL 文件供 DBA 执行的场景。
    """
    # 使用同步 URL（离线模式不需要实际连接）
    url = get_sync_database_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 比较列类型变化
        compare_server_default=True,  # 比较默认值变化
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================================
# 在线模式迁移（异步支持）
# ============================================================================
def do_run_migrations(connection) -> None:
    """
    执行实际的迁移操作
    
    Args:
        connection: 数据库连接对象
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # 比较列类型变化
        compare_server_default=True,  # 比较默认值变化
        include_schemas=True,  # 包含 schema 信息
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    异步方式运行迁移
    
    创建异步引擎并执行迁移操作。
    """
    # 获取数据库 URL
    database_url = get_database_url()
    
    # 创建异步引擎
    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,  # 迁移时不使用连接池
        future=True,
    )
    
    try:
        # 使用异步连接执行迁移
        async with connectable.connect() as connection:
            # 在同步上下文中运行迁移
            await connection.run_sync(do_run_migrations)
    finally:
        # 确保引擎被正确释放
        await connectable.dispose()


def run_migrations_online() -> None:
    """
    在线模式运行迁移
    
    连接到数据库并执行迁移操作。
    这是生产环境使用的标准模式。
    """
    # 运行异步迁移
    asyncio.run(run_async_migrations())


# ============================================================================
# 入口点：根据配置选择运行模式
# ============================================================================
if context.is_offline_mode():
    print("运行离线模式迁移...")
    run_migrations_offline()
else:
    print("运行在线模式迁移...")
    run_migrations_online()
