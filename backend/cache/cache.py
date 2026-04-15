import hashlib
from pathlib import Path
import json
from utils.path_util import resolve_file_path, resolve_dir_path

cache_dir = Path(__file__).resolve().parent.parent.parent / "cache_data"
cache_dir.mkdir(parents=True, exist_ok=True)


def _get_specification_cache_path(specification_code: str) -> Path:
    """获取标准规范缓存路径"""
    return resolve_dir_path(cache_dir, specification_code)


def _get_document_cache_path(specification_code: str, document_name: str) -> Path:
    """获取文档缓存路径"""
    return resolve_dir_path(_get_specification_cache_path(specification_code), document_name)


def _get_announcement_cache_path(specification_code: str, document_name: str, announcement: str) -> Path:
    """获取公告缓存路径"""
    md5 = hashlib.md5(announcement.encode(encoding="utf-8")).hexdigest()
    return resolve_file_path(_get_document_cache_path(specification_code, document_name), "announcement",
                             file_name=f"{md5}.json")


def exist_announcement_cache(specification_code: str, document_name: str, announcement: str) -> bool:
    """检查是否存在公告缓存"""
    cache_file = _get_announcement_cache_path(specification_code, document_name, announcement)
    return cache_file.exists()


def cache_announcement(specification_code: str, document_name: str, announcement: str, data: dict):
    """缓存公告"""
    cache_file = _get_announcement_cache_path(specification_code, document_name, announcement)
    cache_data = {
        "announcement": announcement,
        "data": data
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=4), encoding="utf-8")


def get_announcement(specification_code: str, document_name: str, announcement: str) -> dict:
    """获取公告缓存"""
    cache_file = _get_announcement_cache_path(specification_code, document_name, announcement)
    with cache_file.open("r", encoding="utf-8") as f:
        cache_data = json.load(f)
        return cache_data.get("data", {})


def _get_notice_cache_path(specification_code: str, document_name: str, notice: str) -> Path:
    """获取通知缓存路径"""
    md5 = hashlib.md5(notice.encode(encoding="utf-8")).hexdigest()
    return resolve_file_path(_get_document_cache_path(specification_code, document_name), "notice",
                             file_name=f"{md5}.json")


def exist_notice_cache(specification_code: str, document_name: str, notice: str) -> bool:
    """检查是否存在通知缓存"""
    cache_file = _get_notice_cache_path(specification_code, document_name, notice)
    return cache_file.exists()


def cache_notice(specification_code: str, document_name: str, notice: str, data: dict):
    """缓存通知"""
    cache_file = _get_notice_cache_path(specification_code, document_name, notice)
    cache_data = {
        "notice": notice,
        "data": data
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=4), encoding="utf-8")


def get_notice(specification_code: str, document_name: str, notice: str) -> dict:
    """获取通知缓存"""
    cache_file = _get_notice_cache_path(specification_code, document_name, notice)
    with cache_file.open("r", encoding="utf-8") as f:
        cache_data = json.load(f)
        return cache_data.get("data", {})


def _get_foreword_cache_path(specification_code: str, document_name: str, foreword: str) -> Path:
    """获取前言缓存路径"""
    md5 = hashlib.md5(foreword.encode(encoding="utf-8")).hexdigest()
    return resolve_file_path(_get_document_cache_path(specification_code, document_name), "foreword",
                             file_name=f"{md5}.json")


def exist_foreword_cache(specification_code: str, document_name: str, foreword: str) -> bool:
    """检查是否存在前言缓存"""
    cache_file = _get_foreword_cache_path(specification_code, document_name, foreword)
    return cache_file.exists()


def cache_foreword(specification_code: str, document_name: str, foreword: str, data: dict):
    """缓存前言"""
    cache_file = _get_foreword_cache_path(specification_code, document_name, foreword)
    cache_data = {
        "foreword": foreword,
        "data": data
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=4), encoding="utf-8")


def get_foreword(specification_code: str, document_name: str, foreword: str) -> dict:
    """获取前言缓存"""
    cache_file = _get_foreword_cache_path(specification_code, document_name, foreword)
    with cache_file.open("r", encoding="utf-8") as f:
        cache_data = json.load(f)
        return cache_data.get("data", {})


def _get_toc_cache_path(specification_code: str, document_name: str, toc: str) -> Path:
    """获取目录缓存路径"""
    md5 = hashlib.md5(toc.encode(encoding="utf-8")).hexdigest()
    return resolve_file_path(_get_document_cache_path(specification_code, document_name), "toc",
                             file_name=f"{md5}.json")


def exist_toc_cache(specification_code: str, document_name: str, toc: str) -> bool:
    """检查是否存在目录缓存"""
    cache_file = _get_toc_cache_path(specification_code, document_name, toc)
    return cache_file.exists()


def cache_toc(specification_code: str, document_name: str, toc: str, data: dict):
    """缓存目录"""
    cache_file = _get_toc_cache_path(specification_code, document_name, toc)
    cache_data = {
        "toc": toc,
        "data": data
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=4), encoding="utf-8")


def get_toc(specification_code: str, document_name: str, toc: str) -> dict:
    """获取目录缓存"""
    cache_file = _get_toc_cache_path(specification_code, document_name, toc)
    with cache_file.open("r", encoding="utf-8") as f:
        cache_data = json.load(f)
        return cache_data.get("data", {})

def _get_term_cache_path(specification_code: str, document_name: str, term_content: str) -> Path:
    """获取通知缓存路径"""
    md5 = hashlib.md5(term_content.encode(encoding="utf-8")).hexdigest()
    return resolve_file_path(_get_document_cache_path(specification_code, document_name), "term",
                             file_name=f"{md5}.json")

def exist_term_cache(specification_code: str, document_name: str, term_content: str) -> bool:
    """检查是否存在术语缓存"""
    cache_file = _get_term_cache_path(specification_code, document_name, term_content)
    return cache_file.exists()

def cache_term(specification_code: str, document_name: str, term_content: str, data: dict):
    """缓存术语"""
    cache_file = _get_term_cache_path(specification_code, document_name, term_content)
    cache_data = {
        "term": term_content,
        "data": data
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=4), encoding="utf-8")

def get_term(specification_code: str, document_name: str, term_content: str) -> dict:
    """获取术语缓存"""
    cache_file = _get_term_cache_path(specification_code, document_name, term_content)
    with cache_file.open("r", encoding="utf-8") as f:
        cache_data = json.load(f)
        return cache_data.get("data", {})

def _get_symbol_cache_path(specification_code: str, document_name: str, symbol: str) -> Path:
    """获取符号缓存路径"""
    md5 = hashlib.md5(symbol.encode(encoding="utf-8")).hexdigest()
    return resolve_file_path(_get_document_cache_path(specification_code, document_name), "symbol",
                             file_name=f"{md5}.json")

def exist_symbol_cache(specification_code: str, document_name: str, symbol: str) -> bool:
    """检查是否存在符号缓存"""
    cache_file = _get_symbol_cache_path(specification_code, document_name, symbol)
    return cache_file.exists()

def cache_symbol(specification_code: str, document_name: str, symbol: str, data: dict):
    """缓存符号"""
    cache_file = _get_symbol_cache_path(specification_code, document_name, symbol)
    cache_data = {
        "symbol": symbol,
        "data": data
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=4), encoding="utf-8")

def get_symbol(specification_code: str, document_name: str, symbol: str) -> dict:
    """获取符号缓存"""
    cache_file = _get_symbol_cache_path(specification_code, document_name, symbol)
    with cache_file.open("r", encoding="utf-8") as f:
        cache_data = json.load(f)
        return cache_data.get("data", {})


