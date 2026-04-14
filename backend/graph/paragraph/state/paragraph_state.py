from typing import Optional

from pydantic import BaseModel, Field

from model.equation import Equation
from model.table import Table
from model.text import Text
from model.code import Code
from model.image import Image


class ParagraphState(BaseModel):
    """段落状态"""

    paragraph: dict = Field(description="段落数据")

    result: Optional[Equation | Image | Code | Text | Table] = Field(default=None, description="解析结果")

