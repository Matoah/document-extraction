from pydantic import BaseModel, Field


class StandardSpecificationConfig(BaseModel):

    plate: str = Field(description="板块")

    module: str|None = Field(default=None, description="模块")

    code: str = Field(description="编号")

    name: str = Field(description="名称")

    chief_org: str = Field(description="主编单位")

    chief_editor: str = Field(description="主编")

    contact_name: str = Field(description="联系人姓名")

    approval_department: str = Field(default="", description="批准部门")

    contact_phone: str = Field(default="", description="联系电话")

    contact_email: str|None = Field(default=None, description="联系邮箱")

    contact_address: str = Field(default="", description="联系地址")

    file_names: list[str] = Field(default_factory=list, description="文件名")

