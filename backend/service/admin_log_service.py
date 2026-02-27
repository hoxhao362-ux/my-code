"""
管理员日志服务模块

提供管理员操作日志的记录和查询功能。
"""
from datetime import datetime
from typing import Dict, Any, Optional, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from database.service.database_service import db_manager
from database.orm.models.admin_log import AdminLog
from database.repositories.admin_log_repo import AdminLogRepository
from database.uow import transactional

class AdminLogService:
    """管理员日志服务类"""
    
    def __init__(self):
        pass

    @asynccontextmanager
    async def _ensure_session(self, session: Optional[AsyncSession]) -> AsyncIterator[AsyncSession]:
        if session is not None:
            yield session
            return

        async with db_manager.get_session() as owned_session:
            yield owned_session
    
    async def record_admin_log(
        self,
        admin_uid: int,
        admin_username: str,
        operation_type: str,
        operation_object: str,
        operation_details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ):
        """
        记录管理员操作日志
        
        Args:
            admin_uid: 管理员ID
            admin_username: 管理员用户名
            operation_type: 操作类型（如：添加用户、删除文献、修改角色等）
            operation_object: 操作对象（如：用户ID、文献ID等）
            operation_details: 操作详情（可选）
            ip_address: IP地址（可选）
            user_agent: 用户代理（可选）
        """
        async with self._ensure_session(session) as s:
            repo = AdminLogRepository(s)
            async with transactional(s):
                repo.add(
                    AdminLog(
                        admin_uid=admin_uid,
                        admin_username=admin_username,
                        operation_time=datetime.now().isoformat(),
                        operation_type=operation_type,
                        operation_object=operation_object,
                        operation_details=operation_details,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                )

    async def get_admin_logs(
        self,
        page: int = 1,
        page_size: int = 10,
        operation_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """
        获取管理员操作日志列表
        
        Args:
            page: 页码
            page_size: 每页条数
            operation_type: 操作类型（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
        
        Returns:
            包含日志总数和日志列表的字典
        """
        offset = (page - 1) * page_size

        async with self._ensure_session(session) as s:
            repo = AdminLogRepository(s)
            total = await repo.count(operation_type=operation_type, start_time=start_time, end_time=end_time)
            logs = await repo.list_page(
                page=page,
                page_size=page_size,
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
            )
            return {"total": total, "logs": logs}

# 全局管理员日志服务实例
admin_log_service = AdminLogService()
