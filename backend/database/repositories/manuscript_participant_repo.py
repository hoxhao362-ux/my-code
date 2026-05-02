"""
稿件参与者仓库（审稿人分配等）
"""

from __future__ import annotations

from datetime import datetime

from database.orm.models.manuscript import Manuscript, ManuscriptParticipant
from database.repositories.base_repo import BaseRepository
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class ManuscriptParticipantRepository(BaseRepository[ManuscriptParticipant]):
    _pk_field = "participant_id"

    def __init__(self, session: AsyncSession):
        super().__init__(session, ManuscriptParticipant)

    async def get_by_id(self, participant_id: int) -> ManuscriptParticipant | None:
        stmt = (
            select(ManuscriptParticipant)
            .where(ManuscriptParticipant.participant_id == participant_id)
            .options(joinedload(ManuscriptParticipant.manuscript))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def upsert_reviewer(
        self,
        manuscript_id: int,
        user_uid: int,
        assigned_by_uid: int,
    ) -> ManuscriptParticipant:
        """创建或更新审稿人参与记录（再次分配时重置完成时间）。"""
        existing = await self.session.scalar(
            select(ManuscriptParticipant).where(
                ManuscriptParticipant.manuscript_id == manuscript_id,
                ManuscriptParticipant.user_uid == user_uid,
                ManuscriptParticipant.role_type == "reviewer",
            )
        )
        now = datetime.now()
        if existing:
            existing.is_active = True
            existing.assigned_at = now
            existing.assigned_by_uid = assigned_by_uid
            existing.completed_at = None
            await self.session.flush()
            return existing
        row = ManuscriptParticipant(
            manuscript_id=manuscript_id,
            user_uid=user_uid,
            role_type="reviewer",
            assigned_at=now,
            assigned_by_uid=assigned_by_uid,
            is_active=True,
            completed_at=None,
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_active_reviewers_for_manuscript(
        self, manuscript_id: int
    ) -> list[ManuscriptParticipant]:
        stmt = select(ManuscriptParticipant).where(
            ManuscriptParticipant.manuscript_id == manuscript_id,
            ManuscriptParticipant.role_type == "reviewer",
            ManuscriptParticipant.is_active == True,  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all_by_manuscript_ordered(
        self, manuscript_id: int
    ) -> list[ManuscriptParticipant]:
        stmt = (
            select(ManuscriptParticipant)
            .where(ManuscriptParticipant.manuscript_id == manuscript_id)
            .order_by(ManuscriptParticipant.assigned_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def has_active_membership(
        self, manuscript_id: int, user_uid: int
    ) -> bool:
        """用户是否为该稿活跃参与者（任意角色）。"""
        n = await self.session.scalar(
            select(func.count())
            .select_from(ManuscriptParticipant)
            .where(
                ManuscriptParticipant.manuscript_id == manuscript_id,
                ManuscriptParticipant.user_uid == user_uid,
                ManuscriptParticipant.is_active == True,  # noqa: E712
            )
        )
        return int(n or 0) > 0

    async def count_by_reviewer_tasks(
        self,
        reviewer_uid: int,
        *,
        manuscript_status: str | None = None,
    ) -> int:
        """统计当前审稿人活跃任务数（可选按稿件状态过滤）。"""
        conditions = [
            ManuscriptParticipant.user_uid == reviewer_uid,
            ManuscriptParticipant.role_type == "reviewer",
            ManuscriptParticipant.is_active == True,  # noqa: E712
            Manuscript.is_deleted == False,  # noqa: E712
        ]
        if manuscript_status:
            conditions.append(Manuscript.status == manuscript_status)
        stmt = (
            select(func.count())
            .select_from(ManuscriptParticipant)
            .join(Manuscript, ManuscriptParticipant.manuscript_id == Manuscript.manuscript_id)
            .where(*conditions)
        )
        return int(await self.session.scalar(stmt) or 0)

    async def list_by_reviewer_page(
        self,
        reviewer_uid: int,
        page: int,
        page_size: int,
        *,
        manuscript_status: str | None = None,
    ) -> list[tuple[ManuscriptParticipant, Manuscript]]:
        conditions = [
            ManuscriptParticipant.user_uid == reviewer_uid,
            ManuscriptParticipant.role_type == "reviewer",
            ManuscriptParticipant.is_active == True,  # noqa: E712
            Manuscript.is_deleted == False,  # noqa: E712
        ]
        if manuscript_status:
            conditions.append(Manuscript.status == manuscript_status)
        offset = (page - 1) * page_size
        stmt = (
            select(ManuscriptParticipant, Manuscript)
            .join(Manuscript, ManuscriptParticipant.manuscript_id == Manuscript.manuscript_id)
            .where(*conditions)
            .order_by(ManuscriptParticipant.assigned_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        rows = (await self.session.execute(stmt)).all()
        return [(row[0], row[1]) for row in rows]
