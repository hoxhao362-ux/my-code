import sys
import os
import asyncio

# 修复 Windows 下 asyncio 子进程 NotImplementedError 报错
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy import select

from utils.log import global_logger
from core.config import setup_core, config
from core.service_manager import service_manager

# 显式导入单例，触发它们向 service_manager 注册
from database.service.database_service import db_manager
from database.orm.models.user import User
from service.redis_service import redis_service
from service.kafka_service import kafka_service
from service.payment_service import payment_service

# 导入新重构的 API v1 路由（包含所有子模块）
from core.enums import UserRole
from api.v1 import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动阶段：
    1. 检查并创建配置目录
    2. 启动所有第三方服务（DB/Redis/Kafka/ES）
    3. 创建初始管理员账号
    4. 初始化支付服务
    
    关闭阶段：
    1. 安全关闭所有第三方服务
    """
    # ========== 启动事件 ==========
    global_logger.info('main', "启动应用")
    
    # 执行初始化检查工作
    global_logger.info('config', "开始执行初始化检查")
    
    # 检查并创建配置中声明的目录路径
    config.check_dirs()
    
    # 启动所有已注册的第三方服务
    try:
        await service_manager.start_all()
    except Exception as e:
        global_logger.error('main', f"第三方服务集群启动失败：{e}")
        # 根据业务需求决定是否终止应用启动
        # raise e
    
    # 检查并创建初始管理员
    try:
        async with db_manager.get_session() as session:
            admin_uid = await session.scalar(select(User.uid).where(User.role == UserRole.ADMIN.value))
            if not admin_uid:
                global_logger.info("main", "未检测到管理员账号，正在创建初始管理员...")
                from utils.jwt import jwt_util
                from utils.generator import generator

                try:
                    admin_username = config["admin.admin.default_username"]
                    admin_password = config["admin.admin.default_password"]
                    admin_email = config["admin.admin.default_email"]
                except Exception as e:
                    raise ValueError("管理员配置缺失必要字段") from e

                uid_hash = generator.generate_uid_hash(admin_username)
                hashed_password = jwt_util.hash_password(admin_password)

                session.add(
                    User(
                        uid_hash=uid_hash,
                        username=admin_username,
                        password=hashed_password,
                        email=admin_email,
                        role=UserRole.ADMIN.value,
                        is_verified=True,
                        verification_code=None,
                        avatar_path=None,
                        avatar_hash=None,
                        create_time=datetime.now().isoformat(),
                        last_login_time=None,
                    )
                )
                await session.commit()
                global_logger.info("main", f"初始管理员创建成功：用户名={admin_username}")
            
        # 初始化支付服务
        payment_service.initialize()
            
    except Exception as e:
        global_logger.error('main', f"创建初始管理员或初始化服务失败：{e}")
    
    global_logger.info('main', "初始化检查完成")
    
    yield
    
    # ========== 关闭事件 ==========
    global_logger.info('main', "正在关闭应用...")
    
    # 安全关闭所有第三方服务
    await service_manager.stop_all()
    
    global_logger.info('main', "应用已完全关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="期刊平台 API", 
    description="期刊平台投稿站后端 API",
    version="2.0.0",  # 升级到 2.0 版本，标记重构完成
    lifespan=lifespan
)

# 配置核心功能
setup_core(app)

# 注册重构后的 v1 版本路由（所有子模块已在 api/v1/__init__.py 中注册）
app.include_router(v1_router)


@app.get("/", tags=["健康检查"])
async def root():
    """健康检查接口"""
    return {
        "message": "期刊平台 API 服务运行正常",
        "time": datetime.now().isoformat(),
        "version": "2.0.0"
    }
