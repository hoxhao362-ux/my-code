"""新增 notifications 表

Revision ID: 002
Revises: 001
Create Date: 2026-05-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column(
            "notification_id",
            sa.Integer(),
            nullable=False,
            comment="通知 ID（自增）",
        ),
        sa.Column(
            "user_uid",
            sa.Integer(),
            nullable=False,
            comment="接收者用户 ID",
        ),
        sa.Column(
            "notification_type",
            sa.Text(),
            nullable=False,
            comment="通知类型（见 NotificationType）",
        ),
        sa.Column("title", sa.Text(), nullable=False, comment="标题"),
        sa.Column("content", sa.Text(), nullable=False, comment="正文"),
        sa.Column(
            "is_read",
            sa.Boolean(),
            server_default="false",
            nullable=False,
            comment="是否已读",
        ),
        sa.Column("read_at", sa.DateTime(), nullable=True, comment="已读时间"),
        sa.Column(
            "related_manuscript_id",
            sa.BigInteger(),
            nullable=True,
            comment="关联稿件 ID",
        ),
        sa.Column("related_url", sa.Text(), nullable=True, comment="可选跳转链接"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.ForeignKeyConstraint(
            ["user_uid"],
            ["users.uid"],
            name="fk_notifications_user_uid_users",
        ),
        sa.PrimaryKeyConstraint("notification_id", name="pk_notifications"),
    )
    op.create_index(
        "idx_notifications_user_uid",
        "notifications",
        ["user_uid"],
    )
    op.create_index(
        "idx_notifications_created_at",
        "notifications",
        ["created_at"],
    )
    op.create_index(
        "idx_notifications_user_unread",
        "notifications",
        ["user_uid", "is_read"],
    )


def downgrade() -> None:
    op.drop_index("idx_notifications_user_unread", table_name="notifications")
    op.drop_index("idx_notifications_created_at", table_name="notifications")
    op.drop_index("idx_notifications_user_uid", table_name="notifications")
    op.drop_table("notifications")
