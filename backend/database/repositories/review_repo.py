from __future__ import annotations

from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.journal import Journal, ReviewRecord
from database.orm.models.user import User


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_by_reviewer(self, reviewer_uid: int) -> int:
        total = await self.session.scalar(
            select(func.count()).select_from(ReviewRecord).where(ReviewRecord.reviewer_uid == reviewer_uid)
        )
        return int(total or 0)

    async def count_by_reviewer_and_result(self, reviewer_uid: int, result: str) -> int:
        total = await self.session.scalar(
            select(func.count())
            .select_from(ReviewRecord)
            .where(ReviewRecord.reviewer_uid == reviewer_uid, ReviewRecord.result == result)
        )
        return int(total or 0)

    async def list_history_page(self, reviewer_uid: int, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    ReviewRecord.rid,
                    ReviewRecord.jid,
                    ReviewRecord.reviewer_uid,
                    ReviewRecord.review_time,
                    ReviewRecord.result,
                    ReviewRecord.comment,
                    Journal.title,
                    Journal.authors,
                    Journal.status,
                )
                .join(Journal, ReviewRecord.jid == Journal.jid)
                .where(ReviewRecord.reviewer_uid == reviewer_uid)
                .order_by(ReviewRecord.review_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def list_rejected_journals_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.uid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time,
                    Journal.update_time,
                    ReviewRecord.comment,
                    ReviewRecord.review_time,
                )
                .join(ReviewRecord, Journal.jid == ReviewRecord.jid)
                .where(Journal.status == "rejected")
                .order_by(Journal.update_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_rejected_journals(self) -> int:
        total = await self.session.scalar(select(func.count()).select_from(Journal).where(Journal.status == "rejected"))
        return int(total or 0)

    async def count_all_records(self) -> int:
        total = await self.session.scalar(select(func.count()).select_from(ReviewRecord))
        return int(total or 0)

    async def list_all_records_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    ReviewRecord.rid,
                    ReviewRecord.jid,
                    ReviewRecord.reviewer_uid,
                    ReviewRecord.review_time,
                    ReviewRecord.result,
                    ReviewRecord.comment,
                    Journal.title,
                    User.username.label("reviewer_name"),
                )
                .join(Journal, ReviewRecord.jid == Journal.jid)
                .join(User, ReviewRecord.reviewer_uid == User.uid)
                .order_by(ReviewRecord.review_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    def add_review_record(self, record: ReviewRecord) -> None:
        self.session.add(record)

