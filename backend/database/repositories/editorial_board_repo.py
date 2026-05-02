"""
编委会数据访问
"""

from __future__ import annotations

from database.orm.models.editorial import EditorialBoard
from database.orm.models.user import User
from database.repositories.base_repo import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class EditorialBoardRepository(BaseRepository[EditorialBoard]):
    _pk_field = "board_id"

    def __init__(self, session: AsyncSession):
        super().__init__(session, EditorialBoard)

    async def count_board(
        self,
        *,
        position: str | None = None,
        is_active: bool | None = True,
    ) -> int:
        conditions = []
        if position:
            conditions.append(EditorialBoard.position == position)
        if is_active is not None:
            conditions.append(EditorialBoard.is_active == is_active)
        return await self.count(*conditions) if conditions else await self.count()

    async def list_board_page(
        self,
        page: int,
        page_size: int,
        *,
        position: str | None = None,
        is_active: bool | None = True,
    ) -> list[dict]:
        """分页返回编委 + 用户基础信息。"""
        offset = (page - 1) * page_size
        conditions = []
        if position:
            conditions.append(EditorialBoard.position == position)
        if is_active is not None:
            conditions.append(EditorialBoard.is_active == is_active)

        stmt = (
            select(
                EditorialBoard.board_id,
                EditorialBoard.user_uid,
                EditorialBoard.position,
                EditorialBoard.title,
                EditorialBoard.research_areas,
                EditorialBoard.appointed_at,
                EditorialBoard.is_active,
                User.username,
                User.email,
                User.role,
            )
            .join(User, EditorialBoard.user_uid == User.uid)
        )
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = (
            stmt.order_by(EditorialBoard.position.asc(), EditorialBoard.appointed_at.asc())
            .offset(offset)
            .limit(page_size)
        )
        rows = (await self.session.execute(stmt)).mappings().all()
        return [dict(r) for r in rows]

    async def get_by_user_uid(self, user_uid: int) -> EditorialBoard | None:
        return await self.session.scalar(
            select(EditorialBoard).where(EditorialBoard.user_uid == user_uid)
        )

    async def count_active(self) -> int:
        return await self.count(EditorialBoard.is_active == True)  # noqa: E712
