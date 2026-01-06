import sys
import os
# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from contextlib import asynccontextmanager

from utils.log import global_logger
from core.config import setup_core, config
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
    
    # 数据库初始化 - 使用新的标准化架构
    from database.service.database_service import db_manager
    global_logger.info('database', "开始初始化标准化数据库架构")
    
    # 初始化所有数据库服务
    await db_manager.initialize_all()
    
    global_logger.info('database', "数据库初始化完成")
    
    # Redis连接初始化
    from utils.redis import redis_client
    try:
        # 使用新的配置访问方式
        redis_host = config["global.global.redis_host"]
        redis_password = config["global.global.redis_password"]
        redis_db = config["global.global.redis_db"]
        
        await redis_client.connect(
            host=redis_host,
            password=None,
            db=redis_db
        )
        global_logger.info('redis', "Redis连接初始化完成")
    except AttributeError as e:
        global_logger.error('redis', f"Redis配置不存在或不完整: {e}")
    
    global_logger.info('main', "初始化检查完成")
    yield
    # 关闭事件
    await redis_client.close()
    global_logger.info('main', "关闭应用")

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
