from enums.document_content_type import DocumentContentType
from model.base import DocumentContent
from pydantic import Field


class Image(DocumentContent):
    """图片段落"""

    type: DocumentContentType = Field(default=DocumentContentType.IMAGE, description="类型")

    code: str = Field(description="图片编号")

    title: str = Field(description="图片名称")

    footer_notes: list[str] = Field(default_factory=list, description="图片脚注")

    desc: str = Field(default="", description="图片描述")

    path: str = Field(description="图片路径")

    def to_md_script(self) -> str:
        """转换为Markdown脚本"""
        script = [""]
        img_script = f"![]({self.path})"
        title = ""
        if self.code:
            title += self.code
        if self.title:
            title += " "
            title += self.title
        if self.footer_notes:
            if title:
                script.append(title)
            script.append(img_script)
        else:
            script.append(img_script)
            if title:
                script.append(title)
        if self.desc:
            script.append(self.desc)
        return "  \n".join(script)

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建图片段落"""
        raise NotImplementedError("从新内容列表创建图片段落不支持")

