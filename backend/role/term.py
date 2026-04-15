from pydantic import BaseModel, Field
from pathlib import Path
from role.core import JsonLLM

class TermInfo(BaseModel):
    """术语信息"""

    abbr: str | None = Field(default=None, description="缩写")

    name_zh: str = Field(description="中文术语名称")

    name_en: str | None = Field(default=None, description="英文术语名称")

    definition: str = Field(description="术语定义")

class TermResult(BaseModel):

    type: str = Field(description="类型")

    definition: list[TermInfo] | None = Field(default=None, description="术语定义")


class Term(JsonLLM[TermResult]):
    """术语"""

    def __init__(self):
        super().__init__()
        self._system_prompt = None

    def _get_json_schema(self):
        """获取JSON模式"""
        return TermResult

    def _build_system_prompt(self) -> TermResult:
        """构建系统提示"""
        if self._system_prompt is None:
            prompt_path = Path(__file__).parent / "prompts/term.txt"
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        return self._system_prompt