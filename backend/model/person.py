from pydantic import BaseModel, Field


class Person(BaseModel):
    """人员定义"""
    name: str = Field(description="名称")

    def to_md_script(self) -> str:
        """将人员转换为Markdown脚本"""
        return self.name
