"""
审稿意见仓库
"""

from __future__ import annotations

from datetime import datetime

from database.orm.models.review_opinion import ReviewOpinion
from database.repositories.base_repo import BaseRepository
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ReviewOpinionRepository(BaseRepository[ReviewOpinion]):
    _pk_field = "opinion_id"

    def __init__(self, session: AsyncSession):
        super().__init__(session, ReviewOpinion)

    async def exists_for_round(
        self, manuscript_id: int, reviewer_uid: int, review_round: int
    ) -> bool:
        sid = await self.session.scalar(
            select(ReviewOpinion.opinion_id).where(
                ReviewOpinion.manuscript_id == manuscript_id,
                ReviewOpinion.reviewer_uid == reviewer_uid,
                ReviewOpinion.review_round == review_round,
            )
        )
        return sid is not None

    async def insert(
        self,
        *,
        manuscript_id: int,
        reviewer_uid: int,
        stage: str,
        review_round: int,
        review_score: int,
        review_comments: str,
        recommendations: str | None,
        decision: str | None,
    ) -> ReviewOpinion:
        row = ReviewOpinion(
            manuscript_id=manuscript_id,
            reviewer_uid=reviewer_uid,
            stage=stage,
            review_round=review_round,
            review_score=review_score,
            review_comments=review_comments,
            recommendations=recommendations,
            decision=decision,
            submitted_at=datetime.now(),
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_by_manuscript(self, manuscript_id: int) -> list[ReviewOpinion]:
        stmt = (
            select(ReviewOpinion)
            .where(ReviewOpinion.manuscript_id == manuscript_id)
            .order_by(ReviewOpinion.submitted_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def stats_for_reviewers(
        self, reviewer_uids: list[int]
    ) -> dict[int, dict[str, float | int]]:
        """批量统计审稿量与平均分。uids 为空返回 {}。"""
        if not reviewer_uids:
            return {}
        stmt = (
            select(
                ReviewOpinion.reviewer_uid,
                func.count(ReviewOpinion.opinion_id),
                func.avg(ReviewOpinion.review_score),
            )
            .where(ReviewOpinion.reviewer_uid.in_(reviewer_uids))
            .group_by(ReviewOpinion.reviewer_uid)
        )
        rows = (await self.session.execute(stmt)).all()
        out: dict[int, dict[str, float | int]] = {}
        for uid, cnt, avg in rows:
            out[int(uid)] = {
                "total_reviews": int(cnt),
                "average_score": float(avg) if avg is not None else 0.0,
            }
        return out
