"""
编委会与决策记录相关表 ORM Model

表名：
- editorial_board：编委会成员表
- decision_records：编辑决策记录表
"""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.orm.base import Base


class EditorialBoard(Base):
    """
    编委会成员表
    
    记录所有编辑角色成员信息
    """
    __tablename__ = "editorial_board"

    board_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="编委 ID（自增）")
    user_uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), unique=True, nullable=False, comment="用户 ID")
    
    # 职位信息
    position: Mapped[str] = mapped_column(Text, nullable=False, comment="职位：editor/associate_editor/ea_ae")
    title: Mapped[str | None] = mapped_column(Text, nullable=True, comment="职称/头衔")
    
    # 领域信息
    research_areas: Mapped[str | None] = mapped_column(Text, nullable=True, comment="研究领域（逗号分隔）")
    
    # 任命信息
    appointed_at: Mapped[str] = mapped_column(Text, nullable=False, comment="任命时间（ISO 字符串）")
    appointed_by_uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False, comment="任命者用户 ID")
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, server_default="true", comment="是否在职")
    
    # 关联关系
    appointer: Mapped["User"] = relationship(foreign_keys=[appointed_by_uid], lazy="joined")


class DecisionRecord(Base):
    """
    编辑决策记录表
    
    记录稿件各阶段的编辑决策
    """
    __tablename__ = "decision_records"

    decision_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="决策 ID（自增）")
    manuscript_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("manuscripts.manuscript_id"), nullable=False, comment="稿件 ID")
    
    # 决策信息
    stage: Mapped[str] = mapped_column(Text, nullable=False, comment="决策阶段：initial_review/peer_review/final_decision")
    decision_type: Mapped[str] = mapped_column(Text, nullable=False, comment="决策类型：accept/reject/revision/transfer")
    
    # 决策内容
    decision_title: Mapped[str] = mapped_column(Text, nullable=False, comment="决策标题")
    decision_comments: Mapped[str] = mapped_column(Text, nullable=False, comment="决策意见")
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True, comment="建议")
    
    # 决策者信息
    decided_by_uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False, comment="决策者用户 ID")
    decided_at: Mapped[str] = mapped_column(Text, nullable=False, comment="决策时间（ISO 字符串）")
    
    # 关联关系
    manuscript: Mapped["Manuscript"] = relationship(lazy="joined")
    decider: Mapped["User"] = relationship(foreign_keys=[decided_by_uid], lazy="joined")


# 索引定义
Index("idx_editorial_board_user_uid", EditorialBoard.user_uid)
Index("idx_editorial_board_position", EditorialBoard.position)
Index("idx_editorial_board_is_active", EditorialBoard.is_active)

Index("idx_decision_records_manuscript_id", DecisionRecord.manuscript_id)
Index("idx_decision_records_stage", DecisionRecord.stage)
Index("idx_decision_records_decided_by_uid", DecisionRecord.decided_by_uid)
