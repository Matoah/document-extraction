from pydantic import Field

from enums.document_content_type import DocumentContentType
from model.base import DocumentContent


class Equation(DocumentContent):
    """公式段落"""

    type: DocumentContentType = Field(default= DocumentContentType.EQUATION, description="类型")

    content: str = Field(default="", description="公式内容")

    format: str = Field(default="latex" , description="公式格式")

    tag: str = Field(default="", description="标签")

    def to_md_script(self) -> str:
        """将公式段落转换为Markdown脚本"""
        return f"  \n{self.content}"

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建公式段落"""
        new_equation = Equation(**self.model_dump())
        new_equation.content = "".join(new_content_list)
        return new_equation
