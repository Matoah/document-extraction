from pydantic import BaseModel, Field


class ParagraphContext(BaseModel):
    """段落上下文"""

    page_index: int = Field(description="当前页码，真实页码")

    page_data: list[dict] = Field(description="页面数据")

    page_list: list[list[dict]] = Field(description="所有页面数据", default_factory=list)
