from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph,START,END
from pathlib import Path

from graph.paragraph.items.image_parser import image_parser
from graph.paragraph.items.aside_text_parser import aside_text_parser
from graph.paragraph.items.code_parser import code_parser
from graph.paragraph.items.equation_parser import equation_parser
from graph.paragraph.items.footer_parser import footer_parser
from graph.paragraph.items.header_parser import header_parser
from graph.paragraph.items.list_parser import list_parser
from graph.paragraph.items.page_footnote_parser import page_footnote_parser
from graph.paragraph.items.page_number_parser import page_number_parser
from graph.paragraph.items.paragraph_router import paragraph_router
from graph.paragraph.items.table_parser import table_parser
from graph.paragraph.items.text_parser import text_parser
from graph.paragraph.state.paragraph_context import ParagraphContext
from graph.paragraph.state.paragraph_state import ParagraphState

workflow = StateGraph(ParagraphState)
workflow.add_node(aside_text_parser)
workflow.add_node(code_parser)
workflow.add_node(equation_parser)
workflow.add_node(footer_parser)
workflow.add_node(header_parser)
workflow.add_node(image_parser)
workflow.add_node(list_parser)
workflow.add_node(page_footnote_parser)
workflow.add_node(page_number_parser)
workflow.add_node(table_parser)
workflow.add_node(text_parser)
workflow.add_conditional_edges(START,paragraph_router,{
    "aside_text":"aside_text_parser",
    "code":"code_parser",
    "text":"text_parser",
    "image":"image_parser",
    "list":"list_parser",
    "page_footnote":"page_footnote_parser",
    "page_number":"page_number_parser",
    "table":"table_parser",
    "equation":"equation_parser",
    "footer":"footer_parser",
    "header":"header_parser",
})
workflow.add_edge("aside_text_parser", END)
workflow.add_edge("code_parser", END)
workflow.add_edge("text_parser", END)
workflow.add_edge("image_parser", END)
workflow.add_edge("list_parser", END)
workflow.add_edge("page_footnote_parser", END)
workflow.add_edge("page_number_parser", END)
workflow.add_edge("table_parser", END)
workflow.add_edge("equation_parser", END)
workflow.add_edge("footer_parser", END)
workflow.add_edge("header_parser", END)
checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)

graph_image_path = Path(__file__).parent / "graph.png"
graph_image_path.write_bytes(app.get_graph().draw_mermaid_png())

def invoke(paragraph: dict, specification_code: str, document_name: str, page_index: int, paragraph_index: int, page_data: list[dict], page_list: list[list[dict]]):
    """执行标准规范"""
    config: RunnableConfig = {"configurable": {"thread_id": f"{specification_code}_^_{document_name}_^_{page_index}_^_{paragraph_index}"}}
    paragraph_state = ParagraphState(paragraph=paragraph)
    return app.invoke(paragraph_state, config, context= ParagraphContext(page_data=page_data, page_index=page_index, page_list=page_list))
