"""
文献投稿相关表 ORM Model

表名：
- journals：投稿主表
- review_records：审核记录表
"""

from __future__ import annotations

import warnings
from datetime import datetime

warnings.warn(
    "Journal 和 ReviewRecord 模型已废弃，请使用 Manuscript 相关模型。保留仅为兼容旧数据。",
    DeprecationWarning,
    stacklevel=2,
)

from database.orm.base import Base
from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

# ============================================================
# 数据迁移说明（TEXT → TIMESTAMP）
# 执行以下 SQL 将现有数据从 TEXT 转换为 TIMESTAMP：
#
# ALTER TABLE journals ALTER COLUMN create_time TYPE TIMESTAMP USING create_time::TIMESTAMP;
# ALTER TABLE journals ALTER COLUMN update_time TYPE TIMESTAMP USING update_time::TIMESTAMP;
# ALTER TABLE review_records ALTER COLUMN review_time TYPE TIMESTAMP USING review_time::TIMESTAMP;
#
# 注意：执行前请备份数据库
# ============================================================


class Journal(Base):
    __tablename__ = "journals"

    jid: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, comment="文献ID（自增，BIGSERIAL）"
    )
    uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="投稿用户ID"
    )

    title: Mapped[str] = mapped_column(Text, nullable=False, comment="标题")
    authors: Mapped[str] = mapped_column(
        Text, nullable=False, comment="作者列表（字符串）"
    )
    subject: Mapped[str] = mapped_column(Text, nullable=False, comment="学科/主题")

    file_hash: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, comment="文件哈希（唯一）"
    )
    file_bucket: Mapped[str] = mapped_column(Text, nullable=False, comment="文件存储桶")
    file_name: Mapped[str] = mapped_column(Text, nullable=False, comment="原始文件名")
    file_size: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="文件大小（字节）"
    )

    abstract: Mapped[str | None] = mapped_column(Text, nullable=True, comment="摘要")
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="uploading", comment="状态"
    )

    create_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    update_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="更新时间"
    )


class ReviewRecord(Base):
    __tablename__ = "review_records"

    rid: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, comment="审核记录ID（自增，BIGSERIAL）"
    )
    jid: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("journals.jid"), nullable=False, comment="文献ID"
    )
    reviewer_uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="审核人用户ID"
    )

    review_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="审核时间"
    )
    result: Mapped[str] = mapped_column(Text, nullable=False, comment="审核结果")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审核意见")


Index("idx_journals_uid", Journal.uid)
Index("idx_journals_file_hash", Journal.file_hash)
Index("idx_journals_status", Journal.status)
Index("idx_review_records_jid", ReviewRecord.jid)
Index("idx_review_records_reviewer_uid", ReviewRecord.reviewer_uid)
