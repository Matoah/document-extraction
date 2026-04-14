import json
from pathlib import Path

dir_path = Path(__file__).parent.parent.parent.parent/"knowledge_cache"

file_path = dir_path/"upload_file_cache.json"

dir_path.mkdir(parents=True, exist_ok=True)

upload_file_cache = {}

if file_path.exists():
    with open(file_path) as f:
        upload_file_cache = json.load(f)

def exists(key: str) -> bool:
    """检查文件是否存在"""
    return key in upload_file_cache

def get_cache(key: str) -> str:
    """获取文件ID"""
    return upload_file_cache.get(key) if exists(key) else None

def set_cache(key: str, value: str) -> None:
    """设置文件ID"""
    if get_cache(key) != value:
        upload_file_cache[key] = value
        with open(file_path, "w") as file:
            json.dump(upload_file_cache, file, ensure_ascii=False, indent=4)
