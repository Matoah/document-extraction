from pydantic import BaseModel, Field
from graph.document.state.document_state import DocumentState
from model.standard_specification import StandardSpecification

class PageContext(BaseModel):
    """页面上下文"""

    page_list: list[list[dict]] = Field(default_factory=list, description="文档页面数据")

    document_state: DocumentState = Field(default=None, description="文档状态")

    standard_specification: StandardSpecification = Field(default=None, description="标准规范")
