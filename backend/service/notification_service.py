"""
通知写入服务：在业务流程中创建站内通知，并打日志。
"""

from __future__ import annotations

from datetime import datetime

from database.orm.models.notification import Notification
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import global_logger


async def create_notification(
    session: AsyncSession,
    *,
    user_uid: int,
    notification_type: str,
    title: str,
    content: str,
    related_manuscript_id: int | None = None,
    related_url: str | None = None,
    log_tag: str = "Notification",
) -> Notification:
    """创建一条通知（调用方负责在同一事务中 commit/flush）。"""
    row = Notification(
        user_uid=user_uid,
        notification_type=notification_type,
        title=title,
        content=content,
        is_read=False,
        read_at=None,
        related_manuscript_id=related_manuscript_id,
        related_url=related_url,
        created_at=datetime.now(),
    )
    session.add(row)
    await session.flush()
    global_logger.debug(
        log_tag,
        f"创建通知 id={row.notification_id} uid={user_uid} type={notification_type}",
    )
    return row
