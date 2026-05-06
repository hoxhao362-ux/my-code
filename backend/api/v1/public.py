"""
公共接口相关 API 接口

包含期刊列表、论文检索等公开访问功能
"""

from typing import Optional

from api import dependencies as deps
<<<<<<< HEAD
from core.config import config
from core.enums import ManuscriptStatus
from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript
from database.repositories.editorial_board_repo import EditorialBoardRepository
from database.repositories.manuscript_repo import ManuscriptRepository
from database.repositories.user_repo import UserRepository
=======
from core.enums import ManuscriptStatus
from database.dependencies import get_db_session
from database.repositories.manuscript_repo import ManuscriptRepository
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
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

<<<<<<< HEAD
=======
    # 通过 Repository 查询统计数据
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    repo = ManuscriptRepository(session)
    published_count = await repo.count(
        Manuscript.status == ManuscriptStatus.PUBLISHED.value,
        Manuscript.is_deleted == False,  # noqa: E712
    )
    subject_stats = await repo.get_subject_breakdown(
        status=ManuscriptStatus.PUBLISHED.value
    )

<<<<<<< HEAD
    journal_name = config.get("journal.display.name", "期刊平台")
    journal_desc = config.get("journal.display.description", "")
    journal_version = config.get("journal.display.version", "2.0.0")

    journals = [
        {
            "id": 1,
            "name": journal_name,
            "description": journal_desc,
            "version": journal_version,
=======
    # 当前系统为单期刊模式，返回期刊基本信息
    journals = [
        {
            "id": 1,
            "name": "期刊平台",
            "description": "学术期刊投稿平台",
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
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
<<<<<<< HEAD
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
=======
async def get_journal_info():
    """
    获取期刊基本信息

    TODO: 从数据库或配置读取期刊信息

    建议实现流程：
    1. 从 configs/journal.toml 配置文件读取期刊名称、描述、ISSN、出版周期等基础信息
    2. 从数据库统计期刊的运营数据：已发表论文总数、本月新发表论文数、注册用户总数、编委人数
    3. 查询 ManuscriptInfo 表获取最新期号信息（volume/issue/issue_number）
    4. 查询 EditorialBoard 表获取主编和编委总数
    5. 组装完整的期刊信息返回

    所需 ORM 模型：
    - Manuscript (database/orm/models/manuscript.py) — 稿件主表，统计已发表论文数
    - ManuscriptInfo (database/orm/models/manuscript_info.py) — 稿件出版信息扩展表，获取最新期号/卷号
    - EditorialBoard (database/orm/models/editorial.py) — 编委会成员表，统计编委人数
    - User (database/orm/models/user.py) — 用户表，统计注册用户数

    建议 Repository 方法：
    - ManuscriptRepository.count_by_status(status='published') — 统计已发表论文总数
    - ManuscriptInfoRepository.get_latest_issue() — 获取最新期号信息
    - EditorialBoardRepository.count_active() — 统计在职编委人数
    - UserRepository.count_all() — 统计注册用户总数

    建议 Service 调用链：
    API → config["journal"]] 读取基础信息
        → ManuscriptRepository.count_by_status() 统计论文数
        → ManuscriptInfoRepository.get_latest_issue() 获取期号
        → EditorialBoardRepository.count_active() 统计编委
        → 组装返回

    权限要求：
    - 当前无需登录（公开接口），符合要求
    - 期刊信息属于公开信息，无需鉴权

    返回数据格式建议：
    {
        "name": "XX大学学报",
        "description": "XX大学主办的综合性学术期刊",
        "issn": "1000-1234",
        "publisher": "XX大学出版社",
        "frequency": "双月刊",
        "version": "1.0.0",
        "statistics": {
            "published_articles": 156,
            "monthly_new_articles": 5,
            "registered_users": 320,
            "editorial_board_members": 12
        },
        "latest_issue": {
            "volume": "2026",
            "issue": "2",
            "issue_number": "J2026-02",
            "publication_date": "2026-03-01"
        }
    }

    注意事项：
    - 当前系统为单期刊模式，未来如需多期刊支持，需增加期刊 ID 参数
    - 期刊基础信息建议从配置文件读取而非硬编码，便于动态修改
    - 统计数据可缓存到 Redis（TTL 5分钟），避免每次请求都查数据库
    - 此接口为高频访问接口，需注意性能优化
    - configs/journal.toml 可能需要新增字段（如 issn/publisher/frequency）
    - 需增加数据库 session 依赖（当前函数缺少 session 参数）
    """
    return ApiResponse.success(
        data={"name": "期刊平台", "description": "学术期刊投稿平台", "version": "1.0.0"}
    )
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
