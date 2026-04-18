"""
稿件投稿相关表 ORM Model

表名：
- manuscripts：稿件主表
- manuscript_versions：稿件版本表
- manuscript_participants：稿件参与者表
- manuscript_files：稿件附件表

说明：
时间字段已从 TEXT 迁移为 PostgreSQL 原生 DateTime (TIMESTAMP) 类型，
提升查询性能与规范性。写入时直接传 datetime 对象即可。
"""

from __future__ import annotations

from datetime import datetime

from database.orm.base import Base
from sqlalchemy import (BigInteger, Boolean, DateTime, ForeignKey, Index,
                        Integer, Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

# ============================================================
# 数据迁移说明（TEXT → TIMESTAMP）
# 执行以下 SQL 将现有数据从 TEXT 转换为 TIMESTAMP：
#
# ALTER TABLE manuscripts ALTER COLUMN create_time TYPE TIMESTAMP USING create_time::TIMESTAMP;
# ALTER TABLE manuscripts ALTER COLUMN update_time TYPE TIMESTAMP USING update_time::TIMESTAMP;
# ALTER TABLE manuscripts ALTER COLUMN deleted_at TYPE TIMESTAMP USING deleted_at::TIMESTAMP;
# ALTER TABLE manuscript_versions ALTER COLUMN submitted_at TYPE TIMESTAMP USING submitted_at::TIMESTAMP;
# ALTER TABLE manuscript_participants ALTER COLUMN assigned_at TYPE TIMESTAMP USING assigned_at::TIMESTAMP;
# ALTER TABLE manuscript_participants ALTER COLUMN completed_at TYPE TIMESTAMP USING completed_at::TIMESTAMP;
# ALTER TABLE manuscript_files ALTER COLUMN uploaded_at TYPE TIMESTAMP USING uploaded_at::TIMESTAMP;
#
# 注意：执行前请备份数据库
# ============================================================


class Manuscript(Base):
    """
    稿件主表

    核心字段：
    - stage: 流转阶段（initial_review/peer_review/final_decision）
    - status: 全局状态（28 个状态值之一）
    - version: 当前版本号
    """

    __tablename__ = "manuscripts"

    manuscript_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, comment="稿件 ID（自增，BIGSERIAL）"
    )
    author_uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="投稿作者用户 ID"
    )

    # 基本信息
    title: Mapped[str] = mapped_column(Text, nullable=False, comment="稿件标题")
    article_type: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="Research Article", comment="文章类型"
    )
    section_category: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="栏目/类别"
    )
    keywords: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="", comment="关键字"
    )
    first_author: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="", comment="第一作者"
    )
    corresponding_author: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="", comment="通讯作者"
    )
    order_of_authors: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="[]", comment="作者排序(JSON格式)"
    )
    authors: Mapped[str] = mapped_column(
        Text, nullable=False, comment="作者列表（字符串，逗号分隔，向下兼容）"
    )
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True, comment="摘要")
    subject: Mapped[str] = mapped_column(Text, nullable=False, comment="学科/主题")

    # 流转信息
    stage: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="initial_review",
        comment="流转阶段：initial_review/peer_review/final_decision",
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="pending_initial_review",
        comment="全局状态",
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1", comment="版本号"
    )

    # 文件信息
    file_hash: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, comment="文件哈希（唯一）"
    )
    file_bucket: Mapped[str] = mapped_column(
        Text, nullable=False, comment="文件存储桶路径"
    )
    file_name: Mapped[str] = mapped_column(Text, nullable=False, comment="原始文件名")
    file_size: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="文件大小（字节）"
    )

    # 时间戳
    create_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    update_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="更新时间"
    )

    # 软删除
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", comment="是否已删除（软删除）"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="删除时间"
    )
    delete_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="删除原因"
    )

    # 关联关系
    versions: Mapped[list["ManuscriptVersion"]] = relationship(
        back_populates="manuscript", lazy="select"
    )
    participants: Mapped[list["ManuscriptParticipant"]] = relationship(
        back_populates="manuscript", lazy="select"
    )
    files: Mapped[list["ManuscriptFile"]] = relationship(
        back_populates="manuscript", lazy="select"
    )


class ManuscriptVersion(Base):
    """
    稿件版本表

    用于记录每次修改的历史版本
    """

    __tablename__ = "manuscript_versions"

    version_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, comment="版本 ID（自增）"
    )
    manuscript_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("manuscripts.manuscript_id"),
        nullable=False,
        comment="稿件 ID",
    )
    version_number: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="版本号（从 1 开始）"
    )

    # 版本信息
    title: Mapped[str] = mapped_column(Text, nullable=False, comment="稿件标题")
    authors: Mapped[str] = mapped_column(Text, nullable=False, comment="作者列表")
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True, comment="摘要")

    # 文件信息
    file_hash: Mapped[str] = mapped_column(Text, nullable=False, comment="文件哈希")
    file_bucket: Mapped[str] = mapped_column(
        Text, nullable=False, comment="文件存储桶路径"
    )
    file_name: Mapped[str] = mapped_column(Text, nullable=False, comment="原始文件名")
    file_size: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="文件大小（字节）"
    )

    # 提交信息
    submitted_by_uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="提交者用户 ID"
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="提交时间"
    )
    change_summary: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="修改说明"
    )

    # 关联关系
    manuscript: Mapped["Manuscript"] = relationship(
        back_populates="versions", lazy="joined"
    )


class ManuscriptParticipant(Base):
    """
    稿件参与者表

    记录参与稿件处理的所有人员（编辑、审稿人、作者等）
    """

    __tablename__ = "manuscript_participants"

    participant_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="参与者 ID（自增）"
    )
    manuscript_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("manuscripts.manuscript_id"),
        nullable=False,
        comment="稿件 ID",
    )
    user_uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="用户 ID"
    )

    # 角色类型
    role_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="参与角色：author/editor/associate_editor/ea_ae/reviewer",
    )

    # 分配信息
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="分配时间"
    )
    assigned_by_uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="分配者用户 ID"
    )

    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true", comment="是否活跃"
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )

    # 关联关系
    manuscript: Mapped["Manuscript"] = relationship(
        back_populates="participants", lazy="joined"
    )


class ManuscriptFile(Base):
    """
    稿件附件表

    管理稿件相关的所有附件文件
    """

    __tablename__ = "manuscript_files"

    file_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="附件 ID（自增）"
    )
    manuscript_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("manuscripts.manuscript_id"),
        nullable=False,
        comment="稿件 ID",
    )

    # 文件信息
    file_hash: Mapped[str] = mapped_column(Text, nullable=False, comment="文件哈希")
    file_bucket: Mapped[str] = mapped_column(
        Text, nullable=False, comment="文件存储桶路径"
    )
    original_name: Mapped[str] = mapped_column(
        Text, nullable=False, comment="原始文件名"
    )
    file_size: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="文件大小（字节）"
    )
    content_type: Mapped[str] = mapped_column(
        Text, nullable=False, comment="文件 MIME 类型"
    )

    # 分类信息
    file_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="attachment",
        comment="文件类型：main/review/letter/other",
    )
    uploaded_by_uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid"), nullable=False, comment="上传者用户 ID"
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="上传时间"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="文件描述"
    )

    # 关联关系
    manuscript: Mapped["Manuscript"] = relationship(
        back_populates="files", lazy="joined"
    )


# 索引定义
Index("idx_manuscripts_author_uid", Manuscript.author_uid)
Index("idx_manuscripts_stage", Manuscript.stage)
Index("idx_manuscripts_status", Manuscript.status)
Index("idx_manuscripts_file_hash", Manuscript.file_hash)

Index("idx_manuscript_versions_manuscript_id", ManuscriptVersion.manuscript_id)
Index("idx_manuscript_versions_version_number", ManuscriptVersion.version_number)

Index("idx_manuscript_participants_manuscript_id", ManuscriptParticipant.manuscript_id)
Index("idx_manuscript_participants_user_uid", ManuscriptParticipant.user_uid)
Index("idx_manuscript_participants_role_type", ManuscriptParticipant.role_type)

Index("idx_manuscript_files_manuscript_id", ManuscriptFile.manuscript_id)
Index("idx_manuscript_files_file_hash", ManuscriptFile.file_hash)
Index("idx_manuscript_files_file_type", ManuscriptFile.file_type)

Index("idx_manuscripts_is_deleted", Manuscript.is_deleted)
