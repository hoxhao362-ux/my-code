import os
import re
import tomllib
from pathlib import Path
from typing import Any
from utils.log import global_logger
from dotenv import load_dotenv

# 后端目录 backend/ 与仓库根目录（与 docker-compose.yml、根 .env 同级）
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_DIR.parent

_env_loaded = False
for _env_path in (_REPO_ROOT / ".env", _BACKEND_DIR / ".env"):
    if _env_path.is_file():
        load_dotenv(_env_path)
        global_logger.info("config", f"已加载环境变量: {_env_path}")
        _env_loaded = True
        break
if not _env_loaded:
    load_dotenv()
    global_logger.warning("config", "未在仓库根或 backend 下找到 .env，已尝试从当前工作目录加载")

def _replace_env_vars(data: Any) -> Any:
    """
    递归遍历配置字典，替换所有的环境变量占位符 ${ENV_VAR}
    
    Args:
        data: 配置数据，可能是字典、列表或字符串等基本类型
        
    Returns:
        替换环境变量后的数据
    """
    if isinstance(data, dict):
        return {k: _replace_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_replace_env_vars(v) for v in data]
    elif isinstance(data, str):
        # 匹配 ${ENV_VAR} 格式的占位符
        pattern = re.compile(r'\$\{([^}]+)\}')
        
        def replacer(match):
            env_name = match.group(1)
            env_value = os.environ.get(env_name)
            if env_value is not None:
                global_logger.debug('config', f"成功从环境变量加载配置项: {env_name}")
                return env_value
            global_logger.warning('config', f"未找到环境变量: {env_name}，将保留原占位符")
            return match.group(0)
            
        return pattern.sub(replacer, data)
    return data

def load_toml(path: Path) -> dict:
    """
    读取并解析 TOML 文件，同时将内容中的环境变量占位符替换为实际环境变量值
    
    Args:
        path: TOML 文件的路径
        
    Returns:
        解析并替换后的配置字典
    """
    if not path.exists():
        raise FileNotFoundError(f"TOML文件不存在喵: {path}")
    try:
        with open(path, 'rb') as f:
            config = tomllib.load(f)
            # 解析完成后，替换可能存在的环境变量占位符
            config = _replace_env_vars(config)
            return config
    except Exception as e:
        raise RuntimeError(f"加载TOML文件失败喵: {e}")
    
def get_file_from_hash_bucket(hash_value: str, bucket_dir: Path | str) -> Path:
    """根据哈希值获取文件路径
    
    Args:
        hash_value (str): 文件哈希值
        bucket_dir (Path): 哈希桶目录路径
        
    Returns:
        Path: 文件完整路径
    """
    if isinstance(bucket_dir, str):
        bucket_dir = Path(bucket_dir)
    # 构建文件路径：bucket_dir/hash_value[0:2]/hash_value[2:4]/hash_value[4:]
    file_path = bucket_dir / hash_value[0:2] / hash_value[2:4] / hash_value
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    return file_path