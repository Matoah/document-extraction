from typing import List

from knowledge.model.node import Node


class Chunk:
    """分块"""

    def __init__(self):
        self._node_list = []

    def append_node(self, node: Node):
        """添加节点到分块"""
        self._node_list.append(node)

    def get_node_list(self) -> List[Node]:
        """获取分块中的节点列表"""
        return self._node_list

    def get_token_count(self) -> int:
        """获取分块中的Token数量"""
        return sum([node.get_token_count() for node in self._node_list])

    def get_level(self) -> int:
        """获取分块的等级，从节点列表中倒序查找"""
        if self._node_list:
            for node in self._node_list[::-1]:
                if node.get_node_level() > 0:
                    return node.get_node_level()
        return 0

    def get_markdown(self) -> str:
        """获取分块中的Markdown文本"""
        if self._node_list:
            first_node = self._node_list[0]
            script = []
            parent_title = first_node.get_parent_title()
            content_items = []
            for node in self._node_list:
                content_items.extend(node.get_content())
            # 检查标题是否在内容，如果在，则剔除。解决标题重复问题
            parent_title = [title for title in parent_title if title not in content_items]
            if parent_title:
                script.extend([title.to_md_script() for title in parent_title])
            # 开始尝试合并内容
            # 1、尝试合并内容项
            pre_content_item = content_items[0]
            merged_content_list = [pre_content_item]
            for content in content_items[1:]:
                if type(pre_content_item) == type(content):
                    if pre_content_item.merge(content):
                        continue
                    else:
                        merged_content_list.append(content)
                        pre_content_item = content
            # 2、将合并后的内容项转换为Markdown脚本
            for content in merged_content_list:
                script.append(content.to_md_script())
            return "\n".join(script)
        return ""
