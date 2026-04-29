from model.origin_document import OriginDocument
from graph.document.state.document_state import DocumentState
from model.document import Document
import logging
from model.standard_specification import StandardSpecification
from langgraph.graph import StateGraph, START, END
from graph.document.items.document_name_parser import document_name_parser
from graph.document.items.document_parser import document_paser
from graph.document.items.toc_parser import toc_parser
from graph.document.items.term_parser import term_parser
from graph.document.items.symbol_parser import symbol_parser
from langgraph.checkpoint.memory import InMemorySaver
from pathlib import Path
from langchain_core.runnables import RunnableConfig
from model.text import Text
from utils.text_util import is_chinese

logger = logging.getLogger(__file__)

builder = StateGraph(DocumentState)
builder.add_node(document_name_parser)
builder.add_node(document_paser)
builder.add_node(toc_parser)
builder.add_node(term_parser)
builder.add_node(symbol_parser)

builder.add_edge(START, "document_name_parser")
builder.add_edge("document_name_parser", "document_paser")
builder.add_edge("document_paser", "toc_parser")
builder.add_edge("toc_parser", "term_parser")
builder.add_edge("toc_parser", "symbol_parser")
builder.add_edge("symbol_parser", END)
builder.add_edge("term_parser", END)

checkpointer = InMemorySaver()
app = builder.compile(checkpointer=checkpointer)

graph_image_path = Path(__file__).parent / "graph.png"
graph_image_path.write_bytes(app.get_graph().draw_mermaid_png())

def _enhance_document_content(document_state: DocumentState):
    """
    增强处理文档内容
    1、解决分页后导致文本截断问题
    """
    content_list = document_state.document.content_list
    pre_content = None
    new_content_list = []
    for content in content_list:
        if isinstance(content, Text) and isinstance(pre_content, Text) and pre_content.text_level == content.text_level:
            if pre_content.content and content.content:
                pre_content_tail_char = pre_content.content[-1]
                content_head_char = content.content[0]
                if is_chinese(pre_content_tail_char) and is_chinese(content_head_char):
                    #尾首都是中文，合并
                    pre_content += content.content
                    continue
        new_content_list.append(content)
        pre_content = content
    document_state.document.content_list = new_content_list


def invoke(specification_code: str, document_name: str, origin_document: OriginDocument,
           standard_specification: StandardSpecification) -> dict:
    """调用文档解析图"""
    document = Document.from_original_document(origin_document)
    config: RunnableConfig = {"configurable": {"thread_id": f"{specification_code}_^_{document_name}"}}
    document_state: DocumentState = DocumentState(
        spec_code=specification_code, standard_specification=standard_specification, origin_document=origin_document,
        document=document)
    _enhance_document_content(document_state)
    return app.invoke(document_state, config)  # type: ignore[assignment]
