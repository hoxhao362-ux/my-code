"""
文献仓库（兼容旧 Journal 模型）

提供文献（Journal）相关的数据库操作。
注意：Journal 模型已废弃，新业务应使用 ManuscriptRepository。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm.models.journal import Journal
from database.orm.models.user import User
from database.repositories.base_repo import BaseRepository


class JournalRepository(BaseRepository[Journal]):
    """
    文献仓库

    提供文献的 CRUD 及各类业务查询方法。
    主键字段为 jid。
    """

    _pk_field = "jid"

    def __init__(self, session: AsyncSession):
        super().__init__(session, Journal)

    # ------------------------------------------------------------------
    # 按上传者查询
    # ------------------------------------------------------------------

    async def count_by_uploader(self, uid: int) -> int:
        """统计指定用户上传的文献数"""
        return await self.count(Journal.uid == uid)

    async def list_by_uploader_page(self, uid: int, page: int, page_size: int) -> list[Dict[str, Any]]:
        """按上传者分页查询文献列表"""
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where(Journal.uid == uid)
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 按状态查询
    # ------------------------------------------------------------------

    async def count_by_status(self, status: str) -> int:
        """按状态统计文献数"""
        return await self.count(Journal.status == status)

    async def list_by_status_page(self, status: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        """按状态分页查询文献列表"""
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where(Journal.status == status)
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_public(self) -> int:
        """统计已发表文献数"""
        return await self.count_by_status("published")

    async def list_public_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        """查询已发表文献分页列表"""
        return await self.list_by_status_page("published", page, page_size)

    # ------------------------------------------------------------------
    # 已删除文献
    # ------------------------------------------------------------------

    async def count_deleted(self) -> int:
        """统计已删除文献数"""
        return await self.count(Journal.status == "deleted")

    async def list_deleted_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        """查询已删除文献分页列表"""
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time,
                    Journal.update_time,
                    Journal.uid,
                )
                .where(Journal.status == "deleted")
                .order_by(Journal.update_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 全量查询
    # ------------------------------------------------------------------

    async def count_all(self, status: Optional[str] = None) -> int:
        """统计所有文献数（可按状态过滤）"""
        conditions = []
        if status:
            conditions.append(Journal.status == status)
        return await self.count(*conditions)

    async def list_all_with_uploader_page(self, page: int, page_size: int, status: Optional[str] = None) -> list[Dict[str, Any]]:
        """查询所有文献（含上传者信息），分页返回"""
        offset = (page - 1) * page_size
        stmt = (
            select(
                Journal.jid,
                Journal.title,
                Journal.authors,
                Journal.abstract,
                Journal.status,
                Journal.file_name,
                Journal.file_size,
                Journal.create_time,
                Journal.update_time,
                User.username.label("uploader"),
            )
            .join(User, Journal.uid == User.uid)
        )
        if status:
            stmt = stmt.where(Journal.status == status)
        rows = (await self.session.execute(stmt.order_by(Journal.create_time.desc()).limit(page_size).offset(offset))).mappings().all()
        return [dict(r) for r in rows]

    async def list_deleted_with_uploader_page(self, page: int, page_size: int) -> list[Dict[str, Any]]:
        """查询已删除文献（含上传者信息），分页返回"""
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time,
                    Journal.update_time,
                    User.username.label("uploader"),
                )
                .join(User, Journal.uid == User.uid)
                .where(Journal.status == "deleted")
                .order_by(Journal.update_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 统计
    # ------------------------------------------------------------------

    async def status_breakdown(self) -> list[Dict[str, Any]]:
        """按状态分组统计"""
        rows = (await self.session.execute(select(Journal.status, func.count().label("count")).group_by(Journal.status))).mappings().all()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 搜索
    # ------------------------------------------------------------------

    async def count_search_title_or_abstract(self, keyword: str) -> int:
        """按标题或摘要关键词搜索统计"""
        like_kw = f"%{keyword}%"
        return await self.count(
            (Journal.title.like(like_kw) | Journal.abstract.like(like_kw)) & (Journal.status != "deleted")
        )

    async def list_search_title_or_abstract_page(self, keyword: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        """按标题或摘要关键词搜索分页"""
        offset = (page - 1) * page_size
        like_kw = f"%{keyword}%"
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where((Journal.title.like(like_kw) | Journal.abstract.like(like_kw)) & (Journal.status != "deleted"))
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_search_author(self, keyword: str) -> int:
        """按作者关键词搜索统计"""
        like_kw = f"%{keyword}%"
        return await self.count(
            (Journal.authors.like(like_kw)) & (Journal.status != "deleted")
        )

    async def list_search_author_page(self, keyword: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        """按作者关键词搜索分页"""
        offset = (page - 1) * page_size
        like_kw = f"%{keyword}%"
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where((Journal.authors.like(like_kw)) & (Journal.status != "deleted"))
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    async def count_search_subject(self, subject: str) -> int:
        """按学科搜索统计"""
        return await self.count(
            (Journal.subject == subject) & (Journal.status != "deleted")
        )

    async def list_search_subject_page(self, subject: str, page: int, page_size: int) -> list[Dict[str, Any]]:
        """按学科搜索分页"""
        offset = (page - 1) * page_size
        rows = (
            await self.session.execute(
                select(
                    Journal.jid,
                    Journal.title,
                    Journal.authors,
                    Journal.abstract,
                    Journal.status,
                    Journal.file_name,
                    Journal.file_size,
                    Journal.create_time.label("upload_time"),
                    Journal.update_time,
                )
                .where((Journal.subject == subject) & (Journal.status != "deleted"))
                .order_by(Journal.create_time.desc())
                .limit(page_size)
                .offset(offset)
            )
        ).mappings().all()
        return [dict(r) for r in rows]
