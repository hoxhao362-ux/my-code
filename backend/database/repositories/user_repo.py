"""
用户仓库

提供用户（User）相关的数据库操作。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.user import User
from database.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    用户仓库

    提供用户的 CRUD 及各类业务查询方法。
    主键字段为 uid。
    """

    _pk_field = "uid"

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    # ------------------------------------------------------------------
    # 单条查询
    # ------------------------------------------------------------------

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return await self.session.scalar(
            select(User).where(User.username == username)
        )

    async def username_exists(self, username: str) -> bool:
        """检查用户名是否已存在"""
        uid = await self.session.scalar(
            select(User.uid).where(User.username == username)
        )
        return uid is not None

    async def email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        uid = await self.session.scalar(
            select(User.uid).where(User.email == email)
        )
        return uid is not None

    async def get_public_fields_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        """获取用户的公开字段（脱敏后）"""
        row = (
            await self.session.execute(
                select(
                    User.uid,
                    User.username,
                    User.email,
                    User.role,
                    User.is_verified,
                    User.is_deleted,
                ).where(User.uid == uid)
            )
        ).mappings().first()
        return dict(row) if row else None

    async def get_profile_fields_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        """获取用户的个人资料字段"""
        row = (
            await self.session.execute(
                select(
                    User.uid,
                    User.username,
                    User.email,
                    User.role,
                    User.create_time,
                    User.last_login_time,
                    User.avatar_hash,
                ).where(User.uid == uid)
            )
        ).mappings().first()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # 统计
    # ------------------------------------------------------------------

    async def count_by_role(self, role: Optional[str] = None) -> int:
        """
        按角色统计用户数。

        Args:
            role: 角色过滤（可选）

        Returns:
            int: 用户数
        """
        conditions = []
        if role:
            conditions.append(User.role == role)
        return await self.count(*conditions)

    # 保留原 count 签名以兼容现有调用
    async def count(self, role: Optional[str] = None) -> int:
        """
        统计用户数（兼容原接口签名）。

        Args:
            role: 角色过滤（可选）

        Returns:
            int: 用户数
        """
        conditions = []
        if role:
            conditions.append(User.role == role)
        return await super().count(*conditions)

    # ------------------------------------------------------------------
    # 列表
    # ------------------------------------------------------------------

    async def list_page(
        self, page: int, page_size: int, role: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        分页查询用户列表（列投影）。

        Args:
            page: 页码
            page_size: 每页数量
            role: 角色过滤（可选）

        Returns:
            list[Dict[str, Any]]: 字典列表
        """
        offset = (page - 1) * page_size
        stmt = select(
            User.uid,
            User.username,
            User.email,
            User.role,
            User.is_verified,
            User.create_time,
            User.last_login_time,
        )
        if role:
            stmt = stmt.where(User.role == role)
        rows = (
            await self.session.execute(
                stmt.order_by(User.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def role_breakdown(self) -> list[Dict[str, Any]]:
        """按角色分组统计"""
        rows = (
            await self.session.execute(
                select(User.role, func.count().label("count")).group_by(User.role)
            )
        ).mappings().all()
        return [dict(r) for r in rows]
