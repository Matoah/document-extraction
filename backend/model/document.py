from typing import Union, Self

from pydantic import BaseModel, Field

from model.origin_document import OriginDocument
from model.person import Person
from model.organization import Organization
from model.announcement import Announcement
from model.code import Code
from model.image import Image
from model.notice import Notice
from model.symbol import Symbol
from model.term import Term
from model.toc import TOC
from model.table import Table
from model.text import Text
from model.equation import Equation
from model.foreword import Foreword


class Document(BaseModel):
    """文档"""

    name: str = Field(description="文档名称")

    size: int = Field(default=0, description="文档大小")

    create_time: str = Field(description="创建时间")

    modify_time: str = Field(description="最后修改时间")

    md5: str = Field(description="文档md5码")

    chief_editor: list[Person] = Field(default_factory=list, description="主编")

    main_contributors: list[Person] = Field(default_factory=list, description="主要参编人员")

    contributors: list[Person] = Field(default_factory=list, description="参加人员")

    chief_reviewer: list[Person] = Field(default_factory=list, description="主审")

    reviewing_participant: list[Person] = Field(default_factory=list, description="参审人员")

    chief_editor_organization: list[Organization] = Field(default_factory=list, description="主编单位")

    participating_organization: list[Organization] = Field(default_factory=list, description="参编单位")

    contact_person: list[Person] = Field(default_factory=list, description="联系人")

    contact_organization: list[Organization] = Field(default_factory=list, description="联系单位")

    content_list: list[Union[
        Announcement, Code, Equation, Image, Notice, TOC, Table, Text, Foreword]] = Field(
        default_factory=list, description="内容列表")

    term_list: list[Term] = Field(default_factory=list, description="术语")

    symbol_list: list[Symbol] = Field(default_factory=list, description="符号")

    @classmethod
    def from_original_document(cls, origin_document: OriginDocument) -> Self:
        """从原始文档创建文档"""
        return cls(
            name=origin_document.name,
            size=origin_document.size,
            create_time=origin_document.create_time,
            modify_time=origin_document.modify_time,
            md5=origin_document.md5
        )
