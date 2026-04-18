"""
管理员-稿件管理 API 接口

包含管理员的稿件列表、删除、已删除稿件管理等操作
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
from pathlib import Path
from datetime import datetime

from service.admin_log_service import admin_log_service
from api import dependencies as deps
from core.config import config

from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript
from database.repositories.manuscript_repo import ManuscriptRepository
from database.uow import transactional
from model.response import ApiResponse
from utils.log import global_logger

router = APIRouter(tags=["管理员-稿件管理"])

@router.get("/journals/all", summary="获取所有稿件列表")
async def get_all_journals(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有稿件列表，仅限管理员访问"""
    # 通过 Repository 查询所有稿件（含上传者信息）
    repo = ManuscriptRepository(session)
    manuscripts = await repo.list_all_with_author_page(
        page, page_size, status=status, include_deleted=False
    )

    # 查询总数
    conditions = [Manuscript.is_deleted == False]  # noqa: E712
    if status:
        conditions.append(Manuscript.status == status)
    total = await repo.count(*conditions)

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看所有稿件",
        operation_object=f"页码: {page}, 每页条数: {page_size}, 状态: {status if status else '全部'}",
        operation_details=f"查询了所有稿件，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    return ApiResponse.success(data={
        "total": total,
        "journals": manuscripts,
    })

@router.delete("/journals/{jid}", summary="删除稿件")
async def admin_delete_journal(
    jid: int,
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """删除稿件（软删除），仅限管理员访问"""
    # 通过 Repository 查询稿件
    repo = ManuscriptRepository(session)
    manuscript = await repo.get_by_manuscript_id(jid)

    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")

    async with transactional(session):
        manuscript.is_deleted = True
        manuscript.deleted_at = datetime.now().isoformat()
        manuscript.delete_reason = "管理员删除"
        manuscript.update_time = datetime.now().isoformat()
        global_logger.info("AdminJournals", f"稿件 {jid} 已被管理员 {current_user['username']} 软删除")

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="删除稿件",
        operation_object=f"稿件ID: {jid}",
        operation_details=f"将稿件 {manuscript.title} 标记为已删除",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    return ApiResponse.success(message="稿件删除成功")

@router.get("/review-records", summary="获取所有审核记录")
async def get_all_review_records(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有审核记录，仅限管理员访问

    TODO: 需要实现新的审稿意见模型查询
    当前使用 manuscripts 表作为占位，实际应查询 review_opinions 表
    """
    # TODO: 替换为实际的审稿意见查询
    # 临时返回空数据，等待审稿意见模型实现
    total = 0
    review_records = []

    global_logger.warning("AdminJournals", "审核记录查询功能待实现，需要迁移到新的审稿意见模型")

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看审核记录",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details="查询了所有审核记录（功能待完善）",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    return ApiResponse.success(data={
        "total": total,
        "records": review_records,
    })

@router.get("/journals/deleted", summary="获取已删除稿件列表")
async def get_deleted_journals(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取所有已删除稿件列表，仅限管理员访问"""
    # 通过 Repository 查询已删除稿件（含上传者信息）
    repo = ManuscriptRepository(session)
    total = await repo.count_deleted()
    manuscripts = await repo.list_deleted_with_author_page(page, page_size)

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看已删除稿件",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了已删除稿件，共 {total} 条",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    return ApiResponse.success(data={
        "total": total,
        "journals": manuscripts,
    })

@router.delete("/journals/deleted/{jid}", summary="彻底删除稿件")
async def permanently_delete_journal(
    jid: int,
    request: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """彻底删除已删除稿件，仅限管理员访问"""
    # 通过 Repository 查询已删除的稿件
    repo = ManuscriptRepository(session)
    manuscript = await repo.get_by_manuscript_id(jid, include_deleted=True)

    if not manuscript or not manuscript.is_deleted:
        raise HTTPException(status_code=404, detail="已删除稿件不存在")

    # 获取配置
    paper_dir = Path(config['global.global.literature_dir'])

    # 删除文件
    file_ext = Path(manuscript.file_name).suffix
    file_path = paper_dir / manuscript.file_bucket / f"{manuscript.file_hash}{file_ext}"
    if file_path.exists():
        file_path.unlink()
        global_logger.info("AdminJournals", f"已删除稿件文件: {file_path}")

    # 彻底删除稿件记录
    async with transactional(session):
        await session.delete(manuscript)
        global_logger.info("AdminJournals", f"稿件 {jid} 已被管理员 {current_user['username']} 彻底删除")

    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="彻底删除稿件",
        operation_object=f"稿件ID: {jid}",
        operation_details=f"彻底删除了稿件 {manuscript.title}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session=session,
    )

    return ApiResponse.success(message="稿件彻底删除成功")
