from pydantic import BaseModel, Field


class OriginDocument(BaseModel):
    """原始文档"""

    name: str = Field(description="文档名称")

    size: int = Field(default=0, description="文档大小")

    create_time: str = Field(description="创建时间")

    modify_time: str = Field(description="最后修改时间")

    page_list: list[list[dict]] = Field(default_factory=list, description="文档内容")

    md5: str = Field(description="文档md5值")
