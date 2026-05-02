"""
用户通知表 ORM Model

表名：notifications
"""

from __future__ import annotations

from datetime import datetime

from database.orm.base import Base
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column


class Notification(Base):
    """站内消息通知，与 NotificationType 枚举取值一致。"""

    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="通知 ID（自增）"
    )
    user_uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="接收者用户 ID"
    )
    notification_type: Mapped[str] = mapped_column(
        Text, nullable=False, comment="通知类型（见 NotificationType）"
    )
    title: Mapped[str] = mapped_column(Text, nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="正文")
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", comment="是否已读"
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="已读时间"
    )
    related_manuscript_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="关联稿件 ID"
    )
    related_url: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="可选跳转链接"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )


Index("idx_notifications_user_uid", Notification.user_uid)
Index("idx_notifications_created_at", Notification.created_at)
Index("idx_notifications_user_unread", Notification.user_uid, Notification.is_read)
