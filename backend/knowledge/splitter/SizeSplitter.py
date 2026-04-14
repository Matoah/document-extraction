from knowledge.splitter.base import Splitter
from type.document_content_item import DocumentContentItem
from knowledge.utils.tree_util import build_parent_relation
from knowledge.model.chunk import Chunk
from knowledge.model.node import Node
from model.table import Table
from knowledge.utils.content_item_util import is_atomic__item
import logging
from knowledge.utils.token_util import count_tokens
from knowledge.utils.html_util import split_table_by_token_count

logger = logging.getLogger(__name__)

PARAGRAPH_SPLIT_CHAR_LIST = ['\n', '。', '.', '；',';','!']  # 段落切分字符列表

class SizeSplitter(Splitter):
    """基于大小的切分器"""

    def __init__(
            self,
            content: list[DocumentContentItem],
            min_token_count: int,
            token_count: int,
            max_token_count: int
    ):
        super().__init__(content, min_token_count, token_count, max_token_count)
        self.chunks: list[Chunk] = []

    def _split_str_content(self, current_chunk: Chunk, current_node: Node, content_item: DocumentContentItem,
                           content: str, depth: int = 0) -> Chunk:
        """对字符串内容进行拆分，确保每个段落不超过最大Token大小"""
        if depth >= len(PARAGRAPH_SPLIT_CHAR_LIST):
            logger.warning("最大深度超过段落切分字符列表长度，请添加段落切分字符！")
            logger.warning(content)
            # 无法分割，直接添加到当前分块
            new_node = Node()
            new_node.append_content(content_item.from_new_content([content]))
            new_node.set_parent(current_node.get_parent())
            current_chunk.append_node(new_node)
            self.chunks.append(current_chunk)
            return Chunk()
        spliter = PARAGRAPH_SPLIT_CHAR_LIST[depth]
        str_content_list = []
        # 按切分字符切分，并在每个元素后添加切分字符，确保内容与原始内容一致
        split_content_list = content.split(spliter)
        for i, item in enumerate(split_content_list):
            if i+1 < len(split_content_list):
                str_content_list.append(item+spliter)
            else:
                # 最后一个不需要拼接切分字符
                str_content_list.append(item)
        content_chunk_list: list[str] = []
        content_chunk_list_token_count = 0
        for str_item in str_content_list:
            token_size = count_tokens(str_item)
            current_token_count = current_chunk.get_token_count() + content_chunk_list_token_count + token_size
            if current_token_count > self.max_token_count:
                # 超出大小，继续拆分
                if content_chunk_list:
                    new_node = Node()
                    new_node.append_content(content_item.from_new_content(content_chunk_list))
                    new_node.set_parent(current_node.get_parent())
                    current_chunk.append_node(new_node)
                    content_chunk_list = []
                    content_chunk_list_token_count = 0
                current_chunk = self._split_str_content(current_chunk, current_node, content_item, str_item, depth + 1)
            elif self.max_token_count >= current_token_count >= self.token_count:
                # 大小合适，直接添加
                content_chunk_list.append(str_item)
                new_node = Node()
                new_node.append_content(content_item.from_new_content(content_chunk_list))
                new_node.set_parent(current_node.get_parent())
                current_chunk.append_node(new_node)
                self.chunks.append(current_chunk)
                current_chunk = Chunk()
                content_chunk_list = []
                content_chunk_list_token_count = 0
            else:
                # 太小，继续添加
                content_chunk_list.append(str_item)
                content_chunk_list_token_count += token_size

        if content_chunk_list:
            new_node = Node()
            new_node.append_content(content_item.from_new_content(content_chunk_list))
            new_node.set_parent(current_node.get_parent())
            current_chunk.append_node(new_node)
        return current_chunk

    def _split_table_content(self, current_chunk: Chunk, current_node: Node, content_item: Table) -> Chunk:
        """对表格内容进行拆分"""
        table_html_script = content_item.table_body
        split_item_content = split_table_by_token_count(table_html_script, current_chunk.get_token_count(), self.token_count, self.max_token_count)
        for table_content in split_item_content:
            new_node = Node()
            new_node.append_content(content_item.from_new_content([table_content]))
            new_node.set_parent(current_node)
            current_chunk.append_node(new_node)
            self.chunks.append(current_chunk) # 添加当前分块到结果列表
            current_chunk = Chunk()
        return current_chunk

    def _split_oversized_node(self, current_chunk: Chunk, node: Node) -> Chunk:
        """分割超大分块，在段落边界进行分割，同时保持特殊内容完整性, 并返回新的分块"""

        content_list = node.get_content()
        for content_item in content_list:
            # 从当前节点中拆分出内容项遍历，逐个判断添加
            new_node = Node()
            new_node.append_content(content_item)
            new_node.set_parent(node)
            current_node_token_size = new_node.get_token_count()
            current_token_count = current_chunk.get_token_count() + current_node_token_size
            if current_token_count > self.max_token_count:
                # 超出最大Token大小，需要对当前节点进行拆分
                if isinstance(content_item, Table):
                    # 表格节点需要额外处理
                    current_chunk = self._split_table_content(current_chunk, node, content_item)
                elif is_atomic__item(content_item) and current_token_count > self.min_token_count:
                    # 原子项，直接添加到当前分块
                    self.chunks.append(current_chunk) # 添加当前分块到结果列表
                    current_chunk = Chunk()
                    current_chunk.append_node(new_node)
                else:
                    # 其他类型按照字符串内容进行分块
                    content_item_content = content_item.to_md_script()
                    current_chunk = self._split_str_content(current_chunk, node, content_item, content_item_content)

            elif self.max_token_count > current_token_count > self.token_count:
                # 大小合适，直接添加到当前分块
                current_chunk.append_node(new_node)
                self.chunks.append(current_chunk) # 添加当前分块到结果列表
                current_chunk = Chunk()

            elif current_token_count < self.token_count:
                # 小于目标Token大小，直接添加到当前分块
                current_chunk.append_node(new_node)

        return current_chunk

    def _split_content_node_list(self, node_list: list[Node]):
        """按照Token大小，分割内容节点列表"""
        i = 0
        chunk = Chunk()
        while i < len(node_list):
            node = node_list[i]
            node_token_count = node.get_token_count()
            chunk_token_count = chunk.get_token_count()
            current_token_count = chunk_token_count + node_token_count
            if current_token_count > self.max_token_count:
                # 超出大小，需要拆分当前分块
                if chunk_token_count > self.min_token_count:
                    # 当前分片已经达到最小，判断下一个节点是否为当前节点的子节点，如果是则继续添加，否则创建新的分块
                    if node.get_node_level() >= chunk.get_level():
                        # 非当前节点的子节点，重新分块
                        self.chunks.append(chunk)
                        chunk = Chunk()
                chunk = self._split_oversized_node(chunk, node)

            elif self.max_token_count >= current_token_count >= self.token_count:
                # 大小达到合适，开始搜集分块并创建新的分块
                chunk.append_node(node)
                self.chunks.append(chunk)
                chunk = Chunk()

            elif current_token_count < self.token_count:
                # 还未到达预期大小，继续添加节点
                chunk.append_node(node)
            else:
                raise ValueError(f"未识别异常场景！")
            i += 1
        if chunk.get_node_list():
            self.chunks.append(chunk)

    def _split(self) -> list[str]:
        """内部切分文档"""
        # 实现基于大小的切分逻辑
        node_list = build_parent_relation(self.content)
        self._split_content_node_list(node_list)
        chunk_script_list = []
        for chunk in self.chunks:
            chunk_script_list.append(chunk.get_markdown())
        return chunk_script_list
