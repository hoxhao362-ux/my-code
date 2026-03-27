from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
from pathlib import Path
from datetime import datetime

from service.admin_log_service import admin_log_service
from api import dependencies as deps
from core.config import config

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session
from database.orm.models.deleted_journal import DeletedJournal
from database.orm.models.journal import Journal, ReviewRecord
from database.orm.models.user import User
from database.repositories.journal_repo import JournalRepository
from database.repositories.review_repo import ReviewRepository
from database.uow import transactional
from model.response import ApiResponse

router = APIRouter(tags=["管理员-文献管理"])

@router.get("/journals/all", summary="获取所有文献列表")
async def get_all_journals(
    request: Request,
    page: int = 1, 
    page_size: int = 10, 
    status: Optional[str] = None, 
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有文献列表，仅限管理员访问"""
    journal_repo = JournalRepository(session)
    total = await journal_repo.count_all(status=status)
    journals = await journal_repo.list_all_with_uploader_page(page=page, page_size=page_size, status=status)
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看所有文献",
        operation_object=f"页码: {page}, 每页条数: {page_size}, 状态: {status if status else '全部'}",
        operation_details=f"查询了所有文献，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    return ApiResponse.success(data={
        "total": total,
        "journals": journals,
    })

@router.delete("/journals/{jid}", summary="删除文献")
async def admin_delete_journal(
    jid: int, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """删除文献（软删除），仅限管理员访问"""
    journal_repo = JournalRepository(session)
    journal = await journal_repo.get_by_id(jid)
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    async with transactional(session):
        journal.status = "deleted"
        journal.update_time = datetime.now().isoformat()

        session.add(
            DeletedJournal(
                original_jid=journal.jid,
                uid=journal.uid,
                title=journal.title,
                authors=journal.authors,
                abstract=journal.abstract,
                file_hash=journal.file_hash,
                file_bucket=journal.file_bucket,
                file_name=journal.file_name,
                file_size=journal.file_size,
                delete_time=datetime.now().isoformat(),
                delete_reason=None,
            )
        )
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="删除文献",
        operation_object=f"文献ID: {jid}",
        operation_details=f"将文献 {journal.title} 标记为已删除",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    return ApiResponse.success(message="文献删除成功")

@router.get("/review-records", summary="获取所有审核记录")
async def get_all_review_records(
    request: Request,
    page: int = 1, 
    page_size: int = 10, 
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有审核记录，仅限管理员访问"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询审核记录总数
    review_repo = ReviewRepository(session)
    total = await review_repo.count_all_records()
    review_records = await review_repo.list_all_records_page(page=page, page_size=page_size)
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看审核记录",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了所有审核记录，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    return ApiResponse.success(data={
        "total": total,
        "records": review_records,
    })

@router.get("/journals/deleted", summary="获取已删除文献列表")
async def get_deleted_journals(
    request: Request,
    page: int = 1, 
    page_size: int = 10, 
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有已删除文献列表，仅限管理员访问"""
    journal_repo = JournalRepository(session)
    total = await journal_repo.count_deleted()
    journals = await journal_repo.list_deleted_with_uploader_page(page=page, page_size=page_size)
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看已删除文献",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了已删除文献，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    return ApiResponse.success(data={
        "total": total,
        "journals": journals,
    })

@router.delete("/journals/deleted/{jid}", summary="彻底删除文献")
async def permanently_delete_journal(
    jid: int, 
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """彻底删除已删除文献，仅限管理员访问"""
    journal_repo = JournalRepository(session)
    journal = await journal_repo.get_by_id(jid)
    
    if not journal or journal.status != "deleted":
        raise HTTPException(status_code=404, detail="已删除文献不存在")
    
    # 获取配置
    paper_dir = Path(config['global.global.literature_dir'])
    
    # 删除文件
    file_ext = Path(journal.file_name).suffix
    file_path = paper_dir / journal.file_bucket / f"{journal.file_hash}{file_ext}"
    if file_path.exists():
        file_path.unlink()
    
    # 删除审核记录
    async with transactional(session):
        await session.execute(delete(ReviewRecord).where(ReviewRecord.jid == jid))
        await session.execute(delete(Journal).where(Journal.jid == jid))
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="彻底删除文献",
        operation_object=f"文献ID: {jid}",
        operation_details=f"彻底删除了文献 {journal.title}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    
    return ApiResponse.success(message="文献彻底删除成功")
