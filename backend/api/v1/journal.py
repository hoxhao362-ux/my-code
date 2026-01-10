from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from utils.jwt import jwt_util
from utils.generator import generator
from model.journal import (
    JournalUploadRequest, 
    JournalUploadResponse, 
    JournalInfo, 
    JournalListResponse,
    JournalStatusUpdateRequest
)

# 获取数据库服务实例
from database import db_manager
user_db = db_manager.get_service('user_account')
journal_db = db_manager.get_service('journal_submit')
deleted_journal_db = db_manager.get_service('deleted_journal')


journal_router = APIRouter(
    prefix="/journal",
    tags=["文献相关接口"],
)

@journal_router.get("/public", summary="获取公开文献列表", response_model=JournalListResponse)
async def get_public_journals(page: int = 1, page_size: int = 10):
    """获取已审核通过的公开文献列表"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await journal_db.fetchval(
        "SELECT COUNT(*) FROM journals WHERE status = 'published'"
    )
    
    # 查询文献列表
    journals = await journal_db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE status = 'published' 
        ORDER BY create_time DESC 
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**journal)
        for journal in journals
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )

@journal_router.get("/detail/{jid}", summary="获取文献详情", response_model=JournalInfo)
async def get_journal_detail(jid: int, token: str):
    """获取文献详情"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 查询文献
    journal = await journal_db.fetchone(
        """
        SELECT jid, uid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE jid = ?
        """,
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限
    if journal["status"] == "deleted":
        # 只有作者和管理员可以查看已删除文献
        if journal["uid"] != user_info["uid"] and user_info["role"] != "admin":
            raise HTTPException(status_code=403, detail="无权访问此文献")
    else:
        # 未删除文献：只有已发表的可以公开访问，其他状态只有作者可以访问
        if journal["status"] != "published" and journal["uid"] != user_info["uid"]:
            raise HTTPException(status_code=403, detail="无权访问此文献")
    
    return JournalInfo(**journal)

@journal_router.get("/search/title/{keyword}", summary="根据标题搜索文献", response_model=JournalListResponse)  
async def search_journals(keyword: str, page: int = 1, page_size: int = 10):
    """根据关键词搜索文献"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await journal_db.fetchval(
        """
        SELECT COUNT(*) FROM journals 
        WHERE (title LIKE ? OR abstract LIKE ?) 
        AND status != 'deleted'
        """,
        (f"%{keyword}%", f"%{keyword}%")
    )
    
    # 查询文献列表
    journals = await journal_db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE (title LIKE ? OR abstract LIKE ?) 
        AND status != 'deleted'
        ORDER BY create_time DESC 
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**journal)
        for journal in journals
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )

@journal_router.get("/search/author/{keyword}", summary="根据作者搜索文献", response_model=JournalListResponse)  
async def search_journals_by_author(keyword: str, page: int = 1, page_size: int = 10):
    """根据作者搜索文献"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await journal_db.fetchval(
        """
        SELECT COUNT(*) FROM journals 
        WHERE authors LIKE ? 
        AND status != 'deleted'
        """,
        (f"%{keyword}%",)
    )
    
    # 查询文献列表
    journals = await journal_db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE authors LIKE ? 
        AND status != 'deleted'
        ORDER BY create_time DESC 
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**journal)
        for journal in journals
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )

@journal_router.get("/search/sub/{subject}", summary="根据学科搜索文献", response_model=JournalListResponse)  
async def search_journals_by_subject(subject: str, page: int = 1, page_size: int = 10):
    """根据学科搜索文献"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await journal_db.fetchval(
        """
        SELECT COUNT(*) FROM journals 
        WHERE subject = ? 
        AND status != 'deleted'
        """,
        (subject,)
    )
    
    # 查询文献列表
    journals = await journal_db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE subject = ? 
        AND status != 'deleted'
        ORDER BY create_time DESC 
        LIMIT ? OFFSET ?
        """,
        (page_size, offset)
    )
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**journal)
        for journal in journals
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )
