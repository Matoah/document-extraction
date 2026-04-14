from pydantic import BaseModel, Field

from model.origin_document import OriginDocument
from model.document import Document

class DocumentState(BaseModel):
    """文档状态定义"""

    """原始文档"""
    origin_document: OriginDocument = Field(description="原始文档")

    """文档"""
    document: Document | None = Field(default=None, description="文档")
