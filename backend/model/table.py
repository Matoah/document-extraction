from pydantic import Field

from enums.document_content_type import DocumentContentType
from model.base import DocumentContent


class Table(DocumentContent):
    """表格段落"""

    type: DocumentContentType = Field(default= DocumentContentType.TABLE, description="类型")

    img_path: str = Field(default=None, description="表格图片路径")

    code: str = Field(default=None, description="表格编号")

    title: str = Field(default=None, description="表格标题")

    table_body: str = Field(description="表格内容")

    # 表格是否续表
    is_continued: bool = Field(default=False, description="是否续表")

    footer_notes: list[str] = Field(default=None, description="表格脚注")

    def to_md_script(self) -> str:
        """将表格段落转换为Markdown脚本"""
        script = []
        title = ""
        if self.code:
            if self.code.startswith("表") or self.code.startswith("续表"):
                title += self.code
            else:
                prefix = "续表 " if self.is_continued else "表 "
                title += prefix + self.code
        if self.title:
            title += " " + self.title if title else self.title
        if title:
            script.append(title)
        if self.table_body:
            script.append("")
            script.append(self.table_body)
        if self.footer_notes:
            script.append("")
            for note in self.footer_notes:
                script.append(note)
        return "  \n".join(script)

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建表格段落"""
        new_table = Table(**self.model_dump())
        new_table.table_body = "".join(new_content_list)
        return new_table

