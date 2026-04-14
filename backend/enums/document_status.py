from enum import Enum


class DocumentStatus(str, Enum):
    """文档状态"""

    """未改变"""
    NO_CHANGED = "no_changed"

    """错误"""
    ERROR = "error"

    """等待"""
    WAITING = "waiting"

    """解析中"""
    PARSING = "parsing"

    """清理中"""
    CLEANING = "cleaning"

    """分块中"""
    SPLITTING = "splitting"

    """索引中"""
    INDEXING = "indexing"

    """已完成"""
    COMPLETED = "completed"
