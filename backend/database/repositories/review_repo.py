"""
审稿记录仓库（兼容旧 ReviewRecord 模型）

提供审稿记录相关的数据库操作。
"""

from __future__ import annotations

from typing import Any, Dict

from database.orm.models.journal import Journal, ReviewRecord
from database.orm.models.user import User
from database.repositories.base_repo import BaseRepository
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ReviewRepository(BaseRepository[ReviewRecord]):
    """
    审稿记录仓库

    提供审稿记录的查询方法。
    主键字段为 rid。
    """

    _pk_field = "rid"

    def __init__(self, session: AsyncSession):
        super().__init__(session, ReviewRecord)

    # ------------------------------------------------------------------
    # 按审稿人查询
    # ------------------------------------------------------------------

    async def count_by_reviewer(self, reviewer_uid: int) -> int:
        """统计指定审稿人的审稿记录数"""
        return await self.count(ReviewRecord.reviewer_uid == reviewer_uid)

    async def count_by_reviewer_and_result(self, reviewer_uid: int, result: str) -> int:
        """统计指定审稿人特定结果的审稿记录数"""
        return await self.count(
            ReviewRecord.reviewer_uid == reviewer_uid,
            ReviewRecord.result == result,
        )

    async def list_history_page(
        self, reviewer_uid: int, page: int, page_size: int
    ) -> list[Dict[str, Any]]:
        """按审稿人分页查询审稿历史"""
        offset = (page - 1) * page_size
        rows = (
            (
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
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 被拒稿件
    # ------------------------------------------------------------------

    async def list_rejected_journals_page(
        self, page: int, page_size: int
    ) -> list[Dict[str, Any]]:
        """查询被拒稿件分页列表"""
        offset = (page - 1) * page_size
        rows = (
            (
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
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]

    async def count_rejected_journals(self) -> int:
        """统计被拒稿件数"""
        total = await self.session.scalar(
            select(func.count())
            .select_from(Journal)
            .where(Journal.status == "rejected")
        )
        return int(total or 0)

    # ------------------------------------------------------------------
    # 全量审稿记录
    # ------------------------------------------------------------------

    async def count_all_records(self) -> int:
        """统计所有审稿记录数"""
        return await self.count()

    async def list_all_records_page(
        self, page: int, page_size: int
    ) -> list[Dict[str, Any]]:
        """查询所有审稿记录分页列表（含文献和审稿人信息）"""
        offset = (page - 1) * page_size
        rows = (
            (
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
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def add_review_record(self, record: ReviewRecord) -> None:
        """添加审稿记录（兼容旧方法名）"""
        self.add(record)
