from factory.document_content_factory import create
from graph.page.state.page_state import PageState
from graph.paragraph.index import invoke
from langgraph.runtime import Runtime
from graph.page.state.page_context import PageContext
from type.document_content_item import DocumentContentItem


def paragraph_parser(state: PageState, runtime: Runtime[PageContext]):
    """段落解析"""
    page_data = state.page_data
    page_list = runtime.context.page_list
    for paragraph_index, paragraph_data in enumerate(page_data):
        paragraph_state = invoke(paragraph=paragraph_data, specification_code=state.specification_code,
                                 document_name=state.document_name, page_index=state.page_index,
                                 paragraph_index=paragraph_index, page_data=page_data, page_list=page_list)
        result = paragraph_state.get("result")
        if isinstance(result, DocumentContentItem):
            runtime.context.document_state.document.content_list.append(result)
        elif result is not None:
            raise ValueError(f"未知类型: {type(result)}")
    return {
        "page_step": 1,
    }
