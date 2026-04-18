"""
邀请码相关表 ORM Model

表名：
- invitation_codes：邀请码主表
- invitation_code_usage：邀请码使用记录
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


# ============================================================
# 数据迁移说明（TEXT → TIMESTAMP）
# 执行以下 SQL 将现有数据从 TEXT 转换为 TIMESTAMP：
#
# ALTER TABLE invitation_codes ALTER COLUMN create_time TYPE TIMESTAMP USING create_time::TIMESTAMP;
# ALTER TABLE invitation_codes ALTER COLUMN expire_time TYPE TIMESTAMP USING expire_time::TIMESTAMP;
# ALTER TABLE invitation_code_usage ALTER COLUMN use_time TYPE TIMESTAMP USING use_time::TIMESTAMP;
#
# 注意：执行前请备份数据库
# ============================================================


class InvitationCode(Base):
    __tablename__ = "invitation_codes"

    code_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID（自增）")
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False, comment="邀请码（唯一）")
    role: Mapped[str] = mapped_column(Text, nullable=False, comment="授予角色：user/author/reviewer/ea_ae/associate_editor/editor/admin")
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active", comment="状态：active/disabled/expired")

    max_uses: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", comment="最大可使用次数")
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0", comment="已使用次数")

    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    created_by: Mapped[str] = mapped_column(Text, nullable=False, comment="创建人用户名")
    created_by_uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False, comment="创建人用户ID")

    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    expire_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="过期时间")


class InvitationCodeUsage(Base):
    __tablename__ = "invitation_code_usage"

    usage_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="使用记录ID（自增）")
    code: Mapped[str] = mapped_column(Text, nullable=False, comment="邀请码")
    used_by_uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False, comment="使用人用户ID")
    used_by_username: Mapped[str] = mapped_column(Text, nullable=False, comment="使用人用户名")
    use_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="使用时间")


Index("idx_invitation_codes_code", InvitationCode.code)
Index("idx_invitation_code_usage_code", InvitationCodeUsage.code)
Index("idx_invitation_code_usage_used_by_uid", InvitationCodeUsage.used_by_uid)

