from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.journal import Journal
from database.orm.models.user import User


class JournalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, jid: int) -> Optional[Journal]:
        return await self.session.scalar(select(Journal).where(Journal.jid == jid))

    async def count_by_uploader(self, uid: int) -> int:
        total = await self.session.scalar(select(func.count()).select_from(Journal).where(Journal.uid == uid))
        return int(total or 0)

    async def list_by_uploader_page(self, uid: int, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where(Journal.uid == uid)
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_by_status(self, status: str) -> int:
        total = await self.session.scalar(select(func.count()).select_from(Journal).where(Journal.status == status))
        return int(total or 0)

    async def list_by_status_page(self, status: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where(Journal.status == status)
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_public(self) -> int:
        return await self.count_by_status("published")

    async def list_public_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        return await self.list_by_status_page("published", page, page_size)

    async def count_deleted(self) -> int:
        total = await self.session.scalar(select(func.count()).select_from(Journal).where(Journal.status == "deleted"))
        return int(total or 0)

    async def list_deleted_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time,
                    Journal.update_time,
                    Journal.uid,
                )
                .where(Journal.status == "deleted")
                .order_by(Journal.update_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_all(self, status: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(Journal)
        if status:
            stmt = stmt.where(Journal.status == status)
        total = await self.session.scalar(stmt)
        return int(total or 0)

    async def list_all_with_uploader_page(self, page: int, page_size: int, status: Optional[str] = None) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        stmt = (
            select(
                Journal.jid,
                Journal.title,
                Journal.authors,
                Journal.abstract,
                Journal.status,
                Journal.file_name,
                Journal.file_size,
                Journal.create_time,
                Journal.update_time,
                User.username.label("uploader"),
            )
            .join(User, Journal.uid == User.uid)
        )
        if status:
            stmt = stmt.where(Journal.status == status)
        rows = (await self.session.execute(stmt.order_by(Journal.create_time.desc()).limit(page_size).offset(offset))).mappings().all()
        return [dict(r) for r in rows]

    async def list_deleted_with_uploader_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time,
                    Journal.update_time,
                    User.username.label("uploader"),
                )
                .join(User, Journal.uid == User.uid)
                .where(Journal.status == "deleted")
                .order_by(Journal.update_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def status_breakdown(self) -> list[Dict[str, Any]]:
        rows = (await self.session.execute(select(Journal.status, func.count().label("count")).group_by(Journal.status))).mappings().all()
        return [dict(r) for r in rows]

    async def count_search_title_or_abstract(self, keyword: str) -> int:
        like_kw = f"%{keyword}%"
        total = await self.session.scalar(
            select(func.count())
            .select_from(Journal)
            .where((Journal.title.like(like_kw) | Journal.abstract.like(like_kw)) & (Journal.status != "deleted"))
        )
        return int(total or 0)

    async def list_search_title_or_abstract_page(self, keyword: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        like_kw = f"%{keyword}%"
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where((Journal.title.like(like_kw) | Journal.abstract.like(like_kw)) & (Journal.status != "deleted"))
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_search_author(self, keyword: str) -> int:
        like_kw = f"%{keyword}%"
        total = await self.session.scalar(
            select(func.count()).select_from(Journal).where((Journal.authors.like(like_kw)) & (Journal.status != "deleted"))
        )
        return int(total or 0)

    async def list_search_author_page(self, keyword: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        like_kw = f"%{keyword}%"
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where((Journal.authors.like(like_kw)) & (Journal.status != "deleted"))
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_search_subject(self, subject: str) -> int:
        total = await self.session.scalar(
            select(func.count()).select_from(Journal).where((Journal.subject == subject) & (Journal.status != "deleted"))
        )
        return int(total or 0)

    async def list_search_subject_page(self, subject: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where((Journal.subject == subject) & (Journal.status != "deleted"))
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    def add(self, journal: Journal) -> None:
        self.session.add(journal)

