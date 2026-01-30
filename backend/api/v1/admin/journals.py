from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
from pathlib import Path
from datetime import datetime

from utils.admin_log import record_admin_log
from database import db_manager
from core import dependencies as deps
from core.config import config

journal_db = db_manager.get_service('journal_submit')
deleted_journal_db = db_manager.get_service('deleted_journal')

router = APIRouter(tags=["管理员-文献管理"])

@router.get("/journals/all", summary="获取所有文献列表")
async def get_all_journals(
    request: Request,
    page: int = 1, 
    page_size: int = 10, 
    status: Optional[str] = None, 
    current_user: dict = Depends(deps.get_admin_user)
):
    """获取所有文献列表，仅限管理员访问"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 构建查询条件
    where_clause = "WHERE 1=1"
    params = []
    
    if status:
        where_clause += " AND status = $1"
        params.append(status)
    
    # 查询文献总数
    count_sql = f"SELECT COUNT(*) FROM journals {where_clause}"
    total = await journal_db.fetchval(count_sql, tuple(params))
    
    # 查询文献列表
    limit_idx = len(params) + 1
    offset_idx = limit_idx + 1
    
    journals_sql = f"""
    SELECT j.jid, j.title, j.authors, j.abstract, j.status, j.file_name, j.file_size, j.create_time, j.update_time, u.username as uploader
    FROM journals j
    JOIN users u ON j.uid = u.uid
    {where_clause}
    ORDER BY j.create_time DESC 
    LIMIT ${limit_idx} OFFSET ${offset_idx}
    """
    params.extend([page_size, offset])
    journals = await journal_db.fetchall(journals_sql, tuple(params))
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看所有文献",
        operation_object=f"页码: {page}, 每页条数: {page_size}, 状态: {status if status else '全部'}",
        operation_details=f"查询了所有文献，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "total": total,
        "journals": [dict(journal) for journal in journals]
    }

@router.delete("/journals/{jid}", summary="删除文献")
async def admin_delete_journal(
    jid: int, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user)
):
    """删除文献（软删除），仅限管理员访问"""
    # 查询文献
    journal = await journal_db.fetchone(
        "SELECT jid, uid, title, authors, abstract, file_hash, file_bucket, file_name, file_size FROM journals WHERE jid = $1",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 软删除：将文献状态改为deleted
    await journal_db.execute(
        "UPDATE journals SET status = 'deleted', update_time = $1 WHERE jid = $2",
        (datetime.now().isoformat(), jid)
    )
    
    # 将已删除文献信息添加到已删除文献表
    await deleted_journal_db.execute(
        """
        INSERT INTO deleted_journals (
            original_jid, uid, title, authors, abstract, file_hash, 
            file_bucket, file_name, file_size, delete_time
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
        (
            journal["jid"],
            journal["uid"],
            journal["title"],
            journal["authors"],
            journal["abstract"],
            journal["file_hash"],
            journal["file_bucket"],
            journal["file_name"],
            journal["file_size"],
            datetime.now().isoformat()
        )
    )
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="删除文献",
        operation_object=f"文献ID: {jid}",
        operation_details=f"将文献 {journal['title']} 标记为已删除",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "文献删除成功"}

@router.get("/review-records", summary="获取所有审核记录")
async def get_all_review_records(
    request: Request,
    page: int = 1, 
    page_size: int = 10, 
    current_user: dict = Depends(deps.get_admin_user)
):
    """获取所有审核记录，仅限管理员访问"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询审核记录总数
    total = await journal_db.fetchval("SELECT COUNT(*) FROM review_records")
    
    # 查询审核记录
    review_records = await journal_db.fetchall(
        """
        SELECT rr.*, j.title, u.username as reviewer_name
        FROM review_records rr
        JOIN journals j ON rr.jid = j.jid
        JOIN users u ON rr.reviewer_uid = u.uid
        ORDER BY rr.review_time DESC
        LIMIT $1 OFFSET $2
        """,
        (page_size, offset)
    )
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看审核记录",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了所有审核记录，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "total": total,
        "records": [dict(record) for record in review_records]
    }

@router.get("/journals/deleted", summary="获取已删除文献列表")
async def get_deleted_journals(
    request: Request,
    page: int = 1, 
    page_size: int = 10, 
    current_user: dict = Depends(deps.get_admin_user)
):
    """获取所有已删除文献列表，仅限管理员访问"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 从主数据库查询已删除文献
    # 查询文献总数
    total = await journal_db.fetchval("SELECT COUNT(*) FROM journals WHERE status = 'deleted'")
    
    # 查询文献列表
    journals = await journal_db.fetchall(
        """
        SELECT j.jid, j.title, j.authors, j.abstract, j.status, j.file_name, j.file_size, j.create_time, j.update_time, u.username as uploader
        FROM journals j
        JOIN users u ON j.uid = u.uid
        WHERE j.status = 'deleted'
        ORDER BY j.update_time DESC 
        LIMIT $1 OFFSET $2
        """,
        (page_size, offset)
    )
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看已删除文献",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了已删除文献，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "total": total,
        "journals": [dict(journal) for journal in journals]
    }

@router.delete("/journals/deleted/{jid}", summary="彻底删除文献")
async def permanently_delete_journal(
    jid: int, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user)
):
    """彻底删除已删除文献，仅限管理员访问"""
    # 查询文献
    journal = await journal_db.fetchone(
        "SELECT jid, uid, title, file_hash, file_bucket, file_name FROM journals WHERE jid = $1 AND status = 'deleted'",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="已删除文献不存在")
    
    # 获取配置
    paper_dir = Path(config['global.global.papers_dir'])
    
    # 删除文件
    file_ext = Path(journal["file_name"]).suffix
    file_path = paper_dir / journal["file_bucket"] / f"{journal['file_hash']}{file_ext}"
    if file_path.exists():
        file_path.unlink()
    
    # 删除审核记录
    await journal_db.execute("DELETE FROM review_records WHERE jid = $1", (jid,))
    
    # 从主表中彻底删除文献
    await journal_db.execute("DELETE FROM journals WHERE jid = $1", (jid,))
    
    # 记录管理员操作日志
    await record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="彻底删除文献",
        operation_object=f"文献ID: {jid}",
        operation_details=f"彻底删除了文献 {journal['title']}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "文献彻底删除成功"}
