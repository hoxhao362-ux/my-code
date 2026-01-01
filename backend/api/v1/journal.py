from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import os
from datetime import datetime
from pathlib import Path

from utils.database import db
from utils.jwt import jwt_util
from utils.generator import generator
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
)

@journal_router.post("/upload", summary="上传文献", response_model=JournalUploadResponse)
async def upload_journal(
    token: str,
    title: str = Form(..., description="文献标题"),
    authors: str = Form(..., description="文献作者，多个作者用逗号分隔"),
    abstract: Optional[str] = Form(None, description="文献摘要"),
    file: UploadFile = File(..., description="文献文件")
):
    """上传文献接口"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查文件类型
    allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持PDF和Word文档")
    
    # 获取配置
    from main import global_config
    paper_dir = Path(global_config['global']['paper_dir'])
    
    # 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)
    
    # 生成文件哈希
    file_hash = generator.generate_file_hash(file_content)
    
    # 计算哈希分桶，使用哈希值的前2位作为桶名
    file_bucket = file_hash[:2]
    
    # 创建存储目录（基于哈希分桶）
    bucket_dir = paper_dir / file_bucket
    bucket_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_ext = Path(file.filename).suffix
    file_path = bucket_dir / f"{file_hash}{file_ext}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 记录上传时间
    create_time = datetime.now().isoformat()
    
    # 插入文献数据
    await db.execute(
        """
        INSERT INTO journals (uid, title, authors, abstract, file_hash, file_bucket, file_name, file_size, create_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_info["uid"],
            title,
            authors,
            abstract,
            file_hash,
            file_bucket,
            file.filename,
            file_size,
            create_time
        )
    )
    await db.commit()
    
    # 获取新上传文献的ID
    jid = await db.fetchval("SELECT last_insert_rowid()")
    
    return JournalUploadResponse(
        jid=jid,
        title=title,
        status="pending",
        upload_time=datetime.now()
    )

@journal_router.get("/my", summary="获取我的文献列表", response_model=JournalListResponse)
async def get_my_journals(token: str, page: int = 1, page_size: int = 10):
    """获取当前用户上传的文献列表"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await db.fetchval(
        "SELECT COUNT(*) FROM journals WHERE uid = ?",
        (user_info["uid"],)
    )
    
    # 查询文献列表
    journals = await db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE uid = ? 
        ORDER BY create_time DESC 
        LIMIT ? OFFSET ?
        """,
        (user_info["uid"], page_size, offset)
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
    journal = await db.fetchone(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE jid = ?
        """,
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限
    if journal["status"] != "approved" and journal["uid"] != user_info["uid"]:
        raise HTTPException(status_code=403, detail="无权访问此文献")
    
    return JournalInfo(**journal)

@journal_router.delete("/{jid}", summary="删除文献")
async def delete_journal(jid: int, token: str):
    """删除文献"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 查询文献
    journal = await db.fetchone(
        "SELECT uid, file_hash, file_bucket, file_name FROM journals WHERE jid = ?",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限
    if journal["uid"] != user_info["uid"] and user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权删除此文献")
    
    # 获取配置
    from main import global_config
    paper_dir = Path(global_config['global']['paper_dir'])
    
    # 删除文件
    file_ext = Path(journal["file_name"]).suffix
    file_path = paper_dir / journal["file_bucket"] / f"{journal['file_hash']}{file_ext}"
    if file_path.exists():
        file_path.unlink()
    
    # 删除文献数据
    await db.execute("DELETE FROM journals WHERE jid = ?", (jid,))
    await db.commit()
    
    return {"message": "文献删除成功"}

@journal_router.get("/public", summary="获取公开文献列表", response_model=JournalListResponse)
async def get_public_journals(page: int = 1, page_size: int = 10):
    """获取已审核通过的公开文献列表"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await db.fetchval(
        "SELECT COUNT(*) FROM journals WHERE status = 'approved'"
    )
    
    # 查询文献列表
    journals = await db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE status = 'approved' 
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
