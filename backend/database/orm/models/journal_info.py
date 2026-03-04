"""
文献信息扩展表 ORM Model

表名：journal_info
用途：存储期数、出版信息、DOI 等扩展字段。
"""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


class JournalInfo(Base):
    __tablename__ = "journal_info"

    info_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="信息ID（自增）")
    jid: Mapped[int] = mapped_column(BigInteger, ForeignKey("journals.jid"), nullable=False, comment="文献ID")

    issue_number: Mapped[str] = mapped_column(Text, nullable=False, comment="期号（业务字段）")
    publication_date: Mapped[str] = mapped_column(Text, nullable=False, comment="出版日期（ISO字符串）")

    volume: Mapped[str | None] = mapped_column(Text, nullable=True, comment="卷")
    issue: Mapped[str | None] = mapped_column(Text, nullable=True, comment="期")
    journal_type: Mapped[str | None] = mapped_column(Text, nullable=True, comment="期刊类型")
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True, comment="关键词（字符串）")
    doi: Mapped[str | None] = mapped_column(Text, nullable=True, comment="DOI")

