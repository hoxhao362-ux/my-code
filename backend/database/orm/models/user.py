"""
用户表 ORM Model

表名：users
来源：原 asyncpg 建表逻辑（user_account/users）。

说明：
项目当前以 ISO 字符串存储时间字段（create_time/last_login_time），为了兼容已有数据与业务逻辑，仍使用 TEXT。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


class User(Base):
    __tablename__ = "users"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True, comment="用户ID（自增）")
    uid_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False, comment="用户UID哈希（业务唯一）")
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False, comment="用户名（唯一）")
    password: Mapped[str] = mapped_column(Text, nullable=False, comment="密码哈希")
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False, comment="邮箱（唯一）")

    role: Mapped[str] = mapped_column(Text, nullable=False, server_default="normal", comment="角色：normal/writer/reviewer/admin")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false", comment="是否已验证邮箱/账号")
    verification_code: Mapped[str | None] = mapped_column(Text, nullable=True, comment="验证码")

    avatar_path: Mapped[str | None] = mapped_column(Text, nullable=True, comment="头像文件路径")
    avatar_hash: Mapped[str | None] = mapped_column(Text, nullable=True, comment="头像哈希")

    create_time: Mapped[str] = mapped_column(Text, nullable=False, comment="创建时间（ISO字符串）")
    last_login_time: Mapped[str | None] = mapped_column(Text, nullable=True, comment="最后登录时间（ISO字符串）")


Index("idx_users_username", User.username)
Index("idx_users_email", User.email)

