from pathlib import Path

path_resolve = {
    "/": "_2F_",
    "\\": "_5C_",
    ".": "_2E_",
}

def resolve_special_char(file_name: str) -> str:
    """处理文件名称，使其符合缓存目录名称"""
    for k, v in path_resolve.items():
        file_name = file_name.replace(k, v)
    return file_name

def resolve_dir_path(*parts: str | Path) -> Path:
    """解析目录路径"""
    resolved_parts = []
    for part in parts:
        if isinstance(part, Path):
            resolved_parts.append(part)
        else:
            resolved_parts.append(resolve_special_char(part))
    return Path(*resolved_parts).resolve()

def resolve_file_path(*parts: str | Path, file_name: str) -> Path:
    """解析路径"""
    resolved_parts = []
    for part in parts:
        if isinstance(part, Path):
            resolved_parts.append(part)
        else:
            resolved_parts.append(resolve_special_char(part))
    return Path(*resolved_parts, file_name).resolve()
