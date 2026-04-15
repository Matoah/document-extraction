from pydantic import BaseModel, Field


class Symbol(BaseModel):
    """符号"""

    symbol: str = Field(description="符号")

    alias: str | None = Field(default=None, description="别名")

    name: str = Field(description="中文名称")

    unit: str | None = Field(default=None, description="单位")

    content: str = Field(default="", description="原始内容")

    def to_md_script(self) -> str:
        """将文档段落转换为Markdown脚本"""
        raise NotImplementedError

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建文档段落"""
        raise NotImplementedError