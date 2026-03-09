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
import os
from contextlib import asynccontextmanager
from typing import Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from utils.log import global_logger
from core.config import config
from core.service_manager import BaseManagedService
from database.orm import Base
from database.orm import models as _models
from database.orm.session import build_async_engine, build_sessionmaker, load_sqlalchemy_async_config


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
        """定制化启动：环境变量配置 -> 进程启动 -> 连接池初始化 -> 结构同步"""
        global_logger.info("Database", "启动数据库托管服务...")
        
        exe_path = config["database.database.database_service_path"]
        args = await self._check_args(config["database.database.database_service_args"])
        db_dir = config["database.database.database_dir"]
        
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
        
        exe_path = config["database.database.database_service_path"]
        db_dir = config["database.database.database_dir"]
        
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
                    global_logger.error("database", "数据库连接测试失败，已达到最大重试次数")
                    raise
                await asyncio.sleep(1)

    async def _create_schema(self):
        """根据 ORM Model 同步表结构与索引（create_all）。"""

        if not self.engine:
            raise RuntimeError("Engine 尚未初始化")

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
            global_logger.error('database', f"数据库环境初始化失败: {e}")
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
            raise RuntimeError("数据库尚未初始化，请确保在 lifespan 启动后再获取 session。")

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
