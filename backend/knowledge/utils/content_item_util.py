from model.image import Image
from type.document_content_item import DocumentContentItem
from model.toc import TOC
from model.foreword import Foreword
from model.announcement import Announcement


def is_top_level_item(content_item: DocumentContentItem) -> bool:
    """判断是否为顶级节点"""
    return isinstance(content_item, Announcement) or isinstance(content_item, Foreword) or isinstance(content_item, TOC)

def is_atomic__item(content_item: DocumentContentItem) -> bool:
    """判断是否为原子节点"""
    return isinstance(content_item, Image)
