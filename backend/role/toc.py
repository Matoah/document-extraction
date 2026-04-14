from pydantic import BaseModel, Field
from role.core import JsonLLM
from pathlib import Path

class TOCInfoItem(BaseModel):
    """目录项角色"""
    title: str = Field(description="目录项标题")
    doc_page_index: int = Field(description="目录项所在文档页码")
    children: list["TOCInfoItem"] = Field(description="子目录项列表", default_factory=list)


class TOCInfo(BaseModel):
    """目录信息角色"""
    title: str = Field(description="目录页标题")

    items: list[TOCInfoItem] = Field(description="目录项列表", default_factory=list)


class TOC(JsonLLM):
    """目录角色"""
    def __init__(self):
        super().__init__()
        self._system_prompt = None

    def _get_json_schema(self):
        """获取JSON模式"""
        return TOCInfo

    def _build_system_prompt(self) -> TOCInfo:
        """构建系统提示"""
        if self._system_prompt is None:
            prompt_path = Path(__file__).parent / "prompts/toc.txt"
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        return self._system_prompt