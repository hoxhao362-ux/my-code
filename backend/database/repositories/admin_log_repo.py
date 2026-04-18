"""
管理员操作日志仓库

提供管理员操作日志（AdminLog）相关的数据库操作。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.admin_log import AdminLog
from database.repositories.base_repo import BaseRepository


class AdminLogRepository(BaseRepository[AdminLog]):
    """
    管理员操作日志仓库

    提供操作日志的查询方法。
    主键字段为 log_id。
    """

    _pk_field = "log_id"

    def __init__(self, session: AsyncSession):
        super().__init__(session, AdminLog)

    async def count(self, operation_type: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> int:
        """
        统计操作日志数（兼容原接口签名）。

        Args:
            operation_type: 操作类型过滤（可选）
            start_time: 起始时间过滤（可选）
            end_time: 结束时间过滤（可选）

        Returns:
            int: 日志数
        """
        conditions = []
        if operation_type:
            conditions.append(AdminLog.operation_type == operation_type)
        if start_time:
            conditions.append(AdminLog.operation_time >= start_time)
        if end_time:
            conditions.append(AdminLog.operation_time <= end_time)
        return await super().count(*conditions)

    async def list_page(
        self,
        page: int,
        page_size: int,
        operation_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> list[Dict[str, Any]]:
        """
        分页查询操作日志列表。

        Args:
            page: 页码
            page_size: 每页数量
            operation_type: 操作类型过滤（可选）
            start_time: 起始时间过滤（可选）
            end_time: 结束时间过滤（可选）

        Returns:
            list[Dict[str, Any]]: 字典列表
        """
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
