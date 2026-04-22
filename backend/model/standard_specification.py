from pydantic import BaseModel, Field
from enums.standard import StandardNature
from model.standard_specification_config import StandardSpecificationConfig

class StandardSpecification(BaseModel):
    """标准规范定义"""

    plate: str = Field(description="板块")

    module: str|None = Field(default=None, description="模块")

    code: str = Field(description="标准规范编号")

    name: str = Field(description="标准规范名称")

    standard_nature: StandardNature = Field(description="标准规范类型", default=StandardNature.MANDATORY)

    domain: str = Field(description="适用领域", default="公路工程")

    @classmethod
    def from_config(cls, standard_specification_config: StandardSpecificationConfig):
        """从标准规范配置创建标准规范定义"""
        return cls(**standard_specification_config.model_dump())



