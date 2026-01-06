"""
投稿相关API接口
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from utils.jwt import jwt_util
from utils.redis import redis_client
from utils.generator import generator
from model.journal import (
    JournalUploadRequest, 
    JournalUploadResponse, 
    JournalInfo, 
    JournalListResponse,
    JournalStatusUpdateRequest
)
from model.user import LoginRequest, LoginResponse

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

@submit_router.post("/login", summary="作者登录", response_model=LoginResponse)
async def author_login(request: LoginRequest, req: Request):
    """作者登录接口 - 支持writer及以上角色登录"""
    # 获取客户端IP
    client_ip = req.client.host
    
    # 检查登录频率限制
    allowed, attempts = await redis_client.set_login_limit(client_ip, max_attempts=5, expire_time=3600)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"登录请求过于频繁，请稍后再试。当前尝试次数：{attempts}/5"
        )
    
    # 检查用户是否存在
    user = await user_db.fetchone(
        "SELECT * FROM users WHERE username = ?",
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
        "UPDATE users SET last_login_time = ? WHERE uid = ?",
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
    await redis_client.set_user_online(
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
    token: str,
    title: str = Form(..., description="文献标题"),
    authors: str = Form(..., description="文献作者，多个作者用逗号分隔"),
    abstract: Optional[str] = Form(None, description="文献摘要"),
    file: UploadFile = File(..., description="文献文件")
):
    """上传文献接口 - 仅限writer及以上角色"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查用户角色权限
    allowed_roles = ["writer", "reviewer", "admin"]
    if user_info["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="该用户没有投稿权限")
    
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
    await journal_db.execute(
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
    
    # 获取新上传文献的ID
    jid = await journal_db.fetchval("SELECT last_insert_rowid()")
    
    return JournalUploadResponse(
        jid=jid,
        title=title,
        status="pending",
        upload_time=datetime.now()
    )

@submit_router.get("/my", summary="获取我的文献列表", response_model=JournalListResponse)
async def get_my_journals(token: str, page: int = 1, page_size: int = 10):
    """获取当前用户上传的文献列表"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查用户角色权限
    allowed_roles = ["writer", "reviewer", "admin"]
    if user_info["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="该用户没有投稿权限")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询文献总数
    total = await journal_db.fetchval(
        "SELECT COUNT(*) FROM journals WHERE uid = ?",
        (user_info["uid"],)
    )
    
    # 查询文献列表
    journals = await journal_db.fetchall(
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

@submit_router.get("/detail/{jid}", summary="获取文献详情", response_model=JournalInfo)
async def get_journal_detail(jid: int, token: str):
    """获取文献详情"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查用户角色权限
    allowed_roles = ["writer", "reviewer", "admin"]
    if user_info["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="该用户没有投稿权限")
    
    # 查询文献
    journal = await journal_db.fetchone(
        """
        SELECT jid, uid, title, authors, abstract, status, file_name, file_size, create_time, update_time
        FROM journals 
        WHERE jid = ?
        """,
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限 - 只能查看自己的文献（writer角色）或所有文献（reviewer/admin角色）
    if user_info["role"] == "writer" and journal["uid"] != user_info["uid"]:
        raise HTTPException(status_code=403, detail="无权访问此文献")
    
    return JournalInfo(**journal)

@submit_router.delete("/{jid}", summary="删除文献")
async def delete_journal(jid: int, token: str):
    """删除文献（软删除）"""
    # 验证token
    user_info = jwt_util.get_user_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 检查用户角色权限
    allowed_roles = ["writer", "reviewer", "admin"]
    if user_info["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="该用户没有投稿权限")
    
    # 查询文献
    journal = await journal_db.fetchone(
        "SELECT jid, uid, title, authors, abstract, file_hash, file_bucket, file_name, file_size FROM journals WHERE jid = ?",
        (jid,)
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="文献不存在")
    
    # 检查权限 - writer只能删除自己的文献，reviewer/admin可以删除任何文献
    if user_info["role"] == "writer" and journal["uid"] != user_info["uid"]:
        raise HTTPException(status_code=403, detail="无权删除此文献")
    
    # 软删除：将文献状态改为deleted
    await journal_db.execute(
        "UPDATE journals SET status = 'deleted', update_time = ? WHERE jid = ?",
        (datetime.now().isoformat(), jid)
    )
    
    # 将已删除文献信息添加到已删除文献表
    await deleted_journal_db.execute(
        """
        INSERT INTO deleted_journals (
            original_jid, uid, title, authors, abstract, file_hash, 
            file_bucket, file_name, file_size, delete_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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