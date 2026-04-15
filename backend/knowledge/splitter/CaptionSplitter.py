from knowledge.splitter.base import Splitter
from type.document_content_item import DocumentContentItem
from knowledge.model.chunk import Chunk, Node
import logging
from knowledge.utils.tree_util import build_parent_relation

logger = logging.getLogger(__name__)

class CaptionSplitter(Splitter):
    """标题切分器"""

    def __init__(
            self,
            doc_name: str,
            content: list[DocumentContentItem],
            min_token_count: int,
            token_count: int,
            max_token_count: int
    ):
        super().__init__(doc_name, content, min_token_count, token_count, max_token_count)
        self.chunks: list[Chunk] = []

    def _split_content_node_list(self, node_list: list[Node]):
        """根据节点列表切分文档"""


    def _split(self) -> list[str]:
        """内部切分文档"""
        node_list = build_parent_relation(self.content)
        self._split_content_node_list(node_list)
        chunk_script_list = []
        for chunk in self.chunks:
            chunk_script_list.append(chunk.get_markdown())
        return chunk_script_list
