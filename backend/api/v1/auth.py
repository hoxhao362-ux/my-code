"""
认证相关 API 接口

包含登录、注册、密码修改等认证功能
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime

from core.config import config
from core.enums import UserRole
from utils.jwt import jwt_util
from service.rate_limit_service import rate_limit_service
from service.redis_service import redis_service
from utils.generator import generator
from service.invitation_service import invitation_service
from model.user import RegisterRequest, LoginRequest, ChangePasswordRequest
from model.response import ApiResponse
from api import dependencies as deps
from utils.log import global_logger

from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session
from database.orm.models.user import User
from database.repositories.user_repo import UserRepository
from database.uow import transactional

# 创建认证相关路由
router = APIRouter(
    prefix="/auth",
    tags=["认证相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
        429: {"description": "请求频率过高"},
    },
)


@router.post("/register", summary="用户注册", response_model=ApiResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """
    用户注册接口
    
    功能说明：
    1. 检查注册频率限制
    2. 验证用户名和邮箱唯一性
    3. 基于邀请码确定用户角色（默认 author）
    4. 创建用户账号并生成访问令牌
    
    Args:
        request: 注册请求体（用户名、密码、邮箱、邀请码）
        req: FastAPI 请求对象
        session: 数据库会话
        
    Returns:
        RegisterResponse: 注册响应（注册时间、令牌、消息）
        
    Raises:
        HTTPException: 用户名已存在、邮箱已被注册、邀请码无效等
    """
    # 获取客户端 IP
    client_ip = req.client.host if req.client else "unknown"
    
    # 检查注册频率限制
    allowed, attempts = await rate_limit_service.check("register", client_ip)
    if not allowed:
        cfg = rate_limit_service.get_preset_config("register")
        global_logger.warning("Auth", f"注册频率超限 - IP: {client_ip}, 尝试次数：{attempts}/{cfg['max_attempts']}")
        raise HTTPException(
            status_code=429,
            detail=f"注册请求过于频繁，请稍后再试。当前尝试次数：{attempts}/{cfg['max_attempts']}"
        )
    
    repo = UserRepository(session)

    # 检查用户名是否已存在
    if await repo.username_exists(request.username):
        global_logger.warning("Auth", f"用户名已存在 - username: {request.username}")
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    if await repo.email_exists(request.email):
        global_logger.warning("Auth", f"邮箱已被注册 - email: {request.email}")
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 确定用户角色（基于邀请码，默认 author）
    user_role = UserRole.AUTHOR.value  # 默认角色为 author
    if request.invite_code:
        # 验证邀请码
        validation_result = await invitation_service.validate_invitation_code(request.invite_code, session=session)
        if not validation_result["valid"]:
            global_logger.warning("Auth", f"邀请码无效 - code: {request.invite_code}, reason: {validation_result['message']}")
            raise HTTPException(status_code=400, detail=f"邀请码无效：{validation_result['message']}")
        user_role = validation_result["role"]
        global_logger.info("Auth", f"使用邀请码升级角色 - username: {request.username}, role: {user_role}")
    
    # 生成 uid_hash
    uid_hash = generator.generate_uid_hash(request.username)
    
    # 密码加密
    hashed_password = jwt_util.hash_password(request.password)
    
    # 注册时间
    create_time = datetime.now()

    try:
        async with transactional(session):
            new_user = User(
                uid_hash=uid_hash,
                username=request.username,
                password=hashed_password,
                email=request.email,
                role=user_role,
                is_verified=False,
                verification_code=None,
                avatar_path=None,
                avatar_hash=None,
                create_time=create_time,
                last_login_time=None,
            )
            repo.add(new_user)
            await session.flush()

            if request.invite_code:
                ok = await invitation_service.use_invitation_code(
                    request.invite_code,
                    new_user.uid,
                    new_user.username,
                    session=session,
                )
                if not ok:
                    raise HTTPException(status_code=400, detail="邀请码使用失败")
        
        # 生成 token
        token = await jwt_util.create_access_token({
            "uid": new_user.uid,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
        })
        
        # 设置用户在线状态
        expire_time = 3600 * 24 if request.invite_code else 3600  # 使用邀请码注册记住 30 天
        await redis_service.set_user_online(
            user_id=new_user.uid,
            token=token,
            expire_time=expire_time
        )
        
        global_logger.info("Auth", f"用户注册成功 - uid: {new_user.uid}, username: {new_user.username}, role: {user_role}")
        
        return ApiResponse.success(data={
            "register_time": datetime.now().isoformat(),
            "token": token,
        }, message="注册成功")
    except Exception as e:
        global_logger.exception("Auth", f"用户注册失败 - username: {request.username}, error: {e}")
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")


@router.post("/login", summary="用户登录", response_model=ApiResponse)
async def login(
    request: LoginRequest,
    req: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """
    用户登录接口
    
    功能说明：
    1. 检查登录频率限制（防暴力破解）
    2. 验证用户名和密码
    3. 更新最后登录时间
    4. 生成 JWT 令牌并设置在线状态
    
    Args:
        request: 登录请求体（用户名、密码、是否记住）
        req: FastAPI 请求对象
        session: 数据库会话
        
    Returns:
        LoginResponse: 登录响应（登录时间、令牌、消息）
        
    Raises:
        HTTPException: 用户名或密码错误、登录频率超限
    """
    # 获取客户端 IP
    client_ip = req.client.host if req.client else "unknown"
    
    # 检查登录频率限制
    allowed, attempts = await rate_limit_service.check("login", client_ip)
    if not allowed:
        cfg = rate_limit_service.get_preset_config("login")
        global_logger.warning("Auth", f"登录频率超限 - IP: {client_ip}, 尝试次数：{attempts}/{cfg['max_attempts']}")
        raise HTTPException(
            status_code=429,
            detail=f"登录请求过于频繁，请稍后再试。当前尝试次数：{attempts}/{cfg['max_attempts']}"
        )
    
    # 检查用户是否存在
    repo = UserRepository(session)
    user = await repo.get_by_username(request.username)
    if not user:
        global_logger.warning("Auth", f"用户不存在 - username: {request.username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户是否已被停用（软删除）
    if user.is_deleted:
        global_logger.warning("Auth", f"已停用用户尝试登录: {request.username}")
        raise HTTPException(status_code=403, detail="账户已被停用，请联系管理员")
    
    # 验证密码
    if not jwt_util.verify_password(request.password, user.password):
        global_logger.warning("Auth", f"密码错误 - username: {request.username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 更新最后登录时间并累加登录天数
    last_login_time = datetime.now()
    async with transactional(session):
        user.last_login_time = last_login_time
        user.login_days = User.login_days + 1
    
    # 生成 token
    token = await jwt_util.create_access_token({
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    })
    
    # 设置用户在线状态
    expire_time = 3600 * 24 * 30 if request.is_remember else 3600
    await redis_service.set_user_online(user_id=user.uid, token=token, expire_time=expire_time)
    
    global_logger.info("Auth", f"用户登录成功 - uid: {user.uid}, username: {user.username}, role: {user.role}")
    
    return ApiResponse.success(data={
        "login_time": datetime.now().isoformat(),
        "is_remember": request.is_remember,
        "token": token,
    }, message="登录成功")


@router.post("/logout", summary="用户登出")
async def logout(token: str = Depends(deps.get_token)):
    """
    用户登出接口
    
    功能说明：
    1. 从 Redis 清除用户在线状态
    
    Args:
        token: 访问令牌
        
    Returns:
        dict: 登出成功消息
    """
    # 从 Redis 验证用户在线状态
    user_id = await redis_service.get_user_by_token(token)
    if user_id:
        # 设置用户离线状态
        await redis_service.set_user_offline(user_id, token)
        global_logger.info("Auth", f"用户登出成功 - uid: {user_id}")
    
    return ApiResponse.success(message="登出成功")


@router.put("/password", summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_token),
    session: AsyncSession = Depends(get_db_session),
):
    """
    修改密码接口
    
    功能说明：
    1. 验证旧密码正确性
    2. 加密新密码并更新数据库
    3. 清除 Redis 会话，强制重新登录
    
    Args:
        request: 修改密码请求体（old_password、new_password，均为 SHA256 哈希）
        current_user: 当前用户信息
        token: 当前访问令牌
        session: 数据库会话
        
    Returns:
        ApiResponse: 修改成功提示（需重新登录）
        
    Raises:
        HTTPException: 旧密码错误、用户不存在
    """
    uid = current_user["uid"]
    username = current_user["username"]
    
    # 1. 获取用户完整信息（包含密码哈希）
    repo = UserRepository(session)
    user = await repo.get_by_id(uid)
    if not user:
        global_logger.warning("Auth", f"修改密码时用户不存在 - uid: {uid}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 2. 验证旧密码
    if not jwt_util.verify_password(request.old_password, user.password):
        global_logger.warning("Auth", f"旧密码错误 - uid: {uid}, username: {username}")
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    # 3. 加密新密码并更新数据库
    hashed_password = jwt_util.hash_password(request.new_password)
    async with transactional(session):
        user.password = hashed_password
    
    # 4. 清除 Redis 会话，强制重新登录
    await redis_service.set_user_offline(uid, token)
    
    global_logger.info("Auth", f"密码修改成功，已强制下线 - uid: {uid}, username: {username}")
    
    # 5. 返回成功提示
    return ApiResponse.success(message="密码修改成功，请重新登录")
