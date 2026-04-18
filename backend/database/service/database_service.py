"""
数据库服务层 - 统一管理所有数据库操作（SQLAlchemy ORM 版）

本模块提供 SQLAlchemy 2.0 风格的异步 ORM 能力。

核心能力：
1. 异步 Engine + AsyncSession（高并发、连接池、参数化安全）
2. ORM Model 驱动的建表与索引同步（Base.metadata.create_all）
3. 统一的数据库生命周期管理（仍由 ServiceManager 托管 PostgreSQL 进程）

主要类：
- DatabaseManager: 全局数据库管理器，维护 Engine/Session 与服务生命周期。
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from core.service_manager import BaseManagedService
from database.orm import Base
from database.orm.session import (build_async_engine, build_sessionmaker,
                                  load_sqlalchemy_async_config)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker)
from utils.log import global_logger


class DatabaseManager(BaseManagedService):
    """
    数据库全局管理器
    实现 BaseManagedService 接口，负责连接池的生命周期与服务分发。
    """

    def __init__(self):
        super().__init__("database")
        self.engine: Optional[AsyncEngine] = None
        self.sessionmaker: Optional[async_sessionmaker] = None
        self._initialized = False

    async def start(self):
        """连接数据库：连接池初始化 -> 结构同步"""
        global_logger.info("Database", "正在连接数据库服务...")

        try:
            await self.initialize_all()
        except Exception as e:
            global_logger.error("Database", f"数据库服务连接失败: {e}")
            raise

    async def stop(self):
        """安全断开数据库连接"""
        global_logger.info("Database", "正在安全关闭数据库连接...")

        try:
            await self.close_all()
        except Exception as e:
            global_logger.error("Database", f"数据库关闭异常: {e}")

    async def _init_engine(self):
        """初始化 AsyncEngine（含重试检查机制）。"""

        if self.engine and self.sessionmaker:
            return

        cfg = load_sqlalchemy_async_config()
        self.engine = build_async_engine(cfg)
        self.sessionmaker = build_sessionmaker(self.engine)

        retry_count = 0
        max_retries = 30
        while retry_count < max_retries:
            try:
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return
            except Exception:
                retry_count += 1
                if retry_count >= max_retries:
                    global_logger.error(
                        "database", "数据库连接测试失败，已达到最大重试次数"
                    )
                    raise
                await asyncio.sleep(1)

    async def _create_schema(self):
        """
        根据 ORM Model 同步表结构与索引（create_all）。

        注意：生产环境应使用 Alembic 进行数据库迁移管理
        运行 `alembic upgrade head` 替代 create_all()
        create_all() 仅在开发环境使用，用于快速创建表结构
        """

        if not self.engine:
            raise RuntimeError("Engine 尚未初始化")

        # ================================================================
        # 数据库迁移说明
        # ================================================================
        # 生产环境请使用 Alembic 进行数据库迁移：
        #   cd backend
        #   alembic upgrade head
        #
        # 开发环境可以使用 create_all() 快速创建表结构：
        #   当前代码即为开发环境使用的自动建表逻辑
        #
        # 创建新的迁移脚本：
        #   alembic revision --autogenerate -m "描述信息"
        #
        # 查看迁移历史：
        #   alembic history
        # ================================================================

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        global_logger.info("database", "ORM 元数据同步完成（create_all）")

    async def initialize_all(self):
        """全量初始化：Engine 初始化 -> ORM 元数据同步"""
        if self._initialized:
            return

        try:
            await self._init_engine()
            await self._create_schema()

            self._initialized = True
            global_logger.info("database", "全量数据库环境初始化成功（SQLAlchemy ORM）")

        except Exception as e:
            global_logger.error("database", f"数据库环境初始化失败: {e}")
            raise RuntimeError("数据库环境初始化失败") from e

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """
        获取 AsyncSession（用于 FastAPI 依赖注入）。

        使用方式：
            async with db_manager.get_session() as session:
                ...
        """

        if not self.sessionmaker:
            raise RuntimeError(
                "数据库尚未初始化，请确保在 lifespan 启动后再获取 session。"
            )

        session = self.sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close_all(self):
        """彻底清理资源"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.sessionmaker = None
            self._initialized = False
            global_logger.info("database", "数据库 Engine 已销毁")


# 全局单例管理器
db_manager = DatabaseManager()
