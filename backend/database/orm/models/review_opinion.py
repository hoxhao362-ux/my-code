"""
审稿意见表 ORM Model

表名：review_opinions
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


# ============================================================
# 数据迁移说明（TEXT → TIMESTAMP）
# 执行以下 SQL 将现有数据从 TEXT 转换为 TIMESTAMP：
#
# ALTER TABLE review_opinions ALTER COLUMN submitted_at TYPE TIMESTAMP USING submitted_at::TIMESTAMP;
#
# 注意：执行前请备份数据库
# ============================================================


class ReviewOpinion(Base):
    __tablename__ = "review_opinions"

    opinion_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="意见ID（自增）")
    manuscript_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("manuscripts.manuscript_id"), nullable=False, comment="稿件ID")
    reviewer_uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False, comment="审稿人用户ID")

    stage: Mapped[str] = mapped_column(Text, nullable=False, comment="审稿阶段：initial_review/peer_review/final_decision")
    review_round: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", comment="审稿轮次")
    review_score: Mapped[int] = mapped_column(Integer, nullable=False, comment="评分")
    review_comments: Mapped[str] = mapped_column(Text, nullable=False, comment="审稿意见")
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True, comment="建议")
    decision: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审稿结论：accept/reject/revision")
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="提交时间")


Index("idx_review_opinions_manuscript_id", ReviewOpinion.manuscript_id)
Index("idx_review_opinions_reviewer_uid", ReviewOpinion.reviewer_uid)

