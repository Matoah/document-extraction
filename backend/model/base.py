from abc import abstractmethod, ABC

from pydantic import BaseModel, Field

from enums.document_content_type import DocumentContentType


class DocumentContent(BaseModel, ABC):
    """文档内容，作为基类使用"""

    type: DocumentContentType = Field(default=DocumentContentType.TEXT, description="类型")

    page_index: int = Field(default=-1, description="页码，文档中真实页码，从0开始，-1为未设置")

    doc_page_index: int = Field(default=-1, description="文档中的页码，非真实页码，-1为未设置")

    def merge(self, next_content: "DocumentContent") -> bool:
        """合并下一个分块,使用场景：当文档切片时，连续同类节点为同一分块，是否应该合并为一个分块"""
        return False

    @abstractmethod
    def to_md_script(self) -> str:
        """将文档内容转换为Markdown脚本"""
        raise NotImplementedError

    @abstractmethod
    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建文档内容"""
        raise NotImplementedError

class DocumentBlock(BaseModel, ABC):
    """文档块，作为基类使用"""

    type: DocumentContentType = Field(default=DocumentContentType.TEXT,description="类型")

    page_index: list[int] = Field(description="文档中包含的页码索引列表,从0开始", default_factory=list)

    doc_page_index: list[int] = Field(description="文档中包含的页码索引列表,文档中的页码，非真实页码", default_factory=list)

    def merge(self, next_block: "DocumentBlock") -> bool:
        """合并下一个分块,使用场景：当文档切片时，连续同类节点为同一分块，是否应该合并为一个分块"""
        return False

    @abstractmethod
    def to_md_script(self) -> str:
        """将文档块转换为Markdown脚本"""
        raise NotImplementedError

    @abstractmethod
    def from_new_content(self, new_content_list: list[str]):
        """从新内容列表创建文档内容"""
        raise NotImplementedError
