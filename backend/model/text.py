from pydantic import Field

from model.base import DocumentContent


class Text(DocumentContent):
    """文档段落"""

    content: str = Field(description="段落内容")

    text_level: int = Field(default=0, description="段落等级")

    def to_md_script(self) -> str:
        """将文档段落转换为Markdown脚本"""
        content = self.content.replace("\n", "  \n")
        return f"{'#'*self.text_level} {content}\n" if self.text_level else content+"  \n"


    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建文档段落"""
        new_text = Text(**self.model_dump())
        new_text.content = "".join(new_content_list)
        return new_text
