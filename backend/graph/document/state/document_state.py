from pydantic import BaseModel, Field

from model.origin_document import OriginDocument
from model.document import Document
from model.standard_specification import StandardSpecification


class DocumentState(BaseModel):
    """文档状态定义"""

    spec_code: str = Field(description="标准规范编号")

    standard_specification: StandardSpecification = Field(description="标准规范定义")

    """原始文档"""
    origin_document: OriginDocument = Field(description="原始文档")

    """文档"""
    document: Document | None = Field(default=None, description="文档")
