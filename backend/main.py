import sys
import os
# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tomllib
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from contextlib import asynccontextmanager

from utils.log import global_logger
from utils.file import load_toml
from core.config import setup_core
from api.v1.user import user_router
from api.v1.journal import journal_router
from api.v1.review import review_router
from api.v1.admin import admin_router

CONFIGS_DIR = Path(f'./configs')

# 加载配置文件
configs = {}

# 首先加载global.toml配置
global_config_path = CONFIGS_DIR / 'global.toml'
global_config = load_toml(global_config_path)
configs['global'] = global_config

# 加载其他配置文件
other_config_files = [f for f in CONFIGS_DIR.glob('*.toml') if f.name != 'global.toml']
for config_file in other_config_files:
    config = load_toml(config_file)
    configs[config_file.stem] = config

def check_dirs(a_dict: dict, prefix: str = '') -> None:
    """
    递归检查并自动创建配置文件中声明的目录/路径字段所对应的物理目录
    
    参数:
        a_dict: 待检查的配置字典，可能嵌套多层
        prefix: 当前层级的字段前缀，用于拼出完整的配置键名
    
    逻辑:
        1. 遍历字典中的每一项
        2. 如果值是字典，继续递归往里钻
        3. 如果值是字符串，且键名里带"dir"或以"path"结尾，就认为这是目录路径
        4. 如果该路径不存在，就自动创建，并记录日志
    """
    # 遍历当前层的所有键值对
    for key, value in a_dict.items():
        # 拼出完整的键名，方便日志和后续判断
        full_key = f"{prefix}.{key}" if prefix else key
        
        # 如果值还是字典，继续递归
        if isinstance(value, dict):
            check_dirs(value, full_key)
        
        # 如果值是字符串，且键名暗示它是目录或路径，就处理
        elif isinstance(value, str) and ('dir' in full_key or full_key.endswith('path')):
            # 把字符串转成Path对象，方便操作
            path = Path(value)
            
            # 如果路径不存在，就创建它
            if not path.exists():
                # parents=True 确保父目录一起被创建 
                path.mkdir(parents=True)
                # 记录日志，方便运维排查
                global_logger.info('config', f'创建目录: {path}')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    global_logger.info('main', "启动应用")
    
    # 执行初始化检查工作
    global_logger.info('config', "开始执行初始化检查")
    
    # 检查并创建配置中声明的目录路径
    for config_name, config in configs.items():
        global_logger.info('config', f'检查配置: {config_name}')
        check_dirs(config)
    
    # 数据库初始化 - 使用新的标准化架构
    from database.service.database_service import db_manager
    global_logger.info('database', "开始初始化标准化数据库架构")
    
    # 初始化所有数据库服务
    await db_manager.initialize_all()
    
    global_logger.info('database', "数据库初始化完成")
    
    # Redis连接初始化
    from utils.redis import redis_client
    redis_config = global_config['global']
    await redis_client.connect(
        host=redis_config.get('redis_addr', 'localhost:6379'),
        password=redis_config.get('redis_password', ''),
        db=redis_config.get('redis_db', 0)
    )
    global_logger.info('redis', "Redis连接初始化完成")
    
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
v1_router.include_router(journal_router)
v1_router.include_router(review_router)
v1_router.include_router(admin_router)

# 将v1路由组注册到主应用
app.include_router(v1_router)

@app.get("/", tags=["健康检查"])
async def root():
    return {"message": "期刊平台API服务运行正常", "time": datetime.now().isoformat()}
