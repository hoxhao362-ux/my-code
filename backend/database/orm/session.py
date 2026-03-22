"""
SQLAlchemy AsyncEngine / AsyncSession 工厂

负责：
- 从项目配置构建异步 Engine
- 生成 async_sessionmaker
- 提供统一的连接池参数

注意：
本模块不启动/停止 PostgreSQL 进程；进程托管仍由 DatabaseManager 负责。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from core.config import config
from utils.log import global_logger


@dataclass(frozen=True)
class SqlAlchemyAsyncConfig:
    """SQLAlchemy 异步引擎配置（从项目配置系统抽取后规范化）。"""

    host: str
    port: int
    database: str
    user: str
    password: Optional[str]

    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 1800


def load_sqlalchemy_async_config() -> SqlAlchemyAsyncConfig:
    """从项目配置加载 SQLAlchemy 异步连接信息。"""

    env = config.get("global.global.env", "dev")
    host_key = f"database.database.database_host_{env}"
    host = config.get(host_key, "localhost")
    port = int(config["database.database.database_port"])
    user = config["database.database.database_user"]
    database = config["database.database.database_name"]

    password = config.get("database.database.database_password")
    if password is None or (isinstance(password, float) and password != password):
        password = None

    return SqlAlchemyAsyncConfig(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
    )


def build_async_engine(cfg: SqlAlchemyAsyncConfig) -> AsyncEngine:
    """
    构建 SQLAlchemy AsyncEngine。

    选择 postgresql+asyncpg：
    - asyncpg 性能高、生态成熟；
    - SQLAlchemy 是主流、稳定、可维护的 ORM；
    - 与 FastAPI 的异步模式天然契合。
    """

    url = URL.create(
        drivername="postgresql+asyncpg",
        username=cfg.user,
        password=cfg.password,
        host=cfg.host,
        port=cfg.port,
        database=cfg.database,
    )

    engine = create_async_engine(
        url,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_timeout=cfg.pool_timeout,
        pool_recycle=cfg.pool_recycle,
        pool_pre_ping=True,
        echo=False,
        future=True,
    )

    global_logger.info(
        "Database",
        f"SQLAlchemy AsyncEngine 就绪: {cfg.host}:{cfg.port}/{cfg.database} (pool_size={cfg.pool_size}, max_overflow={cfg.max_overflow})",
    )
    return engine


def build_sessionmaker(engine: AsyncEngine) -> async_sessionmaker:
    """构建 AsyncSession 工厂。"""

    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

