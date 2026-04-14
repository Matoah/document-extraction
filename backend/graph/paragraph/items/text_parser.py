from graph.paragraph.state.paragraph_context import ParagraphContext
from graph.paragraph.state.paragraph_state import ParagraphState
from model.text import Text
from langgraph.runtime import Runtime

from utils.document_util import get_doc_page_index


def text_parser(state: ParagraphState, runtime: Runtime[ParagraphContext]):
    """文本解析"""
    context = runtime.context
    page_index = context.page_index
    paragraph = state.paragraph
    text = paragraph.get("text", "")
    text_level = paragraph.get("text_level", 0)
    doc_page_index = get_doc_page_index(page_index, 1, context.page_list)
    return {
        "result": Text(
            page_index=page_index,
            doc_page_index=doc_page_index[0] if doc_page_index else -1,
            text_level=text_level,
            content=text
        )
    }


if __name__ == "__main__":
    print(text_parser(ParagraphState(paragraph={
        "type": "text",
        "text": "A.0.1 车路协同拓展应用适用的服务场景可根据应用需求定制扩展，本规范典型示例场景类型及代码应符合表A.0.1的规定，以作为工程应用参考。",
        "bbox": [
            110,
            258,
            885,
            297
        ],
        "page_idx": 26
    })))
