from model.announcement import Announcement
from model.code import Code
from model.equation import Equation
from model.image import Image
from model.notice import Notice
from model.table import Table
from enums.document_content_type import DocumentContentType
from model.text import Text
from model.toc import TOC
from model.foreword import Foreword
from type.document_content_item import DocumentContentItem

mapping = {DocumentContentType.TEXT: Text, DocumentContentType.CODE: Code, DocumentContentType.IMAGE: Image,
           DocumentContentType.EQUATION: Equation, DocumentContentType.TABLE: Table,
           DocumentContentType.ANNOUNCEMENT: Announcement, DocumentContentType.NOTICE: Notice,
           DocumentContentType.TOC: TOC, DocumentContentType.FOREWORD: Foreword}


def create(config: dict) -> DocumentContentItem:
    type = config.get("type")
    if type in mapping:
        return mapping[type](**config)
    else:
        raise ValueError(f"未知类型: {type}")
