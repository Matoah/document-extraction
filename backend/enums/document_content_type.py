from enum import Enum

class DocumentContentType(str, Enum):
    """文档内容类型"""

    """代码"""
    CODE = "code"

    """文本"""
    TEXT = "text"

    """图片"""
    IMAGE = "image"

    """表格"""
    TABLE = "table"

    """公式"""
    EQUATION = "equation"

    """目录"""
    TOC = "toc"

    """公告"""
    ANNOUNCEMENT = "announcement"

    """通知"""
    NOTICE = "notice"

    """前言"""
    FOREWORD = "foreword"
