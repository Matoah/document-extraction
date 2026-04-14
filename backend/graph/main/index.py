from pathlib import Path

from langchain_core.runnables import RunnableConfig

from graph.main.items.standard_specification_config_parser import standard_specification_config_parser
from graph.main.items.standard_specification_name_parser import standard_specification_name_parser
from model.standard_specification_config import StandardSpecificationConfig
from model.standard_specification import StandardSpecification
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from graph.main.state.main_state import MainState


builder = StateGraph(MainState)
builder.add_node(standard_specification_config_parser)
builder.add_node(standard_specification_name_parser)
builder.add_edge(START, "standard_specification_config_parser")
builder.add_edge(START, "standard_specification_name_parser")
builder.add_edge("standard_specification_config_parser", END)
builder.add_edge("standard_specification_name_parser", END)
checkpointer = InMemorySaver()
app = builder.compile(checkpointer=checkpointer)

graph_image_path = Path(__file__).parent / "graph.png"
graph_image_path.write_bytes(app.get_graph().draw_mermaid_png())

def invoke(standard_specification_config: StandardSpecificationConfig):
    """执行标准规范"""
    config: RunnableConfig = {"configurable": {"thread_id": standard_specification_config.code}}
    standard_specification = StandardSpecification.from_config(standard_specification_config)
    state = MainState(standard_specification_config=standard_specification_config, standard_specification=standard_specification)
    return app.invoke(state, config)# type: ignore[assignment]
