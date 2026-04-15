from pydantic import Field

from model.base import DocumentContent

class Term(DocumentContent):
    """术语"""

    abbr: str | None = Field(default=None, description="缩写")

    name_zh: str = Field(description="中文术语名称")

    name_en: str | None = Field(default=None, description="英文术语名称")

    definition: str = Field(description="术语定义")

    text_level: int = Field(default=0, description="文本等级")

    def to_md_script(self) -> str:
        """将文档段落转换为Markdown脚本"""
        raise NotImplementedError

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建文档段落"""
        raise NotImplementedError