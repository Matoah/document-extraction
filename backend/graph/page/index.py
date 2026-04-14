from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from pathlib import Path
from model.standard_specification import StandardSpecification

from graph.page.items.notice_parser import notice_parser
from graph.page.items.announcement_parser import announcement_parser
from graph.page.items.foreword_parser import foreword_parser
from graph.page.items.paragraph_parser import paragraph_parser
from graph.page.items.toc_parser import toc_parser
from graph.page.items.paragraph_router import paragraph_router
from graph.page.items.page_content_parser import page_content_parser
from graph.page.state.page_context import PageContext
from graph.page.state.page_state import PageState
from langgraph.types import RetryPolicy
from graph.document.state.document_state import DocumentState

builder = StateGraph(PageState)
builder.add_node(paragraph_parser)
builder.add_node(notice_parser, retry_policy=RetryPolicy(max_attempts=3))
builder.add_node(announcement_parser, retry_policy=RetryPolicy(max_attempts=3))
builder.add_node(foreword_parser, retry_policy=RetryPolicy(max_attempts=3))
builder.add_node(toc_parser, retry_policy=RetryPolicy(max_attempts=3))
builder.add_node(page_content_parser)
builder.add_conditional_edges(START, paragraph_router, {
    "announcement": "announcement_parser",
    "foreword": "foreword_parser",
    "paragraph": "paragraph_parser",
    "notice": "notice_parser",
    "toc": "toc_parser",
})
builder.add_edge(START, "page_content_parser")
builder.add_edge("paragraph_parser", END)
builder.add_edge("notice_parser", END)
builder.add_edge("announcement_parser", END)
builder.add_edge("foreword_parser", END)
builder.add_edge("toc_parser", END)
builder.add_edge("page_content_parser", END)

checkpointer = InMemorySaver()
app = builder.compile(checkpointer=checkpointer)

graph_image_path = Path(__file__).parent / "graph.png"
graph_image_path.write_bytes(app.get_graph().draw_mermaid_png())


def invoke(page_content: list[dict], specification_code: str, document_name: str, page_index: int = 0,
           page_list: list[list[dict]] = None, document_state: DocumentState = None,
           standard_specification: StandardSpecification = None) -> dict:
    """调用页面解析图"""
    config: RunnableConfig = {
        "configurable": {"thread_id": f"{specification_code}_^_{document_name}_^_{page_index}"}
    }
    page_state = PageState(page_index=page_index, page_data=page_content, specification_code=specification_code,
                           document_name=document_name)
    return app.invoke(page_state, config=config, context=PageContext(page_list=page_list, document_state=document_state,
                                                                     standard_specification=standard_specification))
