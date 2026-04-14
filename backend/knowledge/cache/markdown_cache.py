from pathlib import Path
from utils.path_util import resolve_dir_path, resolve_file_path

dir_path = Path(__file__).parent.parent.parent.parent/"markdown_cache"

def get_file_name(doc_name: str) -> str:
    """获取文件名"""
    return doc_name[:doc_name.rindex(".")]+".md"

def _get_specification_cache_path(specification_code: str) -> Path:
    """获取标准规范缓存路径"""
    return resolve_dir_path(dir_path, specification_code)

def get_file_path(spec_code: str, doc_name: str) -> Path:
    """获取文件路径"""
    return resolve_file_path(_get_specification_cache_path(spec_code), file_name=get_file_name(doc_name))

def exists(spec_code: str, doc_name: str) -> bool:
    """检查文件是否存在"""
    file_path = get_file_path(spec_code, doc_name)
    return file_path.exists()

def cache_markdown(spec_code: str, doc_name: str, content: str):
    """缓存Markdown内容"""
    file_path = get_file_path(spec_code, doc_name)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        f.write(content)

def get_markdown(spec_code: str, doc_name: str):
    """获取Markdown内容"""
    if exists(spec_code, doc_name):
        file_path = get_file_path(spec_code, doc_name)
        return file_path.read_text(encoding="utf-8")
    return None
