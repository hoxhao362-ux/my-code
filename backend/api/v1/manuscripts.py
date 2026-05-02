"""
稿件中心相关 API 接口

包含稿件投稿、流转、文件管理等功能
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from api import dependencies as deps
from core.config import config
from core.enums import (FileContentType, ManuscriptStatus, NotificationType,
                        UserRole, WorkflowAction)
from database.dependencies import get_db_session
from database.orm.models.editorial import DecisionRecord
from database.orm.models.manuscript import (Manuscript, ManuscriptFile)
from database.orm.models.user import User
from database.repositories.manuscript_participant_repo import (
    ManuscriptParticipantRepository,
)
from database.repositories.manuscript_repo import ManuscriptRepository
from database.repositories.review_opinion_repo import ReviewOpinionRepository
from database.repositories.user_repo import UserRepository
from database.uow import transactional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from model.manuscript import ManuscriptDetailDTO, ManuscriptListItemDTO
from model.response import ApiResponse
from service.manuscript_service import manuscript_workflow_service
from service.manuscript_access import (user_can_upload_manuscript_file,
                                       user_can_view_manuscript)
from service.notification_service import create_notification
from service.pdf_service import pdf_service
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.generator import generator
from utils.log import global_logger

# ========== 文件上传配置 ==========
# 文件大小限制配置（字节）
FILE_SIZE_LIMITS = {
    "application/pdf": 20 * 1024 * 1024,  # PDF: 20MB
    "application/msword": 10 * 1024 * 1024,  # Word .doc: 10MB
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": 10
    * 1024
    * 1024,  # Word .docx: 10MB
    "image/jpeg": 10 * 1024 * 1024,  # JPEG: 10MB
    "image/png": 10 * 1024 * 1024,  # PNG: 10MB
}
DEFAULT_SIZE_LIMIT = 10 * 1024 * 1024  # 默认: 10MB
CHUNK_SIZE = 1024 * 1024  # 1MB 分块


async def read_file_with_limit(file: UploadFile, max_size: int) -> bytes:
    """
    流式读取上传文件，超出大小限制时抛出异常。

    Args:
        file: 上传的文件对象
        max_size: 最大允许的文件大小（字节）

    Returns:
        bytes: 文件内容

    Raises:
        HTTPException: 文件大小超出限制时抛出 413 错误
    """
    chunks = []
    total_size = 0

    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"文件大小超出限制（最大 {max_size // (1024 * 1024)}MB）",
            )
        chunks.append(chunk)

    return b"".join(chunks)


async def stream_file_to_path(
    file: UploadFile, target_path: Path, max_size: int
) -> int:
    """
    流式读取上传文件并直接写入目标路径，超出大小限制时抛出异常。

    Args:
        file: 上传的文件对象
        target_path: 目标文件路径
        max_size: 最大允许的文件大小（字节）

    Returns:
        int: 实际写入的文件大小

    Raises:
        HTTPException: 文件大小超出限制时抛出 413 错误
    """
    total_size = 0

    with open(target_path, "wb") as f:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > max_size:
                # 删除已写入的部分文件
                f.close()
                if target_path.exists():
                    target_path.unlink()
                raise HTTPException(
                    status_code=413,
                    detail=f"文件大小超出限制（最大 {max_size // (1024 * 1024)}MB）",
                )
            f.write(chunk)

    return total_size


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
    # 通过 Repository 查询稿件列表
    author_uid = (
        current_user["uid"] if current_user["role"] == UserRole.AUTHOR.value else None
    )
    repo = ManuscriptRepository(session)
    manuscripts, total = await repo.list_manuscript_page(
        page,
        page_size,
        author_uid=author_uid,
        status=status,
        order_by=Manuscript.create_time.desc(),
    )

    global_logger.debug(
        "Manuscripts", f"获取稿件列表 - uid: {current_user['uid']}, total: {total}"
    )

    # 使用 Pydantic DTO 转换为响应格式
    manuscript_list = [
        ManuscriptListItemDTO.model_validate(m).model_dump() for m in manuscripts
    ]

    return ApiResponse.paginated(
        items=manuscript_list, total=total, page=page, page_size=page_size
    )


@router.post(
    "/", summary="创建/上传稿件", dependencies=[Depends(deps.upload_rate_limit)]
)
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

    # 获取文件大小限制
    max_size = FILE_SIZE_LIMITS.get(file.content_type, DEFAULT_SIZE_LIMIT)

    # 使用流式读取文件内容
    file_content = await read_file_with_limit(file, max_size)
    file_size = len(file_content)

    # 记录文件上传信息
    global_logger.info(
        "Manuscripts",
        f"文件上传 - filename: {file.filename}, content_type: {file.content_type}, "
        f"size: {file_size} bytes ({file_size // 1024} KB)",
    )

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
    manuscript_id = await generator.generate_jid()
    create_time = datetime.now()

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

    global_logger.info(
        "Manuscripts",
        f"稿件上传成功 - manuscript_id: {manuscript_id}, uid: {current_user['uid']}, title: {title}",
    )

    return ApiResponse.success(
        data={
            "manuscript_id": int(manuscript_id),
            "title": title,
            "status": ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
            "upload_time": create_time,
        }
    )


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
    # 通过 Repository 查询稿件
    repo = ManuscriptRepository(session)
    manuscript = await repo.get_by_manuscript_id(manuscript_id)

    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")

    # 权限检查：作者只能查看自己的稿件
    if (
        current_user["role"] == UserRole.AUTHOR.value
        and manuscript.author_uid != current_user["uid"]
    ):
        raise HTTPException(status_code=403, detail="无权查看此稿件")

    # 使用 Pydantic DTO 转换为响应格式
    dto = ManuscriptDetailDTO.model_validate(manuscript)
    return ApiResponse.success(data=dto.model_dump())


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
    # 通过 Repository 查询稿件
    repo = ManuscriptRepository(session)
    manuscript = await repo.get_by_manuscript_id(manuscript_id)

    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")

    # 权限检查：作者只能查看自己的稿件
    if (
        current_user["role"] == UserRole.AUTHOR.value
        and manuscript.author_uid != current_user["uid"]
    ):
        raise HTTPException(status_code=403, detail="无权查看此稿件")

    # 获取允许的动作
    allowed_actions = manuscript_workflow_service.get_allowed_actions(
        manuscript.status, current_user["role"]
    )

    global_logger.debug(
        "Manuscripts",
        f"获取可执行动作 - mid: {manuscript_id}, status: {manuscript.status}, "
        f"role: {current_user['role']}, actions: {allowed_actions}",
    )

    return ApiResponse.success(
        data={
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
            },
        }
    )


@router.post("/{manuscript_id}/workflow", summary="稿件流转操作")
async def manuscript_workflow(
    manuscript_id: int,
    action: str = Form(...),
    decision_type: Optional[str] = Form(None),
    comment: Optional[str] = Form(None),
    reviewer_uids: Optional[str] = Form(
        None,
        description="assign 时必填：审稿人 uid 的 JSON 数组，如 [1,2]",
    ),
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    稿件流转核心接口。

    assign：须提供 reviewer_uids（JSON 数组）。在初审已通过 / 待送审 / 评审中
    均可追加审稿人；前两态会触发状态机前进，评审中仅写入参与者。
    """
    global_logger.info(
        "Manuscripts",
        f"稿件流转操作 - mid: {manuscript_id}, action: {action}, "
        f"decision_type: {decision_type}, uid: {current_user['uid']}",
    )

    if action == WorkflowAction.ASSIGN.value:
        if not reviewer_uids or not str(reviewer_uids).strip():
            raise HTTPException(
                status_code=400,
                detail="assign 动作需提供 reviewer_uids（JSON 数字数组）",
            )
        try:
            raw_list = json.loads(reviewer_uids)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="reviewer_uids 不是合法 JSON")
        if not isinstance(raw_list, list) or len(raw_list) == 0:
            raise HTTPException(status_code=400, detail="reviewer_uids 必须为非空数组")
        try:
            uid_list = list(dict.fromkeys(int(x) for x in raw_list))
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="reviewer_uids 元素须为整数")

        try:
            async with transactional(session):
                m_repo = ManuscriptRepository(session)
                ms = await m_repo.get_by_manuscript_id(manuscript_id)
                if not ms:
                    raise ValueError("稿件不存在")

                if not manuscript_workflow_service.validate_permission(
                    action, current_user["role"]
                ):
                    raise ValueError("无权分配审稿人")

                assign_ok = {
                    ManuscriptStatus.INITIAL_REVIEW_PASSED.value,
                    ManuscriptStatus.PENDING_PEER_REVIEW.value,
                    ManuscriptStatus.UNDER_PEER_REVIEW.value,
                }
                if ms.status not in assign_ok:
                    raise ValueError("当前稿件状态不可分配审稿人")

                u_repo = UserRepository(session)
                part_repo = ManuscriptParticipantRepository(session)

                for rid in uid_list:
                    assignee = await u_repo.get_by_id(rid)
                    if not assignee or assignee.is_deleted:
                        raise ValueError(f"用户不存在或已删除: {rid}")
                    if UserRole.get_role_level(assignee.role) < UserRole.get_role_level(
                        UserRole.REVIEWER.value
                    ):
                        raise ValueError(f"用户 {rid} 角色不具备审稿人资格")
                    await part_repo.upsert_reviewer(
                        manuscript_id, rid, current_user["uid"]
                    )
                    await create_notification(
                        session,
                        user_uid=rid,
                        notification_type=NotificationType.REVIEW_INVITATION.value,
                        title="审稿邀请",
                        content=f"您被邀请审阅稿件《{ms.title}》（编号 {manuscript_id}）。",
                        related_manuscript_id=manuscript_id,
                        log_tag="Manuscripts",
                    )

                if ms.status == ManuscriptStatus.INITIAL_REVIEW_PASSED.value:
                    wf_result = await manuscript_workflow_service.execute_action(
                        manuscript_id=manuscript_id,
                        action=action,
                        user_id=current_user["uid"],
                        user_role=current_user["role"],
                        session=session,
                        decision_type=decision_type,
                        comment=comment,
                    )
                elif ms.status == ManuscriptStatus.PENDING_PEER_REVIEW.value:
                    wf_result = await manuscript_workflow_service.execute_action(
                        manuscript_id=manuscript_id,
                        action=action,
                        user_id=current_user["uid"],
                        user_role=current_user["role"],
                        session=session,
                        decision_type=decision_type,
                        comment=comment,
                    )
                else:
                    wf_result = {
                        "success": True,
                        "manuscript_id": manuscript_id,
                        "action": action,
                        "decision_type": decision_type,
                        "old_status": ms.status,
                        "new_status": ms.status,
                        "old_stage": ms.stage,
                        "new_stage": ms.stage,
                        "version": ms.version,
                        "update_time": datetime.now(),
                        "note": "评审中仅追加审稿人，未变更稿件状态",
                    }

            global_logger.info(
                "Manuscripts",
                f"分配审稿人成功 - mid: {manuscript_id}, uids: {uid_list}, "
                f"status: {wf_result.get('old_status')} -> {wf_result.get('new_status')}",
            )
            return ApiResponse.success(data=wf_result)

        except ValueError as e:
            global_logger.warning(
                "Manuscripts",
                f"分配审稿人失败 - mid: {manuscript_id}, error: {e}",
            )
            raise HTTPException(status_code=400, detail=str(e))

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
            f"稿件流转成功 - mid: {manuscript_id}, {result['old_status']} -> {result['new_status']}",
        )

        return ApiResponse.success(data=result)

    except ValueError as e:
        global_logger.warning(
            "Manuscripts",
            f"稿件流转失败 - mid: {manuscript_id}, action: {action}, error: {str(e)}",
        )
        raise HTTPException(status_code=400, detail=str(e))


_ALLOWED_MANUSCRIPT_FILE_TYPES = frozenset(
    {"main", "attachment", "review", "letter", "other"}
)


@router.get("/{manuscript_id}/files", summary="获取稿件附件列表")
async def get_manuscript_files(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """返回附件元数据（不含 file_hash）。"""
    repo = ManuscriptRepository(session)
    manuscript = await repo.get_by_manuscript_id(manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")
    if not await user_can_view_manuscript(
        session,
        manuscript,
        current_user["uid"],
        current_user["role"],
    ):
        raise HTTPException(status_code=403, detail="无权查看该稿件附件")

    files = await repo.list_manuscript_files(manuscript_id)
    items = [
        {
            "file_id": f.file_id,
            "original_name": f.original_name,
            "file_size": f.file_size,
            "content_type": f.content_type,
            "file_type": f.file_type,
            "uploaded_by_uid": f.uploaded_by_uid,
            "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
            "description": f.description,
        }
        for f in files
    ]
    return ApiResponse.success(data={"manuscript_id": manuscript_id, "files": items})


@router.post("/{manuscript_id}/files", summary="上传稿件附件")
async def upload_manuscript_file(
    manuscript_id: int,
    file: UploadFile = File(...),
    file_type: str = Form("attachment"),
    description: str | None = Form(None),
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """上传 PDF/Word 附件；main 类型会同步更新稿件主文件字段。"""
    if file_type not in _ALLOWED_MANUSCRIPT_FILE_TYPES:
        raise HTTPException(status_code=400, detail="无效的文件类型")

    if not FileContentType.is_allowed(file.content_type or ""):
        raise HTTPException(status_code=400, detail="只支持 PDF 和 Word 文档")

    repo = ManuscriptRepository(session)
    manuscript = await repo.get_by_manuscript_id(manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")

    if not await user_can_upload_manuscript_file(
        manuscript,
        current_user["uid"],
        current_user["role"],
        file_type,
    ):
        raise HTTPException(status_code=403, detail="无权上传该类型附件")

    max_size = FILE_SIZE_LIMITS.get(file.content_type, DEFAULT_SIZE_LIMIT)
    file_content = await read_file_with_limit(file, max_size)
    file_size = len(file_content)
    file_hash = generator.generate_file_hash(file_content)
    file_bucket_1 = file_hash[:2]
    file_bucket_2 = file_hash[2:4]
    papers_dir = Path(config["global.global.literature_dir"])
    bucket_dir = papers_dir / file_bucket_1 / file_bucket_2
    bucket_dir.mkdir(parents=True, exist_ok=True)
    file_ext = Path(file.filename or "file").suffix or ".bin"
    file_path = bucket_dir / f"{file_hash}{file_ext}"
    with open(file_path, "wb") as fh:
        fh.write(file_content)

    uploaded_at = datetime.now()
    out_file_id: int | None = None
    out_name: str | None = None

    async with transactional(session):
        mf = ManuscriptFile(
            manuscript_id=manuscript_id,
            file_hash=file_hash,
            file_bucket=f"{file_bucket_1}/{file_bucket_2}",
            original_name=file.filename or "unnamed",
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            file_type=file_type,
            uploaded_by_uid=current_user["uid"],
            uploaded_at=uploaded_at,
            description=description,
        )
        session.add(mf)
        await session.flush()
        out_file_id = mf.file_id
        out_name = mf.original_name

        if file_type == "main":
            m = await repo.get_by_manuscript_id(manuscript_id)
            if m:
                m.file_hash = file_hash
                m.file_bucket = f"{file_bucket_1}/{file_bucket_2}"
                m.file_name = mf.original_name
                m.file_size = file_size
                m.update_time = uploaded_at

    global_logger.info(
        "Manuscripts",
        f"附件上传成功 mid={manuscript_id} type={file_type} uid={current_user['uid']}",
    )
    return ApiResponse.success(
        data={
            "file_id": out_file_id,
            "original_name": out_name,
            "file_size": file_size,
            "file_type": file_type,
            "uploaded_at": uploaded_at.isoformat(),
        },
        message="附件上传成功",
    )


@router.get("/{manuscript_id}/history", summary="获取稿件操作历史")
async def get_manuscript_history(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """合并版本、决策、审稿意见、参与者分配为时间线（审稿人视角脱敏他人意见）。"""
    m_repo = ManuscriptRepository(session)
    manuscript = await m_repo.get_by_manuscript_id(manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="稿件不存在")
    if not await user_can_view_manuscript(
        session,
        manuscript,
        current_user["uid"],
        current_user["role"],
    ):
        raise HTTPException(status_code=403, detail="无权查看该稿件历史")

    hide_foreign_opinions = current_user["role"] == UserRole.REVIEWER.value
    my_uid = current_user["uid"]

    versions = await m_repo.list_manuscript_versions(manuscript_id)
    d_rows = (
        (
            await session.execute(
                select(DecisionRecord)
                .where(DecisionRecord.manuscript_id == manuscript_id)
                .order_by(DecisionRecord.decided_at.asc())
            )
        )
        .scalars()
        .all()
    )
    opinion_repo = ReviewOpinionRepository(session)
    opinions = await opinion_repo.list_by_manuscript(manuscript_id)
    part_repo = ManuscriptParticipantRepository(session)
    participants = await part_repo.list_all_by_manuscript_ordered(manuscript_id)

    uids: set[int] = set()
    for v in versions:
        uids.add(v.submitted_by_uid)
    for d in d_rows:
        uids.add(d.decided_by_uid)
    for o in opinions:
        uids.add(o.reviewer_uid)
    for p in participants:
        uids.add(p.user_uid)
        uids.add(p.assigned_by_uid)
    if uids:
        unames = (
            (
                await session.execute(
                    select(User.uid, User.username).where(User.uid.in_(uids))
                )
            )
            .mappings()
            .all()
        )
        names = {int(r["uid"]): r["username"] for r in unames}
    else:
        names = {}

    history: list[dict] = []

    for v in versions:
        history.append(
            {
                "event_type": "version_submit",
                "event_time": v.submitted_at.isoformat() if v.submitted_at else None,
                "operator_uid": v.submitted_by_uid,
                "operator_name": names.get(v.submitted_by_uid, ""),
                "description": f"提交版本 v{v.version_number}",
                "details": {
                    "version_number": v.version_number,
                    "change_summary": v.change_summary,
                },
            }
        )

    for d in d_rows:
        history.append(
            {
                "event_type": "decision",
                "event_time": d.decided_at.isoformat() if d.decided_at else None,
                "operator_uid": d.decided_by_uid,
                "operator_name": names.get(d.decided_by_uid, ""),
                "description": d.decision_title,
                "details": {
                    "stage": d.stage,
                    "decision_type": d.decision_type,
                    "decision_comments": d.decision_comments,
                },
            }
        )

    for o in opinions:
        if hide_foreign_opinions and o.reviewer_uid != my_uid:
            history.append(
                {
                    "event_type": "review_opinion",
                    "event_time": o.submitted_at.isoformat()
                    if o.submitted_at
                    else None,
                    "operator_uid": o.reviewer_uid,
                    "operator_name": names.get(o.reviewer_uid, ""),
                    "description": "审稿人已提交意见（详情已对审稿人角色隐藏）",
                    "details": {
                        "stage": o.stage,
                        "review_round": o.review_round,
                    },
                }
            )
        else:
            history.append(
                {
                    "event_type": "review_opinion",
                    "event_time": o.submitted_at.isoformat()
                    if o.submitted_at
                    else None,
                    "operator_uid": o.reviewer_uid,
                    "operator_name": names.get(o.reviewer_uid, ""),
                    "description": "提交了审稿意见",
                    "details": {
                        "stage": o.stage,
                        "review_round": o.review_round,
                        "decision": o.decision,
                        "review_score": o.review_score,
                        "review_comments": o.review_comments,
                        "recommendations": o.recommendations,
                    },
                }
            )

    for p in participants:
        history.append(
            {
                "event_type": "participant_assign",
                "event_time": p.assigned_at.isoformat() if p.assigned_at else None,
                "operator_uid": p.assigned_by_uid,
                "operator_name": names.get(p.assigned_by_uid, ""),
                "description": f"分配参与者：{p.role_type}（uid {p.user_uid}）",
                "details": {
                    "participant_id": p.participant_id,
                    "role_type": p.role_type,
                    "user_uid": p.user_uid,
                    "is_active": p.is_active,
                    "completed_at": p.completed_at.isoformat()
                    if p.completed_at
                    else None,
                },
            }
        )

    history.sort(key=lambda e: e["event_time"] or "")

    return ApiResponse.success(
        data={"manuscript_id": manuscript_id, "history": history}
    )


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

    # 根据文件扩展名确定 MIME 类型和大小限制
    mime_type_map = {
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    mime_type = mime_type_map.get(ext, "application/octet-stream")
    max_size = FILE_SIZE_LIMITS.get(mime_type, DEFAULT_SIZE_LIMIT)

    try:
        # 使用临时目录来处理文件，避免占用存储空间
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. 保存上传的原文件（使用流式读取）
            input_file_path = os.path.join(temp_dir, f"input{ext}")
            file_size = await stream_file_to_path(file, Path(input_file_path), max_size)

            # 记录文件上传信息
            global_logger.info(
                "Manuscripts",
                f"PDF预览文件上传 - filename: {file.filename}, content_type: {mime_type}, "
                f"size: {file_size} bytes ({file_size // 1024} KB)",
            )

            # 2. 转换为 PDF (如果已经是 PDF，则内部会直接返回原路径)
            main_pdf_path = await pdf_service.convert_to_pdf(input_file_path, temp_dir)

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
                "abstract": abstract,
            }
            await pdf_service.generate_cover_pdf(data, cover_pdf_path)

            # 4. 合并 PDF
            merged_pdf_path = os.path.join(temp_dir, "merged.pdf")
            await pdf_service.merge_pdfs(
                [cover_pdf_path, main_pdf_path], merged_pdf_path
            )

            # 5. 读取合并后的内容并作为流返回
            with open(merged_pdf_path, "rb") as f:
                pdf_content = f.read()

            # 清理临时文件由 TemporaryDirectory 上下文管理器自动完成

        def iterfile():
            yield pdf_content

        return StreamingResponse(
            iterfile(),
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=preview_merged.pdf"},
        )

    except Exception as e:
        global_logger.error("Manuscripts", f"PDF 合成预览失败: {e}")
        raise HTTPException(status_code=500, detail=f"PDF 处理失败: {str(e)}")
