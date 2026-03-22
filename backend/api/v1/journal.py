from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies as deps
from database.dependencies import get_db_session
from database.orm.models.journal import Journal
from database.repositories.journal_repo import JournalRepository

from model.journal import (
    JournalUploadRequest, 
    JournalUploadResponse, 
    JournalInfo, 
    JournalListResponse,
    JournalStatusUpdateRequest
)

journal_router = APIRouter(
    prefix="/journal",
    tags=["文献相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
)

@journal_router.get("/public", summary="获取公开文献列表", response_model=JournalListResponse)
async def get_public_journals(
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_db_session),
):
    """获取已审核通过的公开文献列表"""
    repo = JournalRepository(session)
    total = await repo.count_public()
    rows = await repo.list_public_page(page, page_size)
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**dict(row))
        for row in rows
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )

@journal_router.get("/detail/{jid}", summary="获取文献详情", response_model=JournalInfo)
async def get_journal_detail(
    jid: int,
    current_user: dict = Depends(deps.get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取文献详情"""
    repo = JournalRepository(session)
    journal = await repo.get_by_id(jid)
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限
    if journal.status == "deleted":
        # 只有作者和管理员可以查看已删除文献
        if journal.uid != current_user["uid"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="无权访问此文献")
    else:
        # 未删除文献：只有已发表的可以公开访问，其他状态只有作者可以访问
        if journal.status != "published" and journal.uid != current_user["uid"]:
            raise HTTPException(status_code=403, detail="无权访问此文献")
    
    return JournalInfo(
        jid=journal.jid,
        title=journal.title,
        authors=journal.authors,
        abstract=journal.abstract,
        status=journal.status,
        file_name=journal.file_name,
        file_size=journal.file_size,
        upload_time=journal.create_time,
        update_time=journal.update_time,
    )

@journal_router.get("/search/title/{keyword}", summary="根据标题搜索文献", response_model=JournalListResponse)  
async def search_journals(
    keyword: str,
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_db_session),
):
    """根据关键词搜索文献"""
    repo = JournalRepository(session)
    total = await repo.count_search_title_or_abstract(keyword)
    rows = await repo.list_search_title_or_abstract_page(keyword, page, page_size)
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**dict(row))
        for row in rows
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )

@journal_router.get("/search/author/{keyword}", summary="根据作者搜索文献", response_model=JournalListResponse)  
async def search_journals_by_author(
    keyword: str,
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_db_session),
):
    """根据作者搜索文献"""
    repo = JournalRepository(session)
    total = await repo.count_search_author(keyword)
    rows = await repo.list_search_author_page(keyword, page, page_size)
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**dict(row))
        for row in rows
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )

@journal_router.get("/search/sub/{subject}", summary="根据学科搜索文献", response_model=JournalListResponse)  
async def search_journals_by_subject(
    subject: str,
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_db_session),
):
    """根据学科搜索文献"""
    repo = JournalRepository(session)
    total = await repo.count_search_subject(subject)
    rows = await repo.list_search_subject_page(subject, page, page_size)
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**dict(row))
        for row in rows
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )
