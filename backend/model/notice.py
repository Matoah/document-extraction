from pydantic import Field

from model.base import  DocumentBlock
from model.organization import Organization
from enums.document_content_type import DocumentContentType


class Notice(DocumentBlock):
    """通知定义"""

    type: DocumentContentType = Field(default=DocumentContentType.NOTICE, description="类型")

    title: str = Field(description="标题")

    code: str = Field(description="编号")

    content: str = Field(description="内容")

    release_org: Organization = Field(description="发文机关", default_factory=Organization)

    release_date: str = Field(description="发布日期")

    def to_md_script(self) -> str:
        """将通知段落转换为Markdown脚本"""
        script = [f"# {self.title}", "", self.code, "", self.content.replace("\n", "  \n")]
        if self.release_date:
            script.append("")
            script.append(self.release_org.to_md_script())
        if self.release_date:
            script.append("")
            script.append(self.release_date)
        return "  \n".join(script)

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建通知段落"""
        new_notice = Notice(**self.model_dump())
        new_notice.content = "".join(new_content_list)
        return new_notice
