from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.invitation import InvitationCode


class InvitationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_code(self, code: str, for_update: bool = False) -> Optional[InvitationCode]:
        stmt = select(InvitationCode).where(InvitationCode.code == code)
        if for_update:
            stmt = stmt.with_for_update()
        return await self.session.scalar(stmt)

    async def count(self, status: Optional[str] = None, role: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(InvitationCode)
        if status:
            stmt = stmt.where(InvitationCode.status == status)
        if role:
            stmt = stmt.where(InvitationCode.role == role)
        total = await self.session.scalar(stmt)
        return int(total or 0)

    async def list_page(self, page: int, page_size: int, status: Optional[str] = None, role: Optional[str] = None) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        stmt = select(InvitationCode)
        if status:
            stmt = stmt.where(InvitationCode.status == status)
        if role:
            stmt = stmt.where(InvitationCode.role == role)
        rows = (
            await self.session.execute(stmt.order_by(InvitationCode.create_time.desc()).limit(page_size).offset(offset))
        ).scalars().all()
        return [
            {
                "code": r.code,
                "role": r.role,
                "status": r.status,
                "max_uses": r.max_uses,
                "used_count": r.used_count,
                "description": r.description,
                "created_by": r.created_by,
                "created_by_uid": r.created_by_uid,
                "create_time": r.create_time,
                "expire_time": r.expire_time,
            }
            for r in rows
        ]

    def add(self, invitation: InvitationCode) -> None:
        self.session.add(invitation)

