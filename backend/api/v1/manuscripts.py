"""
稿件中心相关 API 接口

包含稿件投稿、流转、文件管理等功能
TODO: 需要根据新枚举和数据库模型进一步完善
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from core.config import config
from core.enums import UserRole, ManuscriptStatus, FileContentType
from utils.jwt import jwt_util
from service.redis_service import redis_service
from utils.generator import generator
from api import dependencies as deps
from utils.log import global_logger

from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session
from database.orm.models.journal import Journal
from database.repositories.journal_repo import JournalRepository
from database.uow import transactional

# 创建稿件中心路由
router = APIRouter(
    prefix="/manuscripts",
    tags=["稿件中心相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
    },
)


@router.get("/", summary="获取稿件列表")
async def get_manuscript_list(
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取稿件列表
    
    功能说明：
    1. 作者：查看自己的稿件
    2. 编辑/审稿人：查看所有稿件（可筛选）
    
    Args:
        page: 页码
        page_size: 每页数量
        status: 状态筛选（可选）
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 稿件列表（分页）
    """
    # TODO: 需要根据新角色权限细化查询逻辑
    repo = JournalRepository(session)
    
    if current_user["role"] == UserRole.AUTHOR.value:
        # 作者只能看自己的
        total = await repo.count_by_uploader(current_user["uid"])
        manuscripts = await repo.list_by_uploader_page(current_user["uid"], page, page_size)
    else:
        # 编辑/审稿人可以看所有
        total = await repo.count_all()
        # TODO: 实现分页查询所有稿件
        
    global_logger.debug("Manuscripts", f"获取稿件列表 - uid: {current_user['uid']}, total: {total}")
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "manuscripts": []  # TODO: 转换为响应格式
    }


@router.post("/", summary="创建/上传稿件")
async def create_manuscript(
    title: str = Form(...),
    authors: str = Form(...),
    abstract: str | None = Form(None),
    subject: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    创建/上传新稿件
    
    功能说明：
    1. 检查文件类型（PDF/Word）
    2. 生成文件哈希并存储
    3. 创建稿件记录
    
    Args:
        title: 稿件标题
        authors: 作者列表
        abstract: 摘要
        subject: 学科/主题
        file: 稿件文件
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 稿件 ID 和基本信息
    """
    # 检查文件类型
    if not FileContentType.is_allowed(file.content_type):
        raise HTTPException(status_code=400, detail="只支持 PDF 和 Word 文档")
    
    # 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)
    
    # 生成文件哈希
    file_hash = generator.generate_file_hash(file_content)
    
    # 计算哈希分桶
    file_bucket_1 = file_hash[:2]
    file_bucket_2 = file_hash[2:4]
    
    # 获取配置
    papers_dir = Path(config["global.global.papers_dir"])
    
    # 创建存储目录
    bucket_dir = papers_dir / file_bucket_1 / file_bucket_2
    bucket_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_ext = Path(file.filename).suffix
    file_path = bucket_dir / f"{file_hash}{file_ext}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 生成 jid
    jid = generator.generate_jid()
    create_time = datetime.now().isoformat()
    
    # 插入数据库
    journal_repo = JournalRepository(session)
    async with transactional(session):
        journal = Journal(
            jid=int(jid),
            uid=current_user["uid"],
            title=title,
            authors=authors,
            subject=subject,
            abstract=abstract,
            file_hash=file_hash,
            file_bucket=f"{file_bucket_1}/{file_bucket_2}",
            file_name=file.filename,
            file_size=file_size,
            status=ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
            create_time=create_time,
            update_time=None,
        )
        journal_repo.add(journal)
    
    global_logger.info("Manuscripts", f"稿件上传成功 - jid: {jid}, uid: {current_user['uid']}, title: {title}")
    
    return {
        "jid": int(jid),
        "title": title,
        "status": ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
        "upload_time": create_time
    }


@router.get("/{manuscript_id}", summary="获取稿件详情")
async def get_manuscript_detail(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取指定稿件的详细信息
    
    Args:
        manuscript_id: 稿件 ID
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 稿件详细信息
    """
    # TODO: 实现详情查询
    return {"manuscript_id": manuscript_id}


@router.post("/{manuscript_id}/workflow", summary="稿件流转操作")
async def manuscript_workflow(
    manuscript_id: int,
    action: str = Form(...),
    data: dict = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    稿件流转核心接口
    
    支持的动作：
    - save: 保存草稿
    - submit: 提交稿件
    - withdraw: 撤稿
    - screen: 初审筛选
    - assign: 分配审稿人
    - review: 提交评审意见
    - decide: 编辑决策
    - revise: 请求修改
    - approve: 录用确认
    - publish: 出版
    
    Args:
        manuscript_id: 稿件 ID
        action: 流转动作
        data: 动作相关数据
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 操作结果
    """
    # TODO: 实现完整的流转逻辑
    global_logger.info("Manuscripts", f"稿件流转操作 - mid: {manuscript_id}, action: {action}, uid: {current_user['uid']}")
    
    return {"message": f"动作 {action} 执行成功"}


@router.get("/{manuscript_id}/files", summary="获取稿件附件列表")
async def get_manuscript_files(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
):
    """获取稿件的所有附件"""
    # TODO: 实现附件管理
    return {"manuscript_id": manuscript_id, "files": []}


@router.post("/{manuscript_id}/files", summary="上传稿件附件")
async def upload_manuscript_file(
    manuscript_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(deps.get_current_active_user),
):
    """上传稿件附件"""
    # TODO: 实现附件上传
    return {"message": "附件上传成功"}


@router.get("/{manuscript_id}/history", summary="获取稿件操作历史")
async def get_manuscript_history(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取稿件的操作历史记录"""
    # TODO: 实现操作历史查询
    return {"manuscript_id": manuscript_id, "history": []}
