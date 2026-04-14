from typing import Optional

from certifi import contents
from pydantic import Field

from enums.document_content_type import DocumentContentType
from model.base import DocumentBlock
from model.organization import Organization
from model.person import Person
import re

class Foreword(DocumentBlock):
    """前言"""

    type: DocumentContentType = Field(default=DocumentContentType.FOREWORD, description="类型")

    content: str = Field(default="", description="内容")

    contact_person: Optional[Person] = Field(default=None, description="联系人")

    contact_address: str = Field(default="", description="联系地址")

    contact_organization: Optional[Organization] = Field(default=None, description="联系单位")

    postal_code: str = Field(default="", description="邮编")

    phone: str = Field(default="", description="电话")

    fax: str = Field(default="", description="传真")

    email: str = Field(default="", description="电子邮箱")

    chief_editor_organization: list[Organization] = Field(default_factory=list, description="主编单位")

    participating_organization: list[Organization] = Field(default_factory=list, description="参编单位")

    chief_reviewer: list[Person] = Field(default_factory=list, description="主审")

    review_participants: list[Person] = Field(default_factory=list, description="参与审查人员")

    chief_editor: list[Person] = Field(default_factory=list, description="主编")

    main_contributors: list[Person] = Field(default_factory=list, description="主要参编人员")

    contributors: list[Person] = Field(default_factory=list, description="参加人员")

    def to_md_script(self) -> str:
        """将前言转换为Markdown脚本"""
        match = re.search(r"^[\n\s]*#*\s*前\s*言\s*\n",self.content, re.MULTILINE)
        content = self.content
        if match:
            content = self.content[match.end():]
        script = ["# 前言","", content.replace("\n", "  \n")]
        return "  \n".join(script)

    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建前言"""
        new_foreword = Foreword(**self.model_dump())
        new_foreword.content = "".join(new_content_list)
        return new_foreword

    def merge(self, next_foreword: "Foreword") -> bool:
        """合并前言"""
        self.content = "\n".join([self.content, next_foreword.content])
        return True
