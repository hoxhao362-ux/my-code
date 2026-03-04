"""
管理员操作日志表 ORM Model

表名：admin_logs
"""

from __future__ import annotations

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


class AdminLog(Base):
    __tablename__ = "admin_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="日志ID（自增）")
    admin_uid: Mapped[int] = mapped_column(Integer, nullable=False, comment="管理员用户ID")
    admin_username: Mapped[str] = mapped_column(Text, nullable=False, comment="管理员用户名")

    operation_time: Mapped[str] = mapped_column(Text, nullable=False, comment="操作时间（ISO字符串）")
    operation_type: Mapped[str] = mapped_column(Text, nullable=False, comment="操作类型")
    operation_object: Mapped[str] = mapped_column(Text, nullable=False, comment="操作对象")
    operation_details: Mapped[str | None] = mapped_column(Text, nullable=True, comment="操作详情")

    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True, comment="IP地址")
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True, comment="User-Agent")

