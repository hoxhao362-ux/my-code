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