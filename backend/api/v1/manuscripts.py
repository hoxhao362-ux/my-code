"""
稿件中心相关 API 接口

包含稿件投稿、流转、文件管理等功能
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from api import dependencies as deps
from core.config import config
from core.enums import (FileContentType, ManuscriptStatus, UserRole,
                        WorkflowAction)
from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript
from database.repositories.manuscript_repo import ManuscriptRepository
from database.uow import transactional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from model.manuscript import ManuscriptDetailDTO, ManuscriptListItemDTO
from model.response import ApiResponse
from service.manuscript_service import manuscript_workflow_service
from service.pdf_service import pdf_service
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
        f"decision_type: {decision_type}, uid: {current_user['uid']}",
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
            f"稿件流转成功 - mid: {manuscript_id}, {result['old_status']} -> {result['new_status']}",
        )

        return ApiResponse.success(data=result)

    except ValueError as e:
        global_logger.warning(
            "Manuscripts",
            f"稿件流转失败 - mid: {manuscript_id}, action: {action}, error: {str(e)}",
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{manuscript_id}/files", summary="获取稿件附件列表")
async def get_manuscript_files(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
):
    """获取稿件的所有附件

    TODO: 实现稿件附件列表查询

    建议实现流程：
    1. 根据 manuscript_id 查询 Manuscript 记录，确认稿件存在且未删除
    2. 权限检查：作者只能查看自己稿件的附件，编辑/审稿人可查看分配给自己的稿件附件
    3. 查询 ManuscriptFile 表，筛选 manuscript_id 匹配的记录
    4. 按上传时间排序，返回文件列表
    5. 区分主文件（file_type='main'）和附件（file_type='attachment'/'review'/'letter'/'other'）

    所需 ORM 模型：
    - ManuscriptFile (database/orm/models/manuscript.py) — 稿件附件表，含 file_id/manuscript_id/file_hash/file_bucket/original_name/file_size/content_type/file_type/uploaded_by_uid/uploaded_at/description
    - Manuscript (database/orm/models/manuscript.py) — 稿件主表，用于权限验证
    - ManuscriptParticipant (database/orm/models/manuscript.py) — 参与者表，用于验证审稿人权限

    建议 Repository 方法：
    - ManuscriptFileRepository.list_by_manuscript(manuscript_id) — 查询某稿件的所有附件
    - ManuscriptFileRepository.count_by_manuscript(manuscript_id) — 统计附件数

    建议 Service 调用链：
    API → 查询 Manuscript 确认存在 → 权限检查
        → ManuscriptFileRepository.list_by_manuscript(mid) → 格式化返回

    权限要求：
    - 当前使用 get_current_active_user（已登录用户均可访问）
    - 作者只能查看自己稿件的附件
    - 编辑/审稿人可查看分配给自己的稿件附件（需查 ManuscriptParticipant）

    返回数据格式建议：
    {
        "manuscript_id": 10001,
        "files": [
            {
                "file_id": 1,
                "original_name": "论文正文.pdf",
                "file_size": 1024000,
                "content_type": "application/pdf",
                "file_type": "main",
                "uploaded_by_uid": 5,
                "uploaded_at": "2026-04-18T10:00:00",
                "description": "稿件正文"
            }
        ]
    }

    注意事项：
    - 需增加数据库 session 依赖（当前函数缺少 session 参数）
    - ManuscriptFile.file_type 区分：main=主文件/review=审稿意见附件/letter=通信附件/other=其他
    - 前端可能需要下载链接，建议在返回中拼接文件下载 URL
    - 不应在列表中返回 file_hash 等敏感信息
    - 注意区分主文件（Manuscript 表的 file_hash）和附件文件（ManuscriptFile 表）
    """
    # TODO: 实现附件管理
    return ApiResponse.success(data={"manuscript_id": manuscript_id, "files": []})


@router.post("/{manuscript_id}/files", summary="上传稿件附件")
async def upload_manuscript_file(
    manuscript_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(deps.get_current_active_user),
):
    """上传稿件附件

    TODO: 实现稿件附件上传

    建议实现流程：
    1. 根据 manuscript_id 查询 Manuscript 记录，确认稿件存在且未删除
    2. 权限检查：仅作者本人可上传附件到自己的稿件（author_uid 匹配）
    3. 验证文件类型（FileContentType.is_allowed），仅允许 PDF/Word
    4. 读取文件内容，生成文件哈希（generator.generate_file_hash）
    5. 计算哈希分桶路径（file_bucket），保存文件到磁盘
    6. 创建 ManuscriptFile 记录，填充 file_hash/file_bucket/original_name/file_size/content_type/file_type/uploaded_by_uid/uploaded_at
    7. 在事务中执行数据库插入

    所需 ORM 模型：
    - ManuscriptFile (database/orm/models/manuscript.py) — 稿件附件表，需新建记录
    - Manuscript (database/orm/models/manuscript.py) — 稿件主表，用于权限验证

    建议 Repository 方法：
    - ManuscriptFileRepository.add(file_record) — 新增附件记录

    建议 Service 调用链：
    API → 查询 Manuscript → 权限检查 → 文件类型校验
        → 生成文件哈希 → 保存到磁盘 → ManuscriptFileRepository.add() → 返回成功

    权限要求：
    - 当前使用 get_current_active_user（已登录用户均可访问）
    - 仅作者本人可上传附件到自己的稿件，需验证 author_uid
    - 编辑/审稿人上传附件应使用 file_type='review'/'letter'，需另外处理权限

    返回数据格式建议：
    {
        "file_id": 1,
        "original_name": "补充材料.pdf",
        "file_size": 512000,
        "file_type": "attachment",
        "uploaded_at": "2026-04-18T14:00:00"
    }

    注意事项：
    - 需增加数据库 session 依赖（当前函数缺少 session 参数）
    - 需增加 file_type 参数（Form），默认 'attachment'，允许 main/review/letter/other
    - 文件存储逻辑参考 create_manuscript 接口中的哈希分桶方案
    - 需检查文件大小限制（建议配置最大文件大小）
    - 同名文件覆盖问题：使用文件哈希作为实际存储名，original_name 仅做展示
    - 主文件（file_type='main'）应同步更新 Manuscript 表的 file_hash/file_bucket 等字段
    """
    # TODO: 实现附件上传
    return ApiResponse.success(message="附件上传成功")


@router.get("/{manuscript_id}/history", summary="获取稿件操作历史")
async def get_manuscript_history(
    manuscript_id: int,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取稿件的操作历史记录

    TODO: 实现稿件操作历史查询

    建议实现流程：
    1. 根据 manuscript_id 查询 Manuscript 记录，确认稿件存在且未删除
    2. 权限检查：作者只能查看自己稿件的历史，编辑/审稿人可查看分配给自己的稿件历史
    3. 查询 ManuscriptVersion 表获取版本变更历史
    4. 查询 DecisionRecord 表获取编辑决策记录
    5. 查询 ReviewOpinion 表获取审稿意见历史
    6. 查询 ManuscriptParticipant 表获取人员分配变更
    7. 将以上记录按时间合并排序，形成完整的操作时间线
    8. 返回合并后的历史列表

    所需 ORM 模型：
    - ManuscriptVersion (database/orm/models/manuscript.py) — 稿件版本表，记录每次修改，含 version_id/version_number/title/authors/abstract/file_hash/submitted_by_uid/submitted_at/change_summary
    - DecisionRecord (database/orm/models/editorial.py) — 编辑决策记录表，含 decision_id/stage/decision_type/decision_title/decision_comments/recommendations/decided_by_uid/decided_at
    - ReviewOpinion (database/orm/models/review_opinion.py) — 审稿意见表，含 opinion_id/stage/review_round/review_score/review_comments/recommendations/decision/submitted_at
    - ManuscriptParticipant (database/orm/models/manuscript.py) — 参与者表，记录分配变更，含 participant_id/role_type/assigned_at/assigned_by_uid/is_active/completed_at

    建议 Repository 方法：
    - ManuscriptVersionRepository.list_by_manuscript(manuscript_id) — 查询版本历史
    - DecisionRecordRepository.list_by_manuscript(manuscript_id) — 查询决策记录
    - ReviewOpinionRepository.list_by_manuscript(manuscript_id) — 查询审稿意见
    - ManuscriptParticipantRepository.list_by_manuscript(manuscript_id) — 查询人员变更

    建议 Service 调用链：
    API → 查询 Manuscript 确认存在 → 权限检查
        → 并行查询 4 张表 → 联表获取 User 用户名
        → 按时间合并排序 → 格式化为时间线 → 返回

    权限要求：
    - 当前使用 get_current_active_user（已登录用户均可访问）
    - 作者只能查看自己稿件的操作历史
    - 审稿人查看时，审稿意见应脱敏（不显示其他审稿人的详细意见）
    - 编辑/管理员可查看完整历史

    返回数据格式建议：
    {
        "manuscript_id": 10001,
        "history": [
            {
                "event_type": "version_submit",
                "event_time": "2026-04-18T14:00:00",
                "operator_uid": 5,
                "operator_name": "张三",
                "description": "提交了第 2 版修改稿",
                "details": {
                    "version_number": 2,
                    "change_summary": "根据审稿意见修改了实验部分"
                }
            },
            {
                "event_type": "decision",
                "event_time": "2026-04-15T09:00:00",
                "operator_uid": 3,
                "operator_name": "编辑李四",
                "description": "初审通过",
                "details": {
                    "stage": "initial_review",
                    "decision_type": "accept"
                }
            },
            {
                "event_type": "review_opinion",
                "event_time": "2026-04-12T16:30:00",
                "operator_uid": 8,
                "operator_name": "审稿人王五",
                "description": "提交了审稿意见",
                "details": {
                    "stage": "peer_review",
                    "review_round": 1,
                    "decision": "revision"
                }
            }
        ]
    }

    注意事项：
    - 四张表的时间线合并排序是核心逻辑，建议统一用 ISO 字符串比较
    - event_type 建议枚举：version_submit/decision/review_opinion/participant_assign/status_change
    - 审稿人权限下，其他审稿人的 ReviewOpinion 不应返回 review_comments/review_score 等详情
    - 可考虑增加 event_type 和时间范围筛选参数
    - 大量历史记录时建议支持分页
    """
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
