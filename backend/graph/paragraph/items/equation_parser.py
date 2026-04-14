from graph.paragraph.state.paragraph_context import ParagraphContext
from graph.paragraph.state.paragraph_state import ParagraphState
import re
from langgraph.runtime import Runtime
from model.equation import Equation
from utils.document_util import get_doc_page_index

TAG_PATTERN = r"\\tag\s*{([^}]+)}"


def equation_parser(state: ParagraphState, runtime: Runtime[ParagraphContext]):
    """公式解析"""
    paragraph = state.paragraph
    context = runtime.context
    page_index = context.page_index
    equation = paragraph.get("text", "").strip()
    _format = paragraph.get("text_format", "latex")
    if equation:
        """
        使用正则从equation中提取tag标签
        """
        tag = ""
        match = re.search(TAG_PATTERN, equation)
        if match:
            tag = match.group(1)
        doc_page_index = get_doc_page_index(page_index, 1, context.page_list)
        return {
            "result": Equation(
                page_index=page_index,
                doc_page_index=doc_page_index[0] if doc_page_index else -1,
                tag=tag,
                format=_format,
                content=equation
            )
        }
    return {}


if __name__ == '__main__':
    print(equation_parser(ParagraphState(paragraph={
        "type": "equation",
        "bbox": [
            0.4,
            0.512,
            0.884,
            0.531
        ],
        "angle": 0,
        "text": "\\[\n\\Delta f = \\left| f _ {\\mathrm {T x}} - f _ {\\mathrm {T x a}} \\right| / f _ {\\mathrm {T x}} \\times 1 0 ^ {6} \\tag {L.3.5-1}\n\\]"
    })))
