import tomllib
from pathlib import Path

def load_toml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"TOML文件不存在喵: {path}")
    try:
        with open(path, 'rb') as f:
            config = tomllib.load(f)
            return config
    except Exception as e:
        raise RuntimeError(f"加载TOML文件失败喵: {e}")
    
    
