from langgraph.runtime import Runtime
from graph.page.state.page_state import PageState
from graph.page.state.page_context import PageContext

def term_parser(state: PageState, runtime: Runtime[PageContext]):
    """术语解析"""
