import sys
import os
# 添加backend目录到Python路径
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

from api.v1.user import user_router
from api.v1.submit import submit_router
from api.v1.review import review_router
from api.v1.admin import admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    global_logger.info('main', "启动应用")
    
    # 执行初始化检查工作
    global_logger.info('config', "开始执行初始化检查")
    
    # 检查并创建配置中声明的目录路径
    config.check_dirs()
    
    # 启动所有已注册的第三方服务
    # 逻辑：service_manager.start_all() 会触发每个服务单例内部定义的定制化 start() 计划
    try:
        await service_manager.start_all()
    except Exception as e:
        global_logger.error('main', f"第三方服务集群启动失败: {e}")
        # 根据业务需求决定是否终止应用启动
        # raise e
    
    # 检查并创建初始管理员
    try:
        async with db_manager.get_session() as session:
            admin_uid = await session.scalar(select(User.uid).where(User.role == "admin"))
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
                        role="admin",
                        is_verified=True,
                        verification_code=None,
                        avatar_path=None,
                        avatar_hash=None,
                        create_time=datetime.now().isoformat(),
                        last_login_time=None,
                    )
                )
                await session.commit()
                global_logger.info("main", f"初始管理员创建成功: 用户名={admin_username}")
            
        # 初始化支付服务
        payment_service.initialize()
            
    except Exception as e:
        global_logger.error('main', f"创建初始管理员或初始化服务失败: {e}")
    
    global_logger.info('main', "初始化检查完成")
    
    yield
    
    # 关闭事件
    global_logger.info('main', "正在关闭应用...")
    
    # 安全关闭所有第三方服务（调用每个单例内部定义的 stop() 计划）
    await service_manager.stop_all()
    
    global_logger.info('main', "应用已完全关闭")

# 创建FastAPI应用
app = FastAPI(
    title="期刊平台API", 
    description="期刊平台投稿站后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置核心功能
setup_core(app)

# 注册路由，添加版本前缀
from fastapi import APIRouter

# 创建v1版本的API路由组
v1_router = APIRouter(prefix="/api/v1")

# 将所有v1路由注册到v1路由组
v1_router.include_router(user_router)
v1_router.include_router(submit_router)
v1_router.include_router(review_router)
v1_router.include_router(admin_router)

# 将v1路由组注册到主应用
app.include_router(v1_router)

@app.get("/", tags=["健康检查"])
async def root():
    return {"message": "期刊平台API服务运行正常", "time": datetime.now().isoformat()}
