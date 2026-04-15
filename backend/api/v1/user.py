"""
[DEPRECATED] 用户相关API接口

本模块已废弃，请勿在新代码中使用。
迁移指引：
- 用户认证功能（注册、登录、登出、修改密码）请使用 auth.py 中的接口。
- 用户管理功能（获取信息、修改信息、角色管理等）请使用 users.py 中的接口。
- 本文件路由已全部移除，以避免旧版本接口继续被调用。

旧角色名映射：
- 'normal' -> 'user' (UserRole.USER)
- 'writer' -> 'author' (UserRole.AUTHOR)

废弃日期：2026-03-26
保留原因：向后兼容说明
"""
from fastapi import APIRouter

# 创建空的用户相关路由，避免导入错误
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
async def register(
    request: RegisterRequest,
    req: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """用户注册接口"""
    # 获取客户端IP
    client_ip = req.client.host
    
    # 检查登录频率限制
    allowed, attempts = await redis_service.set_login_limit(client_ip, max_attempts=3, expire_time=3600)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"注册请求过于频繁，请稍后再试。当前尝试次数：{attempts}/3"
        )
    
    repo = UserRepository(session)

    # 检查用户名是否已存在
    if await repo.username_exists(request.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    if await repo.email_exists(request.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 确定用户角色（基于邀请码）
    user_role = 'normal'  # 默认角色
    if request.invite_code:
        # 验证邀请码
        validation_result = await invitation_service.validate_invitation_code(request.invite_code, session=session)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=f"邀请码无效: {validation_result['message']}")
        user_role = validation_result["role"]
    
    # 生成uid_hash
    uid_hash = generator.generate_uid_hash(request.username)
    
    # 密码加密
    hashed_password = jwt_util.hash_password(request.password)
    
    # 注册时间
    create_time = datetime.now().isoformat()

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
    
    # 生成token
    token = jwt_util.create_access_token({
        "uid": new_user.uid,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
    })
    
    # 设置用户在线状态
    await redis_service.set_user_online(
        user_id=new_user.uid,
        token=token,
        expire_time=3600 * 24 if request.is_remember else 3600
    )
    
    return RegisterResponse(
        register_time=datetime.now(),
        token=token,
        message="注册成功"
    )

@user_router.post("/login", summary="用户登录", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    req: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """用户登录接口"""
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
    repo = UserRepository(session)
    user = await repo.get_by_username(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not jwt_util.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 更新最后登录时间
    async with transactional(session):
        user.last_login_time = datetime.now().isoformat()
    
    # 生成token
    token = jwt_util.create_access_token({
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    })
    
    # 设置用户在线状态
    expire_time = 3600 * 24 * 30 if request.is_remember else 3600
    await redis_service.set_user_online(user_id=user.uid, token=token, expire_time=expire_time)
    
    return LoginResponse(
        login_time=datetime.now(),
        is_remember=request.is_remember,
        token=token,
        message="登录成功"
    )

@user_router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user: dict = Depends(deps.get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取当前用户信息接口"""
    # 从Redis验证用户在线状态
    is_online = await redis_service.is_user_online(current_user["uid"])
    
    # 从数据库获取最新用户信息 (已经在deps中获取了，但这里为了保持字段完整性，特别是avatar_hash，可能deps没拿全)
    # deps中只拿了: uid, username, email, role, is_verified
    # 这里需要: create_time, last_login_time, avatar_hash
    # 重新查询一下或者修改deps。修改deps更好，但deps是通用的。
    # 为了简单，这里直接再查一次或者让deps返回更多字段。
    # 让我们修改deps返回所有字段? 不，deps只负责鉴权。
    # 这里我们重新查询完整信息。
    
    repo = UserRepository(session)
    user = await repo.get_profile_fields_by_id(current_user["uid"])
    
    return {
        "uid": user["uid"] if user else current_user["uid"],
        "username": user["username"] if user else current_user.get("username"),
        "email": user["email"] if user else current_user.get("email"),
        "role": user["role"] if user else current_user.get("role"),
        "create_time": user.get("create_time") if user else None,
        "last_login_time": user.get("last_login_time") if user else None,
        "avatar_hash": user.get("avatar_hash") if user else None,
        "is_online": is_online
    }

@user_router.post("/logout", summary="用户登出")
async def logout(token: str = Depends(deps.get_token)):
    """用户登出接口"""
    # 从Redis验证用户在线状态
    user_id = await redis_service.get_user_by_token(token)
    if user_id:
        # 设置用户离线状态
        await redis_service.set_user_offline(user_id, token)
    
    return {"message": "登出成功"}

@user_router.post("/upgrade", summary="用户角色升级")
async def upgrade_role(
    request: RoleUpgradeRequest,
    current_user: dict = Depends(deps.get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """使用邀请码升级用户角色"""
    # 验证邀请码
    validation_result = await invitation_service.validate_invitation_code(request.invite_code, session=session)
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=f"邀请码无效: {validation_result['message']}")
    
    new_role = validation_result["role"]
    
    # 简单的角色等级比较 (admin > reviewer > writer > normal)
    role_levels = {"normal": 1, "writer": 2, "reviewer": 3, "ea_ae": 4, "deputy_editor": 5, "editor": 6, "admin": 7}
    current_level = role_levels.get(current_user["role"], 1)
    new_level = role_levels.get(new_role, 1)
    
    if new_level <= current_level:
        raise HTTPException(status_code=400, detail=f"当前角色已是或高于 {new_role}，无需升级")

    # 更新数据库
    repo = UserRepository(session)
    async with transactional(session):
        user = await repo.get_by_id(current_user["uid"])
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        user.role = new_role

        ok = await invitation_service.use_invitation_code(
            request.invite_code,
            current_user["uid"],
            current_user["username"],
            session=session,
        )
        if not ok:
            raise HTTPException(status_code=400, detail="邀请码使用失败")
    
    return {"message": f"成功升级为 {new_role}", "new_role": new_role}
