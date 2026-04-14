from pydantic import BaseModel, Field
from type.document_content_item import DocumentContentItem
from graph.document.state.document_state import DocumentState


class PageState(BaseModel):
    page_data: list[dict] = Field(description="页面数据")

    specification_code: str = Field(description="规格代码")

    document_name: str = Field(description="文档名称")

    page_index: int = Field(description="页码")

    page_step: int = Field(description="页码步长", default=1)


