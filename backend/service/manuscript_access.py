"""
稿件访问权限：作者、编辑部、活跃参与者。
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import UserRole
from database.orm.models.manuscript import Manuscript
from database.repositories.manuscript_participant_repo import (
    ManuscriptParticipantRepository,
)

# 编辑部侧默认可查看稿件正文的角色（无需出现在 participants 表）
_EDITORIAL_VIEW_ROLES: frozenset[str] = frozenset(
    {
        UserRole.ADMIN.value,
        UserRole.EDITOR.value,
        UserRole.ASSOCIATE_EDITOR.value,
        UserRole.EA_AE.value,
    }
)


async def user_can_view_manuscript(
    session: AsyncSession,
    manuscript: Manuscript,
    user_uid: int,
    role: str,
) -> bool:
    if manuscript.author_uid == user_uid:
        return True
    if role in _EDITORIAL_VIEW_ROLES:
        return True
    part = ManuscriptParticipantRepository(session)
    return await part.has_active_membership(manuscript.manuscript_id, user_uid)


async def user_can_upload_manuscript_file(
    manuscript: Manuscript,
    user_uid: int,
    role: str,
    file_type: str,
) -> bool:
    """上传附件：作者可传 main/attachment；审稿人可传 review/letter；编辑部可传 other。"""
    if role in _EDITORIAL_VIEW_ROLES:
        return True
    if manuscript.author_uid == user_uid:
        return file_type in ("main", "attachment", "other")
    if UserRole.get_role_level(role) >= UserRole.get_role_level(UserRole.REVIEWER.value):
        return file_type in ("review", "letter", "attachment", "other")
    return False
