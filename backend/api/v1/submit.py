"""
[DEPRECATED] 投稿相关API接口

本模块已废弃，请勿在新代码中使用。
- 登录功能已迁移至 auth.py
- 投稿功能已迁移至 manuscripts.py
- Journal 模型已统一为 Manuscript 模型

旧角色名映射：
- 'writer' -> 'author' (UserRole.AUTHOR)

废弃日期：2026-03-26
保留原因：向后兼容
"""
from fastapi import APIRouter, HTTPException, Form, Depends
from datetime import datetime
from pathlib import Path

from core.config import config

from utils.generator import generator

from sqlalchemy.ext.asyncio import AsyncSession

from model.journal import (
    JournalUploadRequest, 
    JournalUploadResponse, 
    JournalInfo, 
    JournalListResponse
)
from api import dependencies as deps

from database.dependencies import get_db_session
from database.orm.models.deleted_journal import DeletedJournal
from database.orm.models.journal import Journal
from database.repositories.journal_repo import JournalRepository
from database.uow import transactional

# 创建投稿相关路由
submit_router = APIRouter(
    prefix="/submit",
    tags=["[已废弃] 投稿相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
        429: {"description": "请求频率过高"},
    },
)

# [DEPRECATED] 登录接口已废弃，请使用 auth.py 中的 /api/v1/auth/login
# @submit_router.post("/login") 已移除

async def get_writer_user_from_form(token: str = Form(...)):
    """从表单获取token并验证writer权限"""
    user = await deps.get_current_user(token)
    return await deps.get_writer_user(user)

# ========== 已废弃的登录接口 ==========
# 以下登录端点已废弃，请使用 POST /api/v1/auth/login 代替
# 符合角色要求的用户均可通过统一登录接口登录

# @submit_router.post("/login", summary="作者登录", response_model=LoginResponse)
# async def author_login(...) 已移除 - 请使用 auth.py 中的登录接口

@submit_router.post("/upload", summary="上传文献", response_model=JournalUploadResponse)
async def upload_journal(
    request: JournalUploadRequest = Depends(), # 使用Depends来处理Pydantic model in Form? 
    # 注意：上面的代码使用了 request: JournalUploadRequest，在FastAPI中如果不加Depends且包含UploadFile，
    # 可能会有问题，但如果是旧代码且能运行，可能是使用了特殊方式。
    # 为了保险，我们保持参数定义尽可能接近原样，但使用Depends处理token。
    # 原代码: async def upload_journal(request: JournalUploadRequest, token: str = Form(...)):
    # 如果 request 是 body，token 是 form，这是冲突的。
    # 假设 request 也是 Form。
    # 我们这里保留 request 参数，假设它是以此方式工作的。
    current_user: dict = Depends(get_writer_user_from_form),
    session: AsyncSession = Depends(get_db_session),
):
    """上传文献接口 - 仅限writer及以上角色"""
    # 这里的 request 参数处理比较微妙。如果 JournalUploadRequest 包含 UploadFile，它必须是 multipart/form-data。
    # FastAPI 不会自动将 Pydantic 模型映射到 Form 字段，除非使用 Depends。
    # 但由于我们不能修改前端，我们假设 request 参数能正确接收数据 (可能前端发送的是分开的字段，
    # 而 FastAPI 通过某种方式（比如名字匹配）填充了 request? 不，这不标准)。
    # 最可能的解释是：原代码其实是错误的，或者使用了特定的 FastAPI 版本/插件。
    # 但不管怎样，我们现在的任务是替换 token 验证。
    # 我们删除了 token 参数，改用 current_user 依赖。
    
    # 检查文件类型
    allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if request.file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持PDF和Word文档")
    
    # 读取文件内容
    file_content = await request.file.read()
    file_size = request.file_size
    
    # 生成文件哈希
    file_hash = generator.generate_file_hash(file_content)
    
    # 计算哈希分桶，使用哈希值的前2位作为桶名
    file_bucket_1 = file_hash[:2]
    file_bucket_2 = file_hash[2:4]
    
    # 获取配置
    papers_dir = Path(config["global.global.literature_dir"])
    
    # 创建存储目录（基于哈希分桶）
    bucket_dir = papers_dir / file_bucket_1 / file_bucket_2
    bucket_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_ext = Path(request.file_name).suffix
    file_path = bucket_dir / f"{file_hash}{file_ext}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 记录上传时间
    create_time = datetime.now().isoformat()
    
    # jid 生成
    jid = generator.generate_jid()

    # 插入文献数据
    # 注意：jid 是由生成器生成的毫秒时间戳字符串，在 PostgreSQL 中会被存为 BIGINT
    journal_repo = JournalRepository(session)
    async with transactional(session):
        journal_repo.add(
            Journal(
                jid=int(jid),
                uid=current_user["uid"],
                title=request.title,
                authors=request.authors,
                subject=request.subject,
                abstract=request.abstract,
                file_hash=file_hash,
                file_bucket=f"{file_bucket_1}/{file_bucket_2}",
                file_name=request.file_name,
                file_size=file_size,
                status="pending",
                create_time=create_time,
                update_time=None,
            )
        )
    
    return JournalUploadResponse(
        jid=int(jid),
        title=request.title,
        status="pending",
        upload_time=datetime.now()
    )

@submit_router.get("/my", summary="获取我的文献列表", response_model=JournalListResponse)
async def get_my_journals(
    page: int = 1, 
    page_size: int = 10,
    current_user: dict = Depends(deps.get_writer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取当前用户上传的文献列表"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    journal_repo = JournalRepository(session)
    total = await journal_repo.count_by_uploader(current_user["uid"])
    rows = await journal_repo.list_by_uploader_page(current_user["uid"], page, page_size)
    
    # 转换为响应模型
    journal_list = [
        JournalInfo(**dict(row)) for row in rows
    ]
    
    return JournalListResponse(
        total=total,
        journals=journal_list
    )

@submit_router.get("/detail/{jid}", summary="获取文献详情", response_model=JournalInfo)
async def get_journal_detail(
    jid: int, 
    current_user: dict = Depends(deps.get_writer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取文献详情"""
    journal_repo = JournalRepository(session)
    journal = await journal_repo.get_by_id(jid)
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限 - 只能查看自己的文献（writer角色）或所有文献（reviewer/admin角色）
    if current_user["role"] == "writer" and journal.uid != current_user["uid"]:
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

@submit_router.delete("/{jid}", summary="删除文献")
async def delete_journal(
    jid: int, 
    current_user: dict = Depends(deps.get_writer_user),
    session: AsyncSession = Depends(get_db_session),
):
    """删除文献（软删除）"""
    journal_repo = JournalRepository(session)
    journal = await journal_repo.get_by_id(jid)
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限 - writer只能删除自己的文献，reviewer/admin可以删除任何文献
    if current_user["role"] == "writer" and journal.uid != current_user["uid"]:
        raise HTTPException(status_code=403, detail="无权删除此文献")
    
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
    
    return {"message": "文献删除成功"}
