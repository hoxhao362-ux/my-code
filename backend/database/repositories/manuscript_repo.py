"""
稿件仓库

提供稿件（Manuscript）相关的数据库操作。
将路由中分散的 SQLAlchemy 查询集中到 Repository 层。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.enums import ManuscriptStatus
<<<<<<< HEAD
from database.orm.models.manuscript import Manuscript, ManuscriptFile, ManuscriptVersion
=======
from database.orm.models.manuscript import Manuscript
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
from database.orm.models.user import User
from database.repositories.base_repo import BaseRepository
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class ManuscriptRepository(BaseRepository[Manuscript]):
    """
    稿件仓库

    提供稿件的 CRUD 及各类业务查询方法。
    主键字段为 manuscript_id。
    """

    _pk_field = "manuscript_id"

    def __init__(self, session: AsyncSession):
        super().__init__(session, Manuscript)

    # ------------------------------------------------------------------
    # 单条查询
    # ------------------------------------------------------------------

    async def get_by_manuscript_id(
        self, manuscript_id: int, include_deleted: bool = False
    ) -> Optional[Manuscript]:
        """
        根据稿件 ID 获取稿件，默认排除已删除的。

        Args:
            manuscript_id: 稿件 ID
            include_deleted: 是否包含已删除稿件

        Returns:
            Optional[Manuscript]: 稿件 ORM 对象，不存在则为 None
        """
        conditions = [Manuscript.manuscript_id == manuscript_id]
        if not include_deleted:
            conditions.append(Manuscript.is_deleted == False)  # noqa: E712
        return await self.session.scalar(select(Manuscript).where(*conditions))

    async def get_published_by_id(self, manuscript_id: int) -> Optional[Manuscript]:
        """
        获取已发表的稿件。

        Args:
            manuscript_id: 稿件 ID

        Returns:
            Optional[Manuscript]: 已发表稿件，不存在则为 None
        """
        return await self.session.scalar(
            select(Manuscript).where(
                Manuscript.manuscript_id == manuscript_id,
                Manuscript.status == ManuscriptStatus.PUBLISHED.value,
                Manuscript.is_deleted == False,  # noqa: E712
            )
        )

    # ------------------------------------------------------------------
    # 聚合统计
    # ------------------------------------------------------------------

    async def get_status_breakdown(
        self, include_deleted: bool = False
    ) -> Dict[str, int]:
        """
        按状态统计稿件数量。

        Args:
            include_deleted: 是否包含已删除稿件

        Returns:
            Dict[str, int]: {状态值: 数量}
        """
        conditions = []
        if not include_deleted:
            conditions.append(Manuscript.is_deleted == False)  # noqa: E712
        stmt = select(Manuscript.status, func.count()).group_by(Manuscript.status)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.fetchall()}

    async def get_subject_breakdown(
        self, status: Optional[str] = None
    ) -> Dict[str, int]:
        """
        按学科统计稿件数量。

        Args:
            status: 可选状态过滤

        Returns:
            Dict[str, int]: {学科: 数量}
        """
        conditions = [Manuscript.is_deleted == False]  # noqa: E712
        if status:
            conditions.append(Manuscript.status == status)
        stmt = (
            select(Manuscript.subject, func.count())
            .where(*conditions)
            .group_by(Manuscript.subject)
        )
        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.fetchall()}

    # ------------------------------------------------------------------
    # 列表查询
    # ------------------------------------------------------------------

    async def list_by_statuses(
        self,
        statuses: List[str],
        limit: Optional[int] = None,
        order_by=None,
    ) -> List[Manuscript]:
        """
        按多个状态查询稿件列表。

        Args:
            statuses: 状态值列表
            limit: 返回数量上限（None 表示不限制）
            order_by: 排序字段

        Returns:
            List[Manuscript]: 稿件 ORM 对象列表
        """
        conditions = [
            Manuscript.is_deleted == False,  # noqa: E712
            Manuscript.status.in_(statuses),
        ]
        stmt = select(Manuscript).where(*conditions)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_manuscript_page(
        self,
        page: int,
        page_size: int,
        author_uid: Optional[int] = None,
        status: Optional[str] = None,
        order_by=None,
    ) -> tuple[List[Manuscript], int]:
        """
        稿件分页查询，返回 (列表, 总数)。

        Args:
            page: 页码
            page_size: 每页数量
            author_uid: 作者 UID 过滤（可选）
            status: 状态过滤（可选）
            order_by: 排序字段

        Returns:
            tuple[List[Manuscript], int]: (稿件列表, 总数)
        """
        conditions = [Manuscript.is_deleted == False]  # noqa: E712
        if author_uid is not None:
            conditions.append(Manuscript.author_uid == author_uid)
        if status:
            conditions.append(Manuscript.status == status)

        total = await self.count(*conditions)
        manuscripts = await self.list_page(
            page, page_size, *conditions, order_by=order_by
        )
        return manuscripts, total

    async def list_published_page(
        self,
        page: int,
        page_size: int,
        keyword: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> tuple[List[Manuscript], int]:
        """
        已发表论文分页查询，返回 (列表, 总数)。

        Args:
            page: 页码
            page_size: 每页数量
            keyword: 关键词搜索（标题/作者/摘要）
            subject: 学科过滤

        Returns:
            tuple[List[Manuscript], int]: (论文列表, 总数)
        """
        conditions = [
            Manuscript.status == ManuscriptStatus.PUBLISHED.value,
            Manuscript.is_deleted == False,  # noqa: E712
        ]
        if keyword:
            keyword_pattern = f"%{keyword}%"
            conditions.append(
                or_(
                    Manuscript.title.ilike(keyword_pattern),
                    Manuscript.authors.ilike(keyword_pattern),
                    Manuscript.abstract.ilike(keyword_pattern),
                )
            )
        if subject:
            conditions.append(Manuscript.subject == subject)

        total = await self.count(*conditions)
        manuscripts = await self.list_page(
            page,
            page_size,
            *conditions,
            order_by=Manuscript.update_time.desc(),
        )
        return manuscripts, total

    # ------------------------------------------------------------------
    # 联表查询（含上传者/作者信息）
    # ------------------------------------------------------------------

    async def list_all_with_author_page(
        self,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        include_deleted: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        查询所有稿件（含上传者信息），分页返回。

        Args:
            page: 页码
            page_size: 每页数量
            status: 状态过滤（可选）
            include_deleted: 是否查询已删除稿件

        Returns:
            List[Dict[str, Any]]: 字典列表
        """
        offset = (page - 1) * page_size
        stmt = select(
            Manuscript.manuscript_id.label("jid"),
            Manuscript.title,
            Manuscript.authors,
            Manuscript.abstract,
            Manuscript.status,
            Manuscript.file_name,
            Manuscript.file_size,
            Manuscript.create_time,
            Manuscript.update_time,
            User.username.label("uploader"),
        ).join(User, Manuscript.author_uid == User.uid)
        conditions = []
        if include_deleted:
            conditions.append(Manuscript.is_deleted == True)  # noqa: E712
        else:
            conditions.append(Manuscript.is_deleted == False)  # noqa: E712
        if status:
            conditions.append(Manuscript.status == status)
        if conditions:
            stmt = stmt.where(*conditions)

        if include_deleted:
            stmt = stmt.order_by(Manuscript.deleted_at.desc())
        else:
            stmt = stmt.order_by(Manuscript.create_time.desc())
        stmt = stmt.limit(page_size).offset(offset)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return [dict(r) for r in rows]

    async def list_deleted_with_author_page(
        self, page: int, page_size: int
    ) -> List[Dict[str, Any]]:
        """
        查询已删除稿件（含上传者信息），分页返回。

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            List[Dict[str, Any]]: 字典列表（含 deleted_at、delete_reason）
        """
        offset = (page - 1) * page_size
        stmt = (
            select(
                Manuscript.manuscript_id.label("jid"),
                Manuscript.title,
                Manuscript.authors,
                Manuscript.abstract,
                Manuscript.status,
                Manuscript.file_name,
                Manuscript.file_size,
                Manuscript.create_time,
                Manuscript.update_time,
                Manuscript.deleted_at,
                Manuscript.delete_reason,
                User.username.label("uploader"),
            )
            .join(User, Manuscript.author_uid == User.uid)
            .where(Manuscript.is_deleted == True)  # noqa: E712
            .order_by(Manuscript.deleted_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return [dict(r) for r in rows]

    async def count_deleted(self) -> int:
        """统计已删除稿件数量"""
        return await self.count(Manuscript.is_deleted == True)  # noqa: E712
<<<<<<< HEAD

    async def list_manuscript_files(self, manuscript_id: int) -> List[ManuscriptFile]:
        """某稿件全部附件，按上传时间倒序。"""
        stmt = (
            select(ManuscriptFile)
            .where(ManuscriptFile.manuscript_id == manuscript_id)
            .order_by(ManuscriptFile.uploaded_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_manuscript_versions(self, manuscript_id: int) -> List[ManuscriptVersion]:
        """稿件版本历史，按提交时间正序。"""
        stmt = (
            select(ManuscriptVersion)
            .where(ManuscriptVersion.manuscript_id == manuscript_id)
            .order_by(ManuscriptVersion.submitted_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_manuscript_info_row(self):
        """最新一条出版扩展信息（按 publication_date 文本降序）。"""
        from database.orm.models.manuscript_info import ManuscriptInfo

        stmt = (
            select(ManuscriptInfo)
            .order_by(ManuscriptInfo.publication_date.desc())
            .limit(1)
        )
        return await self.session.scalar(stmt)
=======
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
