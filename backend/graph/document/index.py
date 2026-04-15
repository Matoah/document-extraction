from model.origin_document import OriginDocument
from graph.document.state.document_state import DocumentState
from model.document import Document
import logging
from model.standard_specification import StandardSpecification
from langgraph.graph import StateGraph, START, END
from graph.document.items.document_parser import document_paser
from graph.document.items.toc_parser import toc_parser
from graph.document.items.term_parser import term_parser
from graph.document.items.symbol_parser import symbol_parser
from langgraph.checkpoint.memory import InMemorySaver
from pathlib import Path
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__file__)

builder = StateGraph(DocumentState)
builder.add_node(document_paser)
builder.add_node(toc_parser)
builder.add_node(term_parser)
builder.add_node(symbol_parser)

builder.add_edge(START, "document_paser")
builder.add_edge("document_paser", "toc_parser")
builder.add_edge("toc_parser", "term_parser")
builder.add_edge("toc_parser", "symbol_parser")
builder.add_edge("symbol_parser", END)
builder.add_edge("term_parser", END)

checkpointer = InMemorySaver()
app = builder.compile(checkpointer=checkpointer)

graph_image_path = Path(__file__).parent / "graph.png"
graph_image_path.write_bytes(app.get_graph().draw_mermaid_png())


def invoke(specification_code: str, document_name: str, origin_document: OriginDocument,
           standard_specification: StandardSpecification) -> dict:
    """调用文档解析图"""
    document = Document.from_original_document(origin_document)
    config: RunnableConfig = {"configurable": {"thread_id": f"{specification_code}_^_{document_name}"}}
    document_state: DocumentState = DocumentState(
        spec_code=specification_code, standard_specification=standard_specification, origin_document=origin_document,
        document=document)
    return app.invoke(document_state, config)  # type: ignore[assignment]
