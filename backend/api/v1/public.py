"""
公共接口相关 API 接口

包含期刊列表、论文检索等公开访问功能
"""
from fastapi import APIRouter, Query

from api import dependencies as deps
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
):
    """
    获取公开的期刊列表
    
    Args:
        page: 页码
        page_size: 每页数量
        subject: 学科筛选
        
    Returns:
        dict: 期刊列表
    """
    # TODO: 实现期刊列表查询
    global_logger.debug("Public", f"获取期刊列表 - page: {page}, subject: {subject}")
    
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "journals": []
    }


@router.get("/articles", summary="获取已发表论文列表")
async def get_published_articles(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
):
    """
    获取已发表的论文列表
    
    Args:
        page: 页码
        page_size: 每页数量
        keyword: 关键词搜索
        
    Returns:
        dict: 论文列表
    """
    # TODO: 实现论文列表查询
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "articles": []
    }


@router.get("/search", summary="搜索论文")
async def search_articles(
    query: str = Query(..., description="搜索关键词"),
    page: int = 1,
    page_size: int = 10,
):
    """
    搜索论文（基于 Elasticsearch）
    
    Args:
        query: 搜索关键词
        page: 页码
        page_size: 每页数量
        
    Returns:
        dict: 搜索结果
    """
    # TODO: 实现 Elasticsearch 搜索
    global_logger.debug("Public", f"搜索论文 - query: {query}, page: {page}")
    
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "results": []
    }


@router.get("/info", summary="获取期刊信息")
async def get_journal_info():
    """
    获取期刊基本信息
    
    Returns:
        dict: 期刊信息
    """
    # TODO: 从数据库或配置读取期刊信息
    return {
        "name": "期刊平台",
        "description": "学术期刊投稿平台",
        "version": "1.0.0"
    }
