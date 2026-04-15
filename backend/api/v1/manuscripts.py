"""
稿件中心相关 API 接口

包含稿件投稿、流转、文件管理等功能
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import os
import tempfile
from datetime import datetime
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import config
from core.enums import UserRole, ManuscriptStatus, FileContentType, WorkflowAction
from utils.jwt import jwt_util
from service.redis_service import redis_service
from service.manuscript_service import manuscript_workflow_service
from service.pdf_service import pdf_service
from utils.generator import generator
from api import dependencies as deps
from model.response import ApiResponse
from utils.log import global_logger

from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript, ManuscriptFile
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
    offset = (page - 1) * page_size
    
    # 构建基础查询条件
    base_conditions = [Manuscript.is_deleted == False]
    
    if current_user["role"] == UserRole.AUTHOR.value:
        # 作者只能看自己的
        base_conditions.append(Manuscript.author_uid == current_user["uid"])
    
    if status:
        base_conditions.append(Manuscript.status == status)
    
    # 查询总数
    count_query = select(func.count()).select_from(Manuscript).where(*base_conditions)
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # 查询列表
    list_query = (
        select(Manuscript)
        .where(*base_conditions)
        .order_by(Manuscript.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    list_result = await session.execute(list_query)
    manuscripts = list_result.scalars().all()
    
    global_logger.debug("Manuscripts", f"获取稿件列表 - uid: {current_user['uid']}, total: {total}")
    
    # 转换为响应格式
    manuscript_list = [
        {
            "manuscript_id": m.manuscript_id,
            "title": m.title,
            "authors": m.authors,
            "subject": m.subject,
            "stage": m.stage,
            "status": m.status,
            "version": m.version,
            "create_time": m.create_time,
            "update_time": m.update_time,
        }
        for m in manuscripts
    ]
    
    return ApiResponse.paginated(
        items=manuscript_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", summary="创建/上传稿件")
async def create_manuscript(
    title: str = Form(...),
    article_type: str = Form("Research Article"),
    section_category: str | None = Form(None),
    keywords: str = Form(""),
    first_author: str = Form(""),
    corresponding_author: str = Form(""),
    order_of_authors: str = Form("[]"),
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
        article_type: 文章类型
        section_category: 栏目/类别
        keywords: 关键字
        first_author: 第一作者
        corresponding_author: 通讯作者
        order_of_authors: 作者排序
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
    papers_dir = Path(config["global.global.literature_dir"])
    
    # 创建存储目录
    bucket_dir = papers_dir / file_bucket_1 / file_bucket_2
    bucket_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_ext = Path(file.filename).suffix
    file_path = bucket_dir / f"{file_hash}{file_ext}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 生成 manuscript_id
    manuscript_id = generator.generate_jid()
    create_time = datetime.now().isoformat()
    
    # 插入数据库
    async with transactional(session):
        manuscript = Manuscript(
            manuscript_id=int(manuscript_id),
            author_uid=current_user["uid"],
            title=title,
            article_type=article_type,
            section_category=section_category,
            keywords=keywords,
            first_author=first_author,
            corresponding_author=corresponding_author,
            order_of_authors=order_of_authors,
            authors=authors,
            subject=subject,
            abstract=abstract,
            stage="initial_review",
            status=ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
            version=1,
            file_hash=file_hash,
            file_bucket=f"{file_bucket_1}/{file_bucket_2}",
            file_name=file.filename,
            file_size=file_size,
            create_time=create_time,
            update_time=None,
            is_deleted=False,
            deleted_at=None,
            delete_reason=None,
        )
        session.add(manuscript)
    
    global_logger.info("Manuscripts", f"稿件上传成功 - manuscript_id: {manuscript_id}, uid: {current_user['uid']}, title: {title}")
    
    return ApiResponse.success(data={
        "manuscript_id": int(manuscript_id),
        "title": title,
        "status": ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
        "upload_time": create_time
    })


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
    # 查询稿件
    query = select(Manuscript).where(
        Manuscript.manuscript_id == manuscript_id,
        Manuscript.is_deleted == False
    )
    result = await session.execute(query)
    manuscript = result.scalar_one_or_none()
    
    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")
    
    # 权限检查：作者只能查看自己的稿件
    if current_user["role"] == UserRole.AUTHOR.value and manuscript.author_uid != current_user["uid"]:
        raise HTTPException(status_code=403, detail="无权查看此稿件")
    
    return ApiResponse.success(data={
        "manuscript_id": manuscript.manuscript_id,
        "author_uid": manuscript.author_uid,
        "title": manuscript.title,
        "article_type": manuscript.article_type,
        "section_category": manuscript.section_category,
        "keywords": manuscript.keywords,
        "first_author": manuscript.first_author,
        "corresponding_author": manuscript.corresponding_author,
        "order_of_authors": manuscript.order_of_authors,
        "authors": manuscript.authors,
        "abstract": manuscript.abstract,
        "subject": manuscript.subject,
        "stage": manuscript.stage,
        "status": manuscript.status,
        "version": manuscript.version,
        "file_hash": manuscript.file_hash,
        "file_bucket": manuscript.file_bucket,
        "file_name": manuscript.file_name,
        "file_size": manuscript.file_size,
        "create_time": manuscript.create_time,
        "update_time": manuscript.update_time,
    })


@router.get("/{manuscript_id}/actions", summary="获取稿件可执行动作")
async def get_manuscript_actions(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取当前稿件可执行的动作列表
    
    根据稿件当前状态和用户角色，返回允许执行的动作列表。
    
    Args:
        manuscript_id: 稿件 ID
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 可执行的动作列表
    """
    # 查询稿件
    query = select(Manuscript).where(
        Manuscript.manuscript_id == manuscript_id,
        Manuscript.is_deleted == False
    )
    result = await session.execute(query)
    manuscript = result.scalar_one_or_none()
    
    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")
    
    # 权限检查：作者只能查看自己的稿件
    if current_user["role"] == UserRole.AUTHOR.value and manuscript.author_uid != current_user["uid"]:
        raise HTTPException(status_code=403, detail="无权查看此稿件")
    
    # 获取允许的动作
    allowed_actions = manuscript_workflow_service.get_allowed_actions(
        manuscript.status, current_user["role"]
    )
    
    global_logger.debug(
        "Manuscripts", 
        f"获取可执行动作 - mid: {manuscript_id}, status: {manuscript.status}, "
        f"role: {current_user['role']}, actions: {allowed_actions}"
    )
    
    return ApiResponse.success(data={
        "manuscript_id": manuscript_id,
        "current_status": manuscript.status,
        "current_stage": manuscript.stage,
        "allowed_actions": allowed_actions,
        "action_descriptions": {
            WorkflowAction.SAVE.value: "保存草稿",
            WorkflowAction.SUBMIT.value: "提交稿件",
            WorkflowAction.WITHDRAW.value: "撤稿",
            WorkflowAction.SCREEN.value: "初审筛选",
            WorkflowAction.ASSIGN.value: "分配审稿人",
            WorkflowAction.REVIEW.value: "提交评审意见",
            WorkflowAction.DECIDE.value: "编辑决策",
            WorkflowAction.REVISE.value: "提交修改稿",
            WorkflowAction.APPROVE.value: "录用确认",
            WorkflowAction.PUBLISH.value: "出版",
        }
    })


@router.post("/{manuscript_id}/workflow", summary="稿件流转操作")
async def manuscript_workflow(
    manuscript_id: int,
    action: str = Form(...),
    decision_type: Optional[str] = Form(None),
    comment: Optional[str] = Form(None),
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
    - decide: 编辑决策（需要 decision_type: accept/reject/revision/transfer）
    - revise: 提交修改稿
    - approve: 录用确认
    - publish: 出版
    
    Args:
        manuscript_id: 稿件 ID
        action: 流转动作
        decision_type: 决策类型（decide 动作需要）
        comment: 备注信息
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 操作结果
    """
    global_logger.info(
        "Manuscripts", 
        f"稿件流转操作 - mid: {manuscript_id}, action: {action}, "
        f"decision_type: {decision_type}, uid: {current_user['uid']}"
    )
    
    try:
        async with transactional(session):
            result = await manuscript_workflow_service.execute_action(
                manuscript_id=manuscript_id,
                action=action,
                user_id=current_user["uid"],
                user_role=current_user["role"],
                session=session,
                decision_type=decision_type,
                comment=comment,
            )
        
        global_logger.info(
            "Manuscripts",
            f"稿件流转成功 - mid: {manuscript_id}, {result['old_status']} -> {result['new_status']}"
        )
        
        return ApiResponse.success(data=result)
        
    except ValueError as e:
        global_logger.warning(
            "Manuscripts",
            f"稿件流转失败 - mid: {manuscript_id}, action: {action}, error: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{manuscript_id}/files", summary="获取稿件附件列表")
async def get_manuscript_files(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
):
    """获取稿件的所有附件"""
    # TODO: 实现附件管理
    return ApiResponse.success(data={"manuscript_id": manuscript_id, "files": []})


@router.post("/{manuscript_id}/files", summary="上传稿件附件")
async def upload_manuscript_file(
    manuscript_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(deps.get_current_active_user),
):
    """上传稿件附件"""
    # TODO: 实现附件上传
    return ApiResponse.success(message="附件上传成功")


@router.get("/{manuscript_id}/history", summary="获取稿件操作历史")
async def get_manuscript_history(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取稿件的操作历史记录"""
    # TODO: 实现操作历史查询
    return ApiResponse.success(data={"manuscript_id": manuscript_id, "history": []})

@router.post("/preview-pdf", summary="预览合并后的正式 PDF")
async def preview_merged_pdf(
    title: str = Form(...),
    article_type: str = Form("Research Article"),
    section_category: str | None = Form(None),
    keywords: str = Form(""),
    first_author: str = Form(""),
    corresponding_author: str = Form(""),
    order_of_authors: str = Form("[]"),
    authors: str = Form(""),
    abstract: str | None = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(deps.get_current_active_user),
):
    """
    高阶 PDF 合成与预览接口
    
    接收用户提交的稿件元数据和正文文件，动态生成符合学术规范的封面，
    并与正文合并为单一 PDF 返回给前端进行预览。此接口不保存数据到数据库。
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="未上传文件")
        
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".doc", ".docx"]:
        raise HTTPException(status_code=400, detail="只支持 PDF 和 Word 文档转换")
        
    try:
        # 使用临时目录来处理文件，避免占用存储空间
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. 保存上传的原文件
            input_file_path = os.path.join(temp_dir, f"input{ext}")
            content = await file.read()
            with open(input_file_path, "wb") as f:
                f.write(content)
                
            # 2. 转换为 PDF (如果已经是 PDF，则内部会直接返回原路径)
            main_pdf_path = pdf_service.convert_to_pdf(input_file_path, temp_dir)
            
            # 3. 生成封面 PDF
            cover_pdf_path = os.path.join(temp_dir, "cover.pdf")
            data = {
                "title": title,
                "article_type": article_type,
                "section_category": section_category,
                "keywords": keywords,
                "first_author": first_author,
                "corresponding_author": corresponding_author,
                "order_of_authors": order_of_authors,
                "authors": authors,
                "abstract": abstract
            }
            pdf_service.generate_cover_pdf(data, cover_pdf_path)
            
            # 4. 合并 PDF
            merged_pdf_path = os.path.join(temp_dir, "merged.pdf")
            pdf_service.merge_pdfs([cover_pdf_path, main_pdf_path], merged_pdf_path)
            
            # 5. 读取合并后的内容并作为流返回
            with open(merged_pdf_path, "rb") as f:
                pdf_content = f.read()
                
            # 清理临时文件由 TemporaryDirectory 上下文管理器自动完成
            
        def iterfile():
            yield pdf_content
            
        return StreamingResponse(
            iterfile(), 
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=preview_merged.pdf"
            }
        )
        
    except Exception as e:
        global_logger.error("Manuscripts", f"PDF 合成预览失败: {e}")
        raise HTTPException(status_code=500, detail=f"PDF 处理失败: {str(e)}")

