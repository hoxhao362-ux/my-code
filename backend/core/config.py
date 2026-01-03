from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from utils.file import load_toml
from utils.log import global_logger

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 只初始化一次
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # 配置目录路径
        self.CONFIGS_DIR = Path('./configs')
        
        # 确保配置目录存在
        if not self.CONFIGS_DIR.exists():
            self.CONFIGS_DIR.mkdir(parents=True)
            global_logger.info('config', f'创建配置目录: {self.CONFIGS_DIR}')
        
        # 加载所有配置文件
        self._configs = {}

        # 加载其他配置文件
        config_files = [f for f in self.CONFIGS_DIR.glob('*.toml')]
        for config_file in config_files:
            config = load_toml(config_file)
            self._configs[config_file.stem] = config
        self._initialized = True

    def __getitem__(self, key):
        """支持通过字典访问配置值，如 config["global.redis_addr"]"""
        if '.' not in key:
            # 直接访问表
            return getattr(self, key)
        
        # 解析表名和键名
        table_name, *keys = key.split('.')
        
        # 获取表
        table = getattr(self, table_name)
        
        # 遍历获取嵌套值
        value = table
        for k in keys:
            if isinstance(value, ConfigTable):
                value = getattr(value, k)
            else:
                raise KeyError(f"Invalid config path: '{key}'")
        
        return value
    
    def get(self, key, default=None):
        """支持get方法，如 config.get("global.redis_addr", "localhost:6379")"""
        try:
            return self[key]
        except (AttributeError, KeyError):
            return default
    
    def check_dirs(self):
        """检查并创建配置中声明的目录路径"""
        for config_name, config in self._configs.items():
            global_logger.info('config', f'检查配置: {config_name}')
            self._check_dirs(config, config_name)
    
    def _check_dirs(self, a_dict: dict, prefix: str = '') -> None:
        """递归检查并创建目录"""
        for key, value in a_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                self._check_dirs(value, full_key)
            elif isinstance(value, str) and ('dir' in full_key):
                path = Path(value)
                if not path.exists():
                    path.mkdir(parents=True)
                    global_logger.info('config', f'创建目录: {path}')

class ConfigTable:
    """配置表类，用于支持 config.table.key 访问"""
    def __init__(self, data):
        self._data = data
        
        # 将字典数据转换为属性
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, ConfigTable(value))
            else:
                setattr(self, key, value)
    
    def __getattr__(self, name):
        """获取属性"""
        if name in self._data:
            return getattr(self, name)
        raise AttributeError(f"ConfigTable object has no attribute '{name}'")
    
    def __repr__(self):
        return f"ConfigTable({self._data})"

# 创建全局配置实例
config = Config()

def setup_core(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.global_.cors_origins, 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
