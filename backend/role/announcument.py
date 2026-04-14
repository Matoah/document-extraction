from pydantic import BaseModel,Field

from role.core import JsonLLM
from pathlib import Path

class AnnouncementResult(BaseModel):
    """公告结果"""
    title: str = Field(description="标题")
    subject: str = Field(description="主题")
    code: str = Field(description="编号")
    content: str = Field(description="内容")
    release_org: str = Field(description="发文机关")
    release_date: str = Field(description="发文日期")
    issue_date: str = Field(description="印发日期")
    issue_org: str = Field(description="印发机关")

class Announcement(JsonLLM[AnnouncementResult]):
    """公告大模型"""

    def __init__(self):
        super().__init__()
        self._system_prompt = None

    def _build_system_prompt(self):
        """构建系统提示"""
        if self._system_prompt is None:
            prompt_path = Path(__file__).parent / "prompts/announcement.txt"
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        return self._system_prompt

    def _get_json_schema(self):
        """获取JSON模式"""
        return AnnouncementResult
