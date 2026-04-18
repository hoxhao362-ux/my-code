"""
邀请码仓库

提供邀请码（InvitationCode）相关的数据库操作。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from database.orm.models.invitation import InvitationCode
from database.repositories.base_repo import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class InvitationRepository(BaseRepository[InvitationCode]):
    """
    邀请码仓库

    提供邀请码的查询方法。
    主键字段为 code_id。
    """

    _pk_field = "code_id"

    def __init__(self, session: AsyncSession):
        super().__init__(session, InvitationCode)

    async def get_by_code(
        self, code: str, for_update: bool = False
    ) -> Optional[InvitationCode]:
        """
        根据邀请码获取记录。

        Args:
            code: 邀请码字符串
            for_update: 是否加行锁（SELECT ... FOR UPDATE）

        Returns:
            Optional[InvitationCode]: 邀请码记录，不存在则为 None
        """
        stmt = select(InvitationCode).where(InvitationCode.code == code)
        if for_update:
            stmt = stmt.with_for_update()
        return await self.session.scalar(stmt)

    async def count(
        self, status: Optional[str] = None, role: Optional[str] = None
    ) -> int:
        """
        统计邀请码数（兼容原接口签名）。

        Args:
            status: 状态过滤（可选）
            role: 角色过滤（可选）

        Returns:
            int: 邀请码数
        """
        conditions = []
        if status:
            conditions.append(InvitationCode.status == status)
        if role:
            conditions.append(InvitationCode.role == role)
        return await super().count(*conditions)

    async def list_page(
        self,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        role: Optional[str] = None,
    ) -> list[Dict[str, Any]]:
        """
        分页查询邀请码列表。

        Args:
            page: 页码
            page_size: 每页数量
            status: 状态过滤（可选）
            role: 角色过滤（可选）

        Returns:
            list[Dict[str, Any]]: 字典列表
        """
        offset = (page - 1) * page_size
        stmt = select(InvitationCode)
        if status:
            stmt = stmt.where(InvitationCode.status == status)
        if role:
            stmt = stmt.where(InvitationCode.role == role)
        rows = (
            (
                await self.session.execute(
                    stmt.order_by(InvitationCode.create_time.desc())
                    .limit(page_size)
                    .offset(offset)
                )
            )
            .scalars()
            .all()
        )
        return [
            {
                "code": r.code,
                "role": r.role,
                "status": r.status,
                "max_uses": r.max_uses,
                "used_count": r.used_count,
                "description": r.description,
                "created_by": r.created_by,
                "created_by_uid": r.created_by_uid,
                "create_time": r.create_time,
                "expire_time": r.expire_time,
            }
            for r in rows
        ]
