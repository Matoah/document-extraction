from pydantic import BaseModel, Field
from pathlib import Path
from role.core import JsonLLM

class SymbolInfo(BaseModel):

    symbol: str = Field(description="符号")

    alias: str | None = Field(default=None, description="别名")

    name: str = Field(description="中文名称")

    unit: str | None = Field(default=None, description="单位")

class SymbolResult(BaseModel):

    type: str = Field(description="类型")

    definition: list[SymbolInfo] | None = Field(default=None, description="符号定义")


class Symbol(JsonLLM[SymbolResult]):
    """符号"""

    def __init__(self):
        super().__init__()
        self._system_prompt = None

    def _get_json_schema(self):
        """获取JSON模式"""
        return SymbolResult

    def _build_system_prompt(self) -> SymbolResult:
        """构建系统提示"""
        if self._system_prompt is None:
            prompt_path = Path(__file__).parent / "prompts/symbol.txt"
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        return self._system_prompt
