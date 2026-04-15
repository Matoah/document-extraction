from type.document_content_item import DocumentContentItem
from utils.token_util import count_tokens
from typing import Union

class Node:
    """树形节点"""

    def __init__(self):
        self.content: list[DocumentContentItem] = []
        self.node_level: int = 0
        self._token_count: int = -1
        self._title: DocumentContentItem | None = None
        self._markdown_content: str | None = None
        self._parent: Union["Node", None] = None

    def _clear_cache(self):
        """清除缓存"""
        self._token_count = -1
        self._markdown_content = None

    def set_node_level(self, node_level: int):
        """设置节点等级"""
        self.node_level = node_level

    def get_node_level(self) -> int:
        """获取节点等级"""
        return self.node_level

    def set_content(self, content: list[DocumentContentItem]):
        """设置节点内容"""
        self.content = content
        self._clear_cache()

    def get_content(self) -> list[DocumentContentItem]:
        """获取节点内容"""
        return self.content

    def set_title(self, title: DocumentContentItem):
        """设置节点标题"""
        self._title = title

    def get_title(self) -> DocumentContentItem:
        """获取节点标题"""
        return self._title

    def append_content(self, content: DocumentContentItem):
        """添加节点内容"""
        self.content.append(content)
        self._clear_cache()

    def set_parent(self, parent: Union["Node" , None]):
        """设置父节点"""
        self._parent = parent

    def get_parent(self) -> Union["Node",None]:
        """获取父节点"""
        return self._parent

    def _get_self_markdown_content(self) -> str:
        """获取当前节点的Markdown文本"""
        if self._markdown_content is None:
            script = [content.to_md_script() for content in self.content]
            self._markdown_content = "\n".join(script)
        return self._markdown_content

    def get_self_token_count(self) -> int:
        """获取当前节点的token数量"""
        if self._token_count < 0:
            self._token_count = count_tokens(self._get_self_markdown_content())
        return self._token_count

    def get_token_count(self) -> int:
        """获取当前节点的token数量"""
        return self.get_self_token_count()


    def get_markdown(self) -> str:
        """获取当前节点的Markdown文本"""
        script = []
        self_markdown_content = self._get_self_markdown_content()
        if self_markdown_content:
            script.append(self_markdown_content)
        return "\n".join(script)

    def get_parent_title(self) -> list[DocumentContentItem]:
        """获取父节点标题"""
        parent = self.get_parent()
        title_list = []
        while parent is not None:
            title = parent.get_title()
            if title and title not in title_list:
                title_list.append(title)
            parent = parent.get_parent()
        title_list.reverse()
        return title_list
