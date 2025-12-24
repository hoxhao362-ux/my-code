import tomllib
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI

from utils.log import global_logger
from utils.file import load_toml

CONFIGS_DIR = Path(f'./configs')
config_files = CONFIGS_DIR.glob('*.toml')

def check_dirs(a_dict: dict) -> None:
    for key, value in a_dict.items():
        if isinstance(value, dict):
            check_dirs(value)
        elif isinstance(value, str) and 'dir' in key:
            path = Path(value)
            if not path.exists():
                path.mkdir(parents=True)
                global_logger.info(f'创建目录: {path}')

for config_file in config_files:
    config = load_toml(config_file)
