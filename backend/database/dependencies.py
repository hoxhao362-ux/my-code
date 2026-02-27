"""
数据库依赖注入（FastAPI）

目的：
- 让 API 层通过 Depends 获取 AsyncSession；
- 避免在路由模块 import 时就创建/绑定数据库连接；
- 保持与 ServiceManager + lifespan 的生命周期一致。
"""

from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from database.service.database_service import db_manager


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    FastAPI 依赖：获取 AsyncSession。

    使用示例：
        @router.get(...)
        async def handler(session: AsyncSession = Depends(get_db_session)):
            ...
    """

    async with db_manager.get_session() as session:
        yield session

