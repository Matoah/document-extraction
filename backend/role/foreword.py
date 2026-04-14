from pydantic import BaseModel, Field
from pathlib import Path
from role.core import JsonLLM

class ForewordInfo(BaseModel):
    """前言信息"""

    contact_person: str = Field(default="", description="联系人")

    contact_address: str = Field(default="", description="联系地址")

    contact_organization: str = Field(default="", description="联系单位")

    postal_code: str = Field(default="", description="邮编")

    phone: str = Field(default="", description="电话")

    fax: str = Field(default="", description="传真")

    email: str = Field(default="", description="电子邮箱")

    chief_editor_organization: str = Field(default="", description="主编单位")

    participating_organizations: str = Field(default="", description="参编单位")

    chief_reviewer: str = Field(default="", description="主审")

    review_participants: str = Field(default="", description="参与审查人员")

    chief_editor: str = Field(default="", description="主编")

    main_contributors: str = Field(default="", description="主要参编人员")

    contributors: str = Field(default="", description="参加人员")


class Foreword(JsonLLM[ForewordInfo]):
    """前言角色"""

    def __init__(self):
        super().__init__()
        self._system_prompt = None

    def _get_json_schema(self):
        """获取JSON模式"""
        return ForewordInfo

    def _build_system_prompt(self) -> ForewordInfo:
        """构建系统提示"""
        if self._system_prompt is None:
            prompt_path = Path(__file__).parent / "prompts/foreword.txt"
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        return self._system_prompt
