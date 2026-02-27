from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.admin_log import AdminLog


class AdminLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, log: AdminLog) -> None:
        self.session.add(log)

    async def count(self, operation_type: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(AdminLog)
        if operation_type:
            stmt = stmt.where(AdminLog.operation_type == operation_type)
        if start_time:
            stmt = stmt.where(AdminLog.operation_time >= start_time)
        if end_time:
            stmt = stmt.where(AdminLog.operation_time <= end_time)
        total = await self.session.scalar(stmt)
        return int(total or 0)

    async def list_page(
        self,
        page: int,
        page_size: int,
        operation_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> list[Dict[str, Any]]:
        offset = (page - 1) * page_size
        stmt = select(AdminLog)
        if operation_type:
            stmt = stmt.where(AdminLog.operation_type == operation_type)
        if start_time:
            stmt = stmt.where(AdminLog.operation_time >= start_time)
        if end_time:
            stmt = stmt.where(AdminLog.operation_time <= end_time)
        rows = (
            await self.session.execute(
                stmt.order_by(AdminLog.operation_time.desc()).limit(page_size).offset(offset)
            )
        ).scalars().all()
        return [
            {
                "log_id": r.log_id,
                "admin_uid": r.admin_uid,
                "admin_username": r.admin_username,
                "operation_time": r.operation_time,
                "operation_type": r.operation_type,
                "operation_object": r.operation_object,
                "operation_details": r.operation_details,
                "ip_address": r.ip_address,
                "user_agent": r.user_agent,
            }
            for r in rows
        ]

