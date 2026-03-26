"""
公共接口相关 API 接口

包含期刊列表、论文检索等公开访问功能
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies as deps
from model.response import ApiResponse
from service.elasticsearch_service import elasticsearch_service
from utils.log import global_logger
from core.enums import ManuscriptStatus

from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript

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
    
    # 查询已发表文章数量
    published_count_query = (
        select(func.count())
        .select_from(Manuscript)
        .where(
            Manuscript.status == ManuscriptStatus.PUBLISHED.value,
            Manuscript.is_deleted == False
        )
    )
    published_result = await session.execute(published_count_query)
    published_count = published_result.scalar() or 0
    
    # 查询学科分类统计
    subject_stats_query = (
        select(Manuscript.subject, func.count())
        .where(
            Manuscript.status == ManuscriptStatus.PUBLISHED.value,
            Manuscript.is_deleted == False
        )
        .group_by(Manuscript.subject)
    )
    subject_result = await session.execute(subject_stats_query)
    subject_stats = {row[0]: row[1] for row in subject_result.fetchall()}
    
    # 当前系统为单期刊模式，返回期刊基本信息
    journals = [
        {
            "id": 1,
            "name": "期刊平台",
            "description": "学术期刊投稿平台",
            "published_articles": published_count,
            "subjects": list(subject_stats.keys()),
            "subject_statistics": subject_stats,
        }
    ]
    
    return ApiResponse.paginated(
        items=journals,
        total=1,
        page=page,
        page_size=page_size
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
    global_logger.debug("Public", f"获取已发表论文 - page: {page}, keyword: {keyword}, subject: {subject}")
    
    offset = (page - 1) * page_size
    
    # 构建查询条件
    conditions = [
        Manuscript.status == ManuscriptStatus.PUBLISHED.value,
        Manuscript.is_deleted == False
    ]
    
    # 关键词搜索（标题/作者/摘要）
    if keyword:
        keyword_pattern = f"%{keyword}%"
        conditions.append(
            or_(
                Manuscript.title.ilike(keyword_pattern),
                Manuscript.authors.ilike(keyword_pattern),
                Manuscript.abstract.ilike(keyword_pattern)
            )
        )
    
    # 学科筛选
    if subject:
        conditions.append(Manuscript.subject == subject)
    
    # 查询总数
    count_query = select(func.count()).select_from(Manuscript).where(*conditions)
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0
    
    # 查询列表
    list_query = (
        select(Manuscript)
        .where(*conditions)
        .order_by(Manuscript.update_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    list_result = await session.execute(list_query)
    manuscripts = list_result.scalars().all()
    
    # 转换为响应格式
    articles = [
        {
            "article_id": m.manuscript_id,
            "title": m.title,
            "authors": m.authors,
            "abstract": m.abstract,
            "subject": m.subject,
            "publish_time": m.update_time,
        }
        for m in manuscripts
    ]
    
    return ApiResponse.paginated(
        items=articles,
        total=total,
        page=page,
        page_size=page_size
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
    
    # 查询已发表的论文
    query = select(Manuscript).where(
        Manuscript.manuscript_id == article_id,
        Manuscript.status == ManuscriptStatus.PUBLISHED.value,
        Manuscript.is_deleted == False
    )
    result = await session.execute(query)
    manuscript = result.scalar_one_or_none()
    
    if not manuscript:
        raise HTTPException(status_code=404, detail="论文不存在或未发表")
    
    return ApiResponse.success(data={
        "article_id": manuscript.manuscript_id,
        "title": manuscript.title,
        "authors": manuscript.authors,
        "abstract": manuscript.abstract,
        "subject": manuscript.subject,
        "version": manuscript.version,
        "file_name": manuscript.file_name,
        "file_size": manuscript.file_size,
        "publish_time": manuscript.update_time,
        "create_time": manuscript.create_time,
    })


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
        query=query,
        page=page,
        size=page_size,
        filters=filters if filters else None
    )
    
    # 检查是否有错误
    if result.get("error"):
        return ApiResponse.error(
            message=f"搜索服务异常: {result.get('error')}",
            code=503
        )
    
    return ApiResponse.paginated(
        items=result.get("items", []),
        total=result.get("total", 0),
        page=result.get("page", page),
        page_size=result.get("size", page_size)
    )


@router.get("/info", summary="获取期刊信息")
async def get_journal_info():
    """
    获取期刊基本信息
    
    Returns:
        dict: 期刊信息
    """
    # TODO: 从数据库或配置读取期刊信息
    return ApiResponse.success(data={
        "name": "期刊平台",
        "description": "学术期刊投稿平台",
        "version": "1.0.0"
    })
