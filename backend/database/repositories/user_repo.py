from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, uid: int) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.uid == uid))

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.username == username))

    async def username_exists(self, username: str) -> bool:
        uid = await self.session.scalar(select(User.uid).where(User.username == username))
        return uid is not None

    async def email_exists(self, email: str) -> bool:
        uid = await self.session.scalar(select(User.uid).where(User.email == email))
        return uid is not None

    async def get_public_fields_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        row = (
            await self.session.execute(
                select(
                    User.uid,
                    User.username,
                    User.email,
                    User.role,
                    User.is_verified,
                ).where(User.uid == uid)
            )
        ).mappings().first()
        return dict(row) if row else None

    async def get_profile_fields_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        row = (
            await self.session.execute(
                select(
                    User.uid,
                    User.username,
                    User.email,
                    User.role,
                    User.create_time,
                    User.last_login_time,
                    User.avatar_hash,
                ).where(User.uid == uid)
            )
        ).mappings().first()
        return dict(row) if row else None

    async def count(self, role: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(User)
        if role:
            stmt = stmt.where(User.role == role)
        total = await self.session.scalar(stmt)
        return int(total or 0)

    async def list_page(self, page: int, page_size: int, role: Optional[str] = None) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        stmt = select(
            User.uid,
            User.username,
            User.email,
            User.role,
            User.is_verified,
            User.create_time,
            User.last_login_time,
        )
        if role:
            stmt = stmt.where(User.role == role)
        rows = (
            await self.session.execute(
                stmt.order_by(User.create_time.desc()).limit(page_size).offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def role_breakdown(self) -> list[Dict[str, Any]]:
        rows = (await self.session.execute(select(User.role, func.count().label("count")).group_by(User.role))).mappings().all()
        return [dict(r) for r in rows]

    def add(self, user: User) -> None:
        self.session.add(user)

