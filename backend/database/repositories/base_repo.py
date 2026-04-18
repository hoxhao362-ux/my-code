"""
仓库基类

提供通用的 CRUD 操作，所有具体仓库应继承此基类并指定模型类型。
子类可通过设置 _pk_field 类属性指定主键字段名（默认 "id"）。
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    仓库基类，提供通用的 CRUD 操作。

    用法示例：
        class UserRepository(BaseRepository[User]):
            _pk_field = "uid"

            def __init__(self, session: AsyncSession):
                super().__init__(session, User)

    子类可覆盖 _pk_field 以指定主键字段名，也可直接向 get_by_id()
    传入 id_field 参数临时覆盖。
    """

    _pk_field: str = "id"

    def __init__(self, session: AsyncSession, model_class: type[T]):
        self.session = session
        self._model_class = model_class

    # ------------------------------------------------------------------
    # 读取
    # ------------------------------------------------------------------

    async def get_by_id(
        self, id_value: int, id_field: str | None = None
    ) -> Optional[T]:
        """
        根据主键获取单条记录。

        Args:
            id_value: 主键值
            id_field: 主键字段名，为 None 时使用类属性 _pk_field
        """
        field = id_field or self._pk_field
        column = getattr(self._model_class, field, None)
        if column is None:
            raise ValueError(f"模型 {self._model_class.__name__} 不存在字段 {field}")
        return await self.session.scalar(
            select(self._model_class).where(column == id_value)
        )

    # ------------------------------------------------------------------
    # 统计
    # ------------------------------------------------------------------

    async def count(self, *conditions) -> int:
        """
        按条件统计记录数。

        Args:
            *conditions: SQLAlchemy 查询条件（可选）

        Returns:
            int: 符合条件的记录数
        """
        stmt = select(func.count()).select_from(self._model_class)
        if conditions:
            stmt = stmt.where(*conditions)
        total = await self.session.scalar(stmt)
        return int(total or 0)

    # ------------------------------------------------------------------
    # 分页
    # ------------------------------------------------------------------

    async def list_page(
        self,
        page: int,
        page_size: int,
        *conditions,
        order_by=None,
    ) -> List[T]:
        """
        分页查询，返回 ORM 对象列表。

        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            *conditions: SQLAlchemy 查询条件
            order_by: 排序字段

        Returns:
            List[T]: ORM 对象列表
        """
        offset = (page - 1) * page_size
        stmt = select(self._model_class)
        if conditions:
            stmt = stmt.where(*conditions)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.limit(page_size).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_page_as_dict(
        self,
        page: int,
        page_size: int,
        *columns,
        conditions=None,
        order_by=None,
        joins=None,
    ) -> List[Dict[str, Any]]:
        """
        分页查询，返回字典列表（指定列投影）。

        当需要只查询部分列或联表查询时使用此方法。

        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            *columns: 要查询的列（SQLAlchemy Column 对象）
            conditions: 查询条件列表
            order_by: 排序字段
            joins: 联表配置列表，每项为 (target, on_clause) 元组

        Returns:
            List[Dict[str, Any]]: 字典列表
        """
        offset = (page - 1) * page_size
        stmt = select(*columns) if columns else select(self._model_class)

        # 处理联表
        if joins:
            for target, on_clause in joins:
                stmt = stmt.join(target, on_clause)

        if conditions:
            stmt = stmt.where(*conditions)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.limit(page_size).offset(offset)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def add(self, entity: T) -> None:
        """添加实体到会话"""
        self.session.add(entity)
