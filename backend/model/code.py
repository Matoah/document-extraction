from enums.document_content_type import DocumentContentType
from model.base import DocumentContent
from pydantic import Field


class Code(DocumentContent):
    """代码段落"""

    type: DocumentContentType = Field(default= DocumentContentType.CODE, description="类型")

    code_caption: list[str] = Field(description="代码标题")

    code_body: str = Field(description="代码主体")

    code_language: str = Field(description="代码语言")

    def to_md_script(self) -> str:
        """转换为Markdown脚本"""
        script = []
        if self.code_caption:
            script.extend(self.code_caption)
        if self.code_body:
            script.append("")
            script.append(f"```{self.code_language}")
            script.append(self.code_body)
            script.append("```")
        return "  \n".join(script)

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建代码段落"""
        new_code = Code(**self.model_dump())
        new_code.code_body = "".join(new_content_list)
        return new_code
