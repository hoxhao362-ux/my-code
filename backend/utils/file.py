import tomllib
from pathlib import Path

def load_toml(path: Path) -> dict:
    with open(path, 'rb') as f:
        config = tomllib.load(f)
    return config
