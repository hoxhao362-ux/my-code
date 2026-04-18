"""
管理员操作日志表 ORM Model

表名：admin_logs
"""

from __future__ import annotations

from datetime import datetime

from database.orm.base import Base
from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

# ============================================================
# 数据迁移说明（TEXT → TIMESTAMP）
# 执行以下 SQL 将现有数据从 TEXT 转换为 TIMESTAMP：
#
# ALTER TABLE admin_logs ALTER COLUMN operation_time TYPE TIMESTAMP USING operation_time::TIMESTAMP;
#
# 注意：执行前请备份数据库
# ============================================================


class AdminLog(Base):
    __tablename__ = "admin_logs"

    log_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="日志ID（自增）"
    )
    admin_uid: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="管理员用户ID"
    )
    admin_username: Mapped[str] = mapped_column(
        Text, nullable=False, comment="管理员用户名"
    )

    operation_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="操作时间"
    )
    operation_type: Mapped[str] = mapped_column(
        Text, nullable=False, comment="操作类型"
    )
    operation_object: Mapped[str] = mapped_column(
        Text, nullable=False, comment="操作对象"
    )
    operation_details: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="操作详情"
    )

    ip_address: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="IP地址"
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="User-Agent"
    )
