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

    approved_by: str = Field(description="批准部门", default="")

    release_date: str = Field(description="发布日期", default="")

    effective_date: str = Field(description="实施日期", default="")

    category_level_1: str = Field(description="一级分类", default="")

    category_level_2: str = Field(description="二级分类", default="")

    type: str = Field(description="类型", default="")

    keywords: list[str] = Field(description="关键词", default_factory=list)

    stage: str = Field(description="生命周期阶段", default="")

    domain: str = Field(description="适用领域", default="公路工程")

    @classmethod
    def from_config(cls, standard_specification_config: StandardSpecificationConfig):
        """从标准规范配置创建标准规范定义"""
        return cls(**standard_specification_config.model_dump())



