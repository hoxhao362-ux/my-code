"""
用户通知仓库
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from database.orm.models.notification import Notification
from database.repositories.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationRepository(BaseRepository[Notification]):
    _pk_field = "notification_id"

    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    async def count_for_user(
        self,
        user_uid: int,
        *,
        is_read: bool | None = None,
        notification_type: str | None = None,
    ) -> int:
        conditions = [Notification.user_uid == user_uid]
        if is_read is not None:
            conditions.append(Notification.is_read == is_read)
        if notification_type:
            conditions.append(Notification.notification_type == notification_type)
        return await self.count(*conditions)

    async def list_page_for_user(
        self,
        user_uid: int,
        page: int,
        page_size: int,
        *,
        is_read: bool | None = None,
        notification_type: str | None = None,
    ) -> list[Notification]:
        conditions = [Notification.user_uid == user_uid]
        if is_read is not None:
            conditions.append(Notification.is_read == is_read)
        if notification_type:
            conditions.append(Notification.notification_type == notification_type)
        return await self.list_page(
            page,
            page_size,
            *conditions,
            order_by=Notification.created_at.desc(),
        )

    async def mark_read(
        self, notification_id: int, user_uid: int
    ) -> Notification | None:
        """将通知标为已读（须属于 user_uid）。已读则幂等返回当前行。"""
        n = await self.get_by_id(notification_id)
        if not n or n.user_uid != user_uid:
            return None
        if not n.is_read:
            n.is_read = True
            n.read_at = datetime.now()
        return n

    def to_item_dict(self, n: Notification) -> dict[str, Any]:
        return {
            "notification_id": n.notification_id,
            "title": n.title,
            "content": n.content,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "related_manuscript_id": n.related_manuscript_id,
            "related_url": n.related_url,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "read_at": n.read_at.isoformat() if n.read_at else None,
        }
