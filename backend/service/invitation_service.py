"""
邀请码服务模块

提供邀请码生成、验证、管理等功能。
"""

import secrets
import string
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional

from database.orm.models.invitation import InvitationCode, InvitationCodeUsage
from database.repositories.invitation_repo import InvitationRepository
from database.service.database_service import db_manager
from database.uow import transactional
from sqlalchemy.ext.asyncio import AsyncSession


class InvitationService:
    """邀请码服务类"""

    def __init__(self):
        pass

    @asynccontextmanager
    async def _ensure_session(
        self, session: Optional[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        """
        确保存在可用的 AsyncSession。

        说明：
        - 若上层（如 FastAPI 路由）已注入 session，则复用该 session，避免重复建连与多事务；
        - 若未传入 session，则内部创建并自动关闭。
        """

        if session is not None:
            yield session
            return

        async with db_manager.get_session() as owned_session:
            yield owned_session

    def generate_code(self, length: int = 8) -> str:
        """
        生成邀请码

        Args:
            length: 邀请码长度，默认为8位

        Returns:
            str: 生成的邀请码
        """
        alphabet = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    async def create_invitation_code(
        self,
        role: str,
        created_by: str,
        created_by_uid: int,
        description: Optional[str] = None,
        max_uses: int = 1,
        expire_time: Optional[datetime] = None,
        session: Optional[AsyncSession] = None,
    ) -> str:
        """
        创建邀请码

        Args:
            role: 邀请码对应的角色
            created_by: 创建者用户名
            created_by_uid: 创建者用户ID
            description: 邀请码描述
            max_uses: 最大使用次数
            expire_time: 过期时间

        Returns:
            str: 生成的邀请码
        """
        code = self.generate_code()
        create_time = datetime.now()
        # expire_time 已是 datetime 对象，直接使用

        async with self._ensure_session(session) as s:
            repo = InvitationRepository(s)
            async with transactional(s):
                repo.add(
                    InvitationCode(
                        code=code,
                        role=role,
                        status="active",
                        max_uses=max_uses,
                        used_count=0,
                        description=description,
                        created_by=created_by,
                        created_by_uid=created_by_uid,
                        create_time=create_time,
                        expire_time=expire_time,
                    )
                )

        return code

    async def validate_invitation_code(
        self, code: str, session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        验证邀请码

        Args:
            code: 邀请码

        Returns:
            Dict[str, Any]: 验证结果，包含valid、role、message
        """
        async with self._ensure_session(session) as s:
            repo = InvitationRepository(s)
            invitation = await repo.get_by_code(code)

            if not invitation:
                return {"valid": False, "role": None, "message": "邀请码不存在"}

            if invitation.status != "active":
                return {"valid": False, "role": None, "message": "邀请码已失效"}

            if invitation.used_count >= invitation.max_uses:
                return {
                    "valid": False,
                    "role": None,
                    "message": "邀请码已达到最大使用次数",
                }

            if invitation.expire_time:
                expire_time_dt = invitation.expire_time
                if datetime.now() > expire_time_dt:
                    return {"valid": False, "role": None, "message": "邀请码已过期"}

            return {"valid": True, "role": invitation.role, "message": "邀请码有效"}

    async def use_invitation_code(
        self,
        code: str,
        used_by_uid: int,
        used_by_username: str,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """
        使用邀请码

        Args:
            code: 邀请码
            used_by_uid: 使用者用户ID
            used_by_username: 使用者用户名

        Returns:
            bool: 是否使用成功
        """
        async with self._ensure_session(session) as s:
            repo = InvitationRepository(s)
            try:
                async with transactional(s):
                    invitation = await repo.get_by_code(code, for_update=True)

                    if not invitation:
                        return False

                    if invitation.status != "active":
                        return False

                    if invitation.used_count >= invitation.max_uses:
                        return False

                    if invitation.expire_time:
                        expire_time_dt = invitation.expire_time
                        if datetime.now() > expire_time_dt:
                            return False

                    invitation.used_count += 1
                    if invitation.used_count >= invitation.max_uses:
                        invitation.status = "inactive"

                    use_time = datetime.now()
                    s.add(
                        InvitationCodeUsage(
                            code=code,
                            used_by_uid=used_by_uid,
                            used_by_username=used_by_username,
                            use_time=use_time,
                        )
                    )

                return True
            except Exception:
                return False

    async def update_code_status(
        self, code: str, status: str, session: Optional[AsyncSession] = None
    ) -> bool:
        """
        更新邀请码状态

        Args:
            code: 邀请码
            status: 新状态

        Returns:
            bool: 是否更新成功
        """
        async with self._ensure_session(session) as s:
            repo = InvitationRepository(s)
            async with transactional(s):
                invitation = await repo.get_by_code(code)
                if not invitation:
                    return False
                invitation.status = status
            return True

    async def get_invitation_codes(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        role: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """
        获取邀请码列表

        Args:
            page: 页码
            page_size: 每页条数
            status: 状态筛选
            role: 角色筛选

        Returns:
            Dict[str, Any]: 邀请码列表和总数
        """
        offset = (page - 1) * page_size

        async with self._ensure_session(session) as s:
            repo = InvitationRepository(s)
            total = await repo.count(status=status, role=role)
            codes = await repo.list_page(
                page=page, page_size=page_size, status=status, role=role
            )
            return {"total": total, "codes": codes}


# 全局邀请码服务实例
invitation_service = InvitationService()
