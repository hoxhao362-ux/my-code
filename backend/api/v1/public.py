"""
公共接口相关 API 接口

包含期刊列表、论文检索等公开访问功能
"""

from typing import Optional

from api import dependencies as deps
from core.config import config
from core.enums import ManuscriptStatus
from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript
from database.repositories.editorial_board_repo import EditorialBoardRepository
from database.repositories.manuscript_repo import ManuscriptRepository
from database.repositories.user_repo import UserRepository
from fastapi import APIRouter, Depends, HTTPException, Query
from model.manuscript import ArticleDetailDTO, ArticleListItemDTO
from model.response import ApiResponse
from service.elasticsearch_service import elasticsearch_service
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import global_logger

# 创建公共接口路由
router = APIRouter(
    prefix="/public",
    tags=["公共接口相关接口"],
    dependencies=[Depends(deps.check_db_service)],
    responses={
        404: {"description": "资源不存在"},
    },
)


@router.get("/journals", summary="获取期刊列表")
async def get_journal_list(
    page: int = 1,
    page_size: int = 10,
    subject: str | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取公开的期刊列表

    注：当前系统为单期刊模式，返回期刊基本信息和统计数据

    Args:
        page: 页码
        page_size: 每页数量
        subject: 学科筛选
        session: 数据库会话

    Returns:
        dict: 期刊列表
    """
    global_logger.debug("Public", f"获取期刊列表 - page: {page}, subject: {subject}")

    repo = ManuscriptRepository(session)
    published_count = await repo.count(
        Manuscript.status == ManuscriptStatus.PUBLISHED.value,
        Manuscript.is_deleted == False,  # noqa: E712
    )
    subject_stats = await repo.get_subject_breakdown(
        status=ManuscriptStatus.PUBLISHED.value
    )

    journal_name = config.get("journal.display.name", "期刊平台")
    journal_desc = config.get("journal.display.description", "")
    journal_version = config.get("journal.display.version", "2.0.0")

    journals = [
        {
            "id": 1,
            "name": journal_name,
            "description": journal_desc,
            "version": journal_version,
            "published_articles": published_count,
            "subjects": list(subject_stats.keys()),
            "subject_statistics": subject_stats,
        }
    ]

    return ApiResponse.paginated(
        items=journals, total=1, page=page, page_size=page_size
    )


@router.get("/articles", summary="获取已发表论文列表")
async def get_published_articles(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    subject: str | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取已发表的论文列表

    Args:
        page: 页码
        page_size: 每页数量
        keyword: 关键词搜索（标题/作者/摘要）
        subject: 学科筛选
        session: 数据库会话

    Returns:
        dict: 论文列表
    """
    global_logger.debug(
        "Public",
        f"获取已发表论文 - page: {page}, keyword: {keyword}, subject: {subject}",
    )

    # 通过 Repository 查询已发表论文
    repo = ManuscriptRepository(session)
    manuscripts, total = await repo.list_published_page(
        page, page_size, keyword=keyword, subject=subject
    )

    # 使用 Pydantic DTO 转换为响应格式
    articles = [ArticleListItemDTO.model_validate(m).model_dump() for m in manuscripts]

    return ApiResponse.paginated(
        items=articles, total=total, page=page, page_size=page_size
    )


@router.get("/articles/{article_id}", summary="获取论文详情")
async def get_article_detail(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取单篇已发表论文的详细信息

    Args:
        article_id: 论文 ID（即 manuscript_id）
        session: 数据库会话

    Returns:
        dict: 论文详细信息
    """
    global_logger.debug("Public", f"获取论文详情 - article_id: {article_id}")

    # 通过 Repository 查询已发表的论文
    repo = ManuscriptRepository(session)
    manuscript = await repo.get_published_by_id(article_id)

    if not manuscript:
        raise HTTPException(status_code=404, detail="论文不存在或未发表")

    # 使用 Pydantic DTO 转换为响应格式
    dto = ArticleDetailDTO.model_validate(manuscript)
    return ApiResponse.success(data=dto.model_dump())


@router.get("/search", summary="搜索论文")
async def search_articles(
    query: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    subject: Optional[str] = Query(None, description="学科过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
):
    """
    搜索论文（基于 Elasticsearch）

    Args:
        query: 搜索关键词
        page: 页码
        page_size: 每页数量
        subject: 学科过滤（可选）
        status: 状态过滤（可选）

    Returns:
        dict: 搜索结果
    """
    global_logger.debug("Public", f"搜索论文 - query: {query}, page: {page}")

    # 构建过滤条件
    filters = {}
    if subject:
        filters["subject"] = subject
    if status:
        filters["status"] = status

    # 调用 Elasticsearch 服务进行搜索
    result = await elasticsearch_service.search(
        query=query, page=page, size=page_size, filters=filters if filters else None
    )

    # 检查是否有错误
    if result.get("error"):
        return ApiResponse.error(
            message=f"搜索服务异常: {result.get('error')}", code=503
        )

    return ApiResponse.paginated(
        items=result.get("items", []),
        total=result.get("total", 0),
        page=result.get("page", page),
        page_size=result.get("size", page_size),
    )


@router.get("/info", summary="获取期刊信息")
async def get_journal_info(session: AsyncSession = Depends(get_db_session)):
    """门户期刊信息：配置中的展示字段 + 运行统计 + 最近期号（如有）。"""
    m_repo = ManuscriptRepository(session)
    u_repo = UserRepository(session)
    eb_repo = EditorialBoardRepository(session)

    published_articles = await m_repo.count(
        Manuscript.status == ManuscriptStatus.PUBLISHED.value,
        Manuscript.is_deleted == False,  # noqa: E712
    )
    registered_users = await u_repo.count_active_users()
    board_members = await eb_repo.count_active()

    latest = await m_repo.get_latest_manuscript_info_row()
    latest_issue = None
    if latest:
        latest_issue = {
            "volume": latest.volume,
            "issue": latest.issue,
            "issue_number": latest.issue_number,
            "publication_date": latest.publication_date,
            "doi": latest.doi,
        }

    data = {
        "name": config.get("journal.display.name", "期刊平台"),
        "description": config.get("journal.display.description", ""),
        "version": config.get("journal.display.version", "2.0.0"),
        "issn": config.get("journal.display.issn", ""),
        "publisher": config.get("journal.display.publisher", ""),
        "frequency": config.get("journal.display.frequency", ""),
        "contact_email": config.get("journal.display.contact_email", ""),
        "statistics": {
            "published_articles": published_articles,
            "registered_users": registered_users,
            "editorial_board_members": board_members,
        },
        "latest_issue": latest_issue,
    }

    global_logger.debug("Public", "返回 /public/info")
    return ApiResponse.success(data=data)
