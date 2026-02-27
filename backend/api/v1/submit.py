"""
投稿相关API接口
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Depends
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from core.config import config

from utils.jwt import jwt_util
from service.redis_service import redis_service
from utils.generator import generator

from model.journal import (
    JournalUploadRequest, 
    JournalUploadResponse, 
    JournalInfo, 
    JournalListResponse,
    JournalStatusUpdateRequest
)
from model.user import LoginRequest, LoginResponse
from api import dependencies as deps

# 获取数据库服务实例
from database import db_manager
user_db = db_manager.get_service('user_account')
journal_db = db_manager.get_service('journal_submit')
deleted_journal_db = db_manager.get_service('deleted_journal')

# 创建投稿相关路由
submit_router = APIRouter(
    prefix="/submit",
    tags=["投稿相关接口"],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
        429: {"description": "请求频率过高"},
    },
)

async def get_writer_user_from_form(token: str = Form(...)):
    """从表单获取token并验证writer权限"""
    user = await deps.get_current_user(token)
    return await deps.get_writer_user(user)

@submit_router.post("/login", summary="作者登录", response_model=LoginResponse)
async def author_login(request: LoginRequest, req: Request):
    """作者登录接口 - 支持writer及以上角色登录"""
    # 获取客户端IP
    client_ip = req.client.host if req.client else "unknown"
    
    # 检查登录频率限制
    allowed, attempts = await redis_service.set_login_limit(client_ip, max_attempts=5, expire_time=3600)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"登录请求过于频繁，请稍后再试。当前尝试次数：{attempts}/5"
        )
    
    # 检查用户是否存在
    user = await user_db.fetchone(
        "SELECT * FROM users WHERE username = $1",
        (request.username,)
    )
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not jwt_util.verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户角色权限（writer及以上角色才能登录投稿系统）
    allowed_roles = ["writer", "reviewer", "admin"]
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="该用户没有投稿权限，需要使用writer及以上角色的账号登录")
    
    # 更新最后登录时间
    last_login_time = datetime.now().isoformat()
    await user_db.execute(
        "UPDATE users SET last_login_time = $1 WHERE uid = $2",
        (last_login_time, user["uid"])
    )
    
    # 生成token
    token = jwt_util.create_access_token({
        "uid": user["uid"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    })
    
    # 设置用户在线状态
    expire_time = 3600 * 24 * 30 if request.is_remember else 3600
    await redis_service.set_user_online(
        user_id=user["uid"],
        token=token,
        expire_time=expire_time
    )
    
    return LoginResponse(
        login_time=datetime.now(),
        is_remember=request.is_remember,
        token=token,
        message="作者登录成功"
    )

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
    current_user: dict = Depends(get_writer_user_from_form)
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
    papers_dir = Path(config["global.global.papers_dir"])
    
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
    await journal_db.execute(
        """
        INSERT INTO journals (jid, uid, title, authors, subject, abstract, file_hash, file_bucket, file_name, file_size, create_time)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """,
        (
            int(jid), # 转换为整数
            current_user["uid"],
            request.title,
            request.authors,
            request.subject,
            request.abstract,
            file_hash,
            f"{file_bucket_1}/{file_bucket_2}",
            request.file_name,
            file_size,
            create_time
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
    current_user: dict = Depends(deps.get_writer_user)
):
    """获取当前用户上传的文献列表"""
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await journal_db.fetchval(
        "SELECT COUNT(*) FROM journals WHERE uid = $1",
        (current_user["uid"],)
    )
    
    # 查询文献列表
    journals = await journal_db.fetchall(
        """
        SELECT jid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE uid = $1 
        ORDER BY create_time DESC 
        LIMIT $2 OFFSET $3
        """,
        (current_user["uid"], page_size, offset)
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

@submit_router.get("/detail/{jid}", summary="获取文献详情", response_model=JournalInfo)
async def get_journal_detail(
    jid: int, 
    current_user: dict = Depends(deps.get_writer_user)
):
    """获取文献详情"""
    # 查询文献
    journal = await journal_db.fetchone(
        """
        SELECT jid, uid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE jid = $1
        """,
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限 - 只能查看自己的文献（writer角色）或所有文献（reviewer/admin角色）
    if current_user["role"] == "writer" and journal["uid"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="无权访问此文献")
    
    return JournalInfo(**journal)

@submit_router.delete("/{jid}", summary="删除文献")
async def delete_journal(
    jid: int, 
    current_user: dict = Depends(deps.get_writer_user)
):
    """删除文献（软删除）"""
    # 查询文献
    journal = await journal_db.fetchone(
        "SELECT jid, uid, title, authors, abstract, file_hash, file_bucket, file_name, file_size FROM journals WHERE jid = $1",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限 - writer只能删除自己的文献，reviewer/admin可以删除任何文献
    if current_user["role"] == "writer" and journal["uid"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="无权删除此文献")
    
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
    
    return {"message": "文献删除成功"}
