"""
用户表 ORM Model

表名：users
来源：原 asyncpg 建表逻辑（user_account/users）。

说明：
时间字段已从 TEXT 迁移为 PostgreSQL 原生 DateTime (TIMESTAMP) 类型，
提升查询性能与规范性。写入时直接传 datetime 对象即可。
"""

from __future__ import annotations

from datetime import datetime

from database.orm.base import Base
from sqlalchemy import Boolean, DateTime, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

# ============================================================
# 数据迁移说明（TEXT → TIMESTAMP）
# 执行以下 SQL 将现有数据从 TEXT 转换为 TIMESTAMP：
#
# ALTER TABLE users ALTER COLUMN create_time TYPE TIMESTAMP USING create_time::TIMESTAMP;
# ALTER TABLE users ALTER COLUMN last_login_time TYPE TIMESTAMP USING last_login_time::TIMESTAMP;
# ALTER TABLE users ALTER COLUMN deleted_at TYPE TIMESTAMP USING deleted_at::TIMESTAMP;
#
# 注意：执行前请备份数据库
# ============================================================


class User(Base):
    __tablename__ = "users"

    uid: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="用户ID（自增）"
    )
    uid_hash: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, comment="用户UID哈希（业务唯一）"
    )
    username: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, comment="用户名（唯一）"
    )
    password: Mapped[str] = mapped_column(Text, nullable=False, comment="密码哈希")
    email: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, comment="邮箱（唯一）"
    )

    role: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="author",
        comment="角色：user/author/reviewer/ea_ae/associate_editor/editor/admin",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", comment="是否已验证邮箱/账号"
    )
    verification_code: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="验证码"
    )

    avatar_path: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="头像文件路径"
    )
    avatar_hash: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="头像哈希"
    )

    create_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="最后登录时间"
    )
    login_days: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0", comment="累计登录天数"
    )

    # 软删除字段
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", comment="是否已删除（软删除）"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="删除时间"
    )


Index("idx_users_username", User.username)
Index("idx_users_email", User.email)
Index("idx_users_is_deleted", User.is_deleted)
