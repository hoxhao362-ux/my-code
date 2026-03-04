"""
审稿意见表 ORM Model

表名：review_opinions
"""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


class ReviewOpinion(Base):
    __tablename__ = "review_opinions"

    opinion_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="意见ID（自增）")
    jid: Mapped[int] = mapped_column(BigInteger, ForeignKey("journals.jid"), nullable=False, comment="文献ID")
    reviewer_uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False, comment="审稿人用户ID")

    review_round: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", comment="审稿轮次")
    review_score: Mapped[int] = mapped_column(Integer, nullable=False, comment="评分")
    review_comments: Mapped[str] = mapped_column(Text, nullable=False, comment="审稿意见")
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True, comment="建议")
    submitted_at: Mapped[str] = mapped_column(Text, nullable=False, comment="提交时间（ISO字符串）")

