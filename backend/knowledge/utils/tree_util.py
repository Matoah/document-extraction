from knowledge.model.node import Node
from model.text import Text
from type.document_content_item import DocumentContentItem
from knowledge.utils.content_item_util import is_top_level_item


def build_node(content: list[DocumentContentItem], index: int, node: Node, node_list: list[Node]) -> int:
    """构建节点"""
    while index < len(content):
        content_item = content[index]
        if is_top_level_item(content_item):
            return index
        elif isinstance(content_item, Text):
            text_level = content_item.text_level
            if text_level > 0:
                # 标题节点
                if text_level <= node.get_node_level():
                    return index
                elif text_level > node.get_node_level():
                    # 当前节点的比父节点层级低，为子节点
                    child_node = Node()
                    child_node.set_node_level(text_level)
                    child_node.append_content(content_item)
                    child_node.set_title(content_item)
                    # node.append_child(child_node)
                    child_node.set_parent(node)
                    node_list.append(child_node)
                    if index + 1 < len(content):
                        index = build_node(content, index + 1, child_node, node_list)
                        continue
            else:
                node.append_content(content_item)
        else:
            node.append_content(content_item)
        index += 1
    return index

def build_tree(content: list[DocumentContentItem]) -> list[Node]:
    """构建树结构"""
    pass


def build_parent_relation(content: list[DocumentContentItem]) -> list[Node]:
    """构建父子关系，返回平级节点列表"""
    node_list: list[Node] = []
    index = 0
    current_node: Node | None = None
    while index < len(content):
        content_item = content[index]
        if isinstance(content_item, Text):
            if content_item.text_level > 0:
                # 是标题
                node = Node()
                node.set_node_level(content_item.text_level)
                node.append_content(content_item)
                node.set_title(content_item)
                node_list.append(node)
                if index + 1 < len(content):
                    index = build_node(content, index + 1, node, node_list)
                    continue
            else:
                if current_node is None:
                    current_node = Node()
                    node_list.append(current_node)
                current_node.append_content(content_item)
        elif is_top_level_item(content_item):
            node = Node()
            node.set_content([content_item])
            node.set_node_level(1) # 顶级节点层级为1
            node_list.append(node)
        else:
            if current_node is None:
                current_node = Node()
                node_list.append(current_node)
            current_node.append_content(content_item)
        index += 1
    return node_list
