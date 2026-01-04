"""用户相关API接口"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from core.config import config
from utils.jwt import jwt_util
from utils.redis import redis_client
from utils.generator import generator
from model.user import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse

# 获取数据库服务实例
from database import db_manager
user_db = db_manager.get_service('user_account')
journal_db = db_manager.get_service('journal_submit')

# 创建用户相关路由
user_router = APIRouter(
    prefix="/user",
    tags=["用户相关接口"],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
        429: {"description": "请求频率过高"},
    },
)

@user_router.post("/register", summary="用户注册", response_model=RegisterResponse)
async def register(request: RegisterRequest, req: Request):
    """用户注册接口"""
    # 获取客户端IP
    client_ip = req.client.host
    
    # 检查登录频率限制
    allowed, attempts = await redis_client.set_login_limit(client_ip, max_attempts=3, expire_time=3600)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"注册请求过于频繁，请稍后再试。当前尝试次数：{attempts}/3"
        )
    
    # 检查用户名是否已存在
    existing_user = await user_db.fetchone(
        "SELECT * FROM users WHERE username = ?",
        (request.username,)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = await user_db.fetchone(
        "SELECT * FROM users WHERE email = ?",
        (request.email,)
    )
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 生成uid_hash
    uid_hash = generator.generate_uid_hash(request.username)
    
    # 密码加密
    hashed_password = jwt_util.hash_password(request.password)
    
    # 注册时间
    create_time = datetime.now().isoformat()
    
    # 插入用户数据
    await user_db.execute(
        """
        INSERT INTO users (uid_hash, username, password, email, role, create_time)
        VALUES (?, ?, ?, ?, 'user', ?)
        """,
        (uid_hash, request.username, hashed_password, request.email, create_time)
    )
    
    # 获取新注册用户信息
    new_user = await user_db.fetchone(
        "SELECT uid, username, email, role FROM users WHERE username = ?",
        (request.username,)
    )
    
    # 生成token
    token = jwt_util.create_access_token({
        "uid": new_user["uid"],
        "username": new_user["username"],
        "email": new_user["email"],
        "role": new_user["role"]
    })
    
    # 设置用户在线状态
    await redis_client.set_user_online(
        user_id=new_user["uid"],
        token=token,
        expire_time=3600 * 24 if request.is_remember else 3600
    )
    
    return RegisterResponse(
        register_time=datetime.now(),
        token=token
    )

@user_router.post("/login", summary="用户登录", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request):
    """用户登录接口"""
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
        token=token
    )

@user_router.get("/me", summary="获取当前用户信息")
async def get_current_user(token: str):
    """获取当前用户信息接口"""
    # 从Redis验证用户在线状态
    user_id = await redis_client.get_user_by_token(token)
    if not user_id:
        # 如果Redis中没有，尝试从token中解析
        user_info = jwt_util.get_user_from_token(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="无效的token")
        user_id = user_info["uid"]
    
    # 从数据库获取最新用户信息
    user = await user_db.fetchone(
        "SELECT uid, username, email, role, create_time, last_login_time, avatar_hash FROM users WHERE uid = ?",
        (user_id,)
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 刷新token过期时间
    await redis_client.refresh_token_expire(user_id, token)
    
    return {
        "uid": user["uid"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "create_time": user["create_time"],
        "last_login_time": user["last_login_time"],
        "avatar_hash": user["avatar_hash"],
        "is_online": await redis_client.is_user_online(user_id)
    }

@user_router.post("/logout", summary="用户登出")
async def logout(token: str):
    """用户登出接口"""
    # 从Redis验证用户在线状态
    user_id = await redis_client.get_user_by_token(token)
    if user_id:
        # 设置用户离线状态
        await redis_client.set_user_offline(user_id, token)
    
    return {"message": "登出成功"}
