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
from utils.database import db
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
    """检查并创建配置文件中声明的目录路径"""
    for key, value in a_dict.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            check_dirs(value, full_key)
        elif isinstance(value, str) and ('dir' in full_key or full_key.endswith('path')):
            path = Path(value)
            if not path.exists():
                path.mkdir(parents=True)
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
    
    # 数据库初始化
    from utils.database import db_manager, db
    database_dir = Path(global_config['global']['database_dir'])
    
    # 添加数据库实例到管理器
    database_config = configs.get('database', {})
    
    # 主数据库
    main_db_path = database_dir / 'journal.db'
    db_manager.add_database('main', main_db_path)
    
    # 管理员日志数据库
    admin_log_db_path = database_dir / database_config.get('admin_log_db', 'admin_log.db')
    db_manager.add_database('admin_log', admin_log_db_path)
    
    # 已删除文献数据库
    deleted_journal_db_path = database_dir / database_config.get('deleted_journal_db', 'deleted_journal.db')
    db_manager.add_database('deleted_journal', deleted_journal_db_path)
    
    # 连接并初始化所有数据库
    await db_manager.connect_all()
    await db_manager.create_all_tables()
    
    # 更新旧的db实例，保持兼容性
    db.db_path = main_db_path
    db.conn = db_manager.get_database('main').conn
    
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
    await db.close()
    await db_manager.close_all()
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
