from pydantic import Field

from model.base import DocumentBlock, DocumentContent
from enums.document_content_type import DocumentContentType


class TOCItem(DocumentContent):
    """目录项"""
    id: int = Field(description="目录项ID")

    title: str = Field(description="目录项标题")

    page_index: int = Field(description="目录项所在页码索引, -1表示未解析", default=-1)

    parent_id: int = Field(description="目录项父项ID, -1表示根目录项", default=-1)

    children: list["TOCItem"] = Field(description="目录项子项列表", default_factory=list)

    def to_md_script(self) -> str:
        """将目录项转换为Markdown脚本"""
        return "  \n".join([self.title,*[item.to_md_script() for item in self.children]])

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建目录项"""
        raise NotImplementedError("从新内容列表创建文档目录不支持")

class TOC(DocumentBlock):
    """文档目录"""

    type: DocumentContentType = Field(default=DocumentContentType.TOC, description="类型")

    title: str = Field(description="目录标题")

    items: list[TOCItem] = Field(description="目录项列表", default_factory=list)

    temp: str = Field(description="临时目录标题", default="")

    def to_md_script(self) -> str:
        """将文档目录转换为Markdown脚本"""
        if self.temp:
            return self.temp
        script = []
        if self.title:
            script.append("# "+self.title)
        for item in self.items or []:
            script.append(item.to_md_script())
        return "  \n".join(script)

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建文档目录"""
        new_toc = TOC(**self.model_dump())
        new_toc.temp = "".join(new_content_list)
        return new_toc
