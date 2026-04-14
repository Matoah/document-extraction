from pydantic import Field, BaseModel

from model.base import DocumentBlock
from model.organization import Organization
from enums.document_content_type import DocumentContentType


class Announcement(DocumentBlock, BaseModel):
    """公告定义"""

    type: DocumentContentType = Field(default=DocumentContentType.ANNOUNCEMENT, description="类型")

    title: str = Field(description="标题")

    subject: str = Field(description="主题")

    code: str = Field(description="编号")

    content: str = Field(description="内容")

    release_org: Organization = Field(description="发文机关")

    release_date: str = Field(description="发文日期")

    issue_date: str = Field(description="印发日期")

    issue_org: Organization = Field(description="印发机关")

    def to_md_script(self) -> str:
        """将公告段落转换为Markdown脚本"""
        script = [f"# {self.title}"]
        if self.code:
            script.append("")
            script.append(self.code)
        if self.subject:
            script.append("")
            script.append(f"## {self.subject}")
        script.append("")
        script.append(self.content.replace("\n", "  \n"))
        if self.release_org:
            script.append("")
            script.append(self.release_org.to_md_script())
        if self.release_date:
            script.append("")
            script.append(self.release_date)
        if self.issue_org:
            script.append("")
            script.append(self.issue_org.to_md_script())
        if self.issue_date:
            script.append("")
            script.append(self.issue_date)
        return "  \n".join(script)

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建公告段落"""
        new_announcement = Announcement(**self.model_dump())
        new_announcement.content = "".join(new_content_list)
        return new_announcement
