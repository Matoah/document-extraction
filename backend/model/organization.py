from pydantic import BaseModel, Field

from model.person import Person


class Organization(BaseModel):
    """组织、单位定义"""

    name: str = Field(description="名称")

    address: str = Field(default="", description="地址")

    postal_code: str = Field(default="", description="邮编")

    email: str = Field(default="", description="电子邮箱")

    phone: str = Field(default="", description="联系电话")

    fax: str = Field(default="", description="传真号码")

    contact_person: list[Person] = Field(default_factory=list, description="联系人")

    def to_md_script(self) -> str:
        """将组织、单位转换为Markdown脚本"""
        return self.name
