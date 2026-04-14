from pydantic import BaseModel, Field
from pathlib import Path

from role.core import JsonLLM


class NoticeInfo(BaseModel):
    """通知信息"""

    title: str = Field(default="",description="通知标题")

    code: str = Field(default="",description="通知编号")

    content: str = Field(default="",description="通知内容")

    release_org: str = Field(default="",description="发文机关")

    release_date: str = Field(default="",description="发文日期")

class Notice(JsonLLM[NoticeInfo]):
    """通知解析"""

    def __init__(self):
        super().__init__()
        self._system_prompt = None

    def _build_system_prompt(self):
        """构建系统提示"""
        if self._system_prompt is None:
            prompt_path = Path(__file__).parent / "prompts/notice.txt"
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        return self._system_prompt

    def _get_json_schema(self):
        """获取JSON模式"""
        return NoticeInfo
