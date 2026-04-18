"""已删除文献表 ORM Model

表名：deleted_journals
用途：存档软删除/删除原因等信息，便于审计与追溯。
"""
from __future__ import annotations

from datetime import datetime
import warnings
warnings.warn(
    "DeletedJournal 模型已废弃。软删除功能已迁移至 Manuscript.is_deleted 字段。保留仅为兼容旧数据。",
    DeprecationWarning,
    stacklevel=2,
)

from sqlalchemy import BigInteger, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


# ============================================================
# 数据迁移说明（TEXT → TIMESTAMP）
# 执行以下 SQL 将现有数据从 TEXT 转换为 TIMESTAMP：
#
# ALTER TABLE deleted_journals ALTER COLUMN delete_time TYPE TIMESTAMP USING delete_time::TIMESTAMP;
#
# 注意：执行前请备份数据库
# ============================================================


class DeletedJournal(Base):
    __tablename__ = "deleted_journals"

    jid: Mapped[int] = mapped_column(Integer, primary_key=True, comment="记录ID（自增）")
    original_jid: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="原文献ID（journals.jid）")
    uid: Mapped[int] = mapped_column(Integer, nullable=False, comment="投稿用户ID")

    title: Mapped[str] = mapped_column(Text, nullable=False, comment="标题")
    authors: Mapped[str] = mapped_column(Text, nullable=False, comment="作者列表（字符串）")

    file_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False, comment="文件哈希（唯一）")
    file_bucket: Mapped[str] = mapped_column(Text, nullable=False, comment="文件存储桶")
    file_name: Mapped[str] = mapped_column(Text, nullable=False, comment="原始文件名")
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="文件大小（字节）")

    abstract: Mapped[str | None] = mapped_column(Text, nullable=True, comment="摘要")
    delete_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="删除时间")
    delete_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="删除原因")

