from pydantic import BaseModel, Field

from model.standard_specification import StandardSpecification
from model.standard_specification_config import StandardSpecificationConfig
from model.document import Document


class MainState(BaseModel):

    standard_specification_config: StandardSpecificationConfig = Field(default_factory=StandardSpecificationConfig, description="标准规范配置")

    standard_specification: StandardSpecification = Field(default_factory=StandardSpecification, description="标准规范定义")

    document_list: list[Document] = Field(default_factory=list, description="文档列表")