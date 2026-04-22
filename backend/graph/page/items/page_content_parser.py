from graph.page.state.page_state import PageState
from langgraph.runtime import Runtime
from graph.page.state.page_context import PageContext
from utils.paragraph_util import to_text
import re
from utils.date_util import resolve_date

release_date_patterns = [
    r"(\d{4}-\d+-\d+)\s*发布",
    r"发布日期[:：]\s*(\d+\s*年\s*\d+\s*月\s*\d+\s*日)"
]

effective_date_patterns = [
    r"实施日期[:：]\s*(\d+\s*年\s*\d+\s*月\s*\d+\s*日)",
    r"实行日期[:：]\s*(\d+\s*年\s*\d+\s*月\s*\d+\s*日)"
    r"(\d{4}-\d+-\d+)\s*实施",
]

approved_date_patterns = [
    r"批准部门[:：]\s*(\S+)"
]

def _get_content(page_index: int, page_count: int, page_list: list[list[dict]]) -> str:
    """获取前言内容"""
    page_content = []
    for delta in range(0, page_count):
        page = page_list[page_index + delta]
        page_content.append(to_text(page))
    return "\n".join(page_content)

def _has_release_date(page_content: str) -> bool:
    """检查是否包含发布日期, 格式为：yyyy-MM-dd 发布"""
    for pattern in release_date_patterns:
        if re.search(pattern, page_content) is not None:
            return True
    return False

def _get_release_date(page_content: str) -> str:
    """获取发布日期, 格式为：yyyy-MM-dd 发布"""
    for pattern in release_date_patterns:
        match = re.search(pattern, page_content)
        if match:
            return resolve_date(match.group(1))
    return ""

def _has_effective_date(page_content: str) -> bool:
    """检查是否包含实施日期, 格式为：yyyy-MM-dd 实施"""
    for pattern in effective_date_patterns:
        if re.search(pattern, page_content) is not None:
            return True
    return False

def _get_effective_date(page_content: str) -> str:
    """获取实施日期, 格式为：yyyy-MM-dd 实施"""
    for pattern in effective_date_patterns:
        match = re.search(pattern, page_content)
        if match:
            return resolve_date(match.group(1))
    return ""

def _has_approved_by(page_content: str) -> bool:
    """检查是否包含批准部门"""
    for pattern in approved_date_patterns:
        if re.search(pattern, page_content) is not None:
            return True
    return False

def _get_approved_by(page_content: str) -> str:
    """获取批准部门"""
    for pattern in approved_date_patterns:
        match = re.search(pattern, page_content)
        if match:
            return match.group(1)
    return ""

def page_content_parser(state: PageState, runtime: Runtime[PageContext]):
    """页面内容解析器, 从页面内容中提取发布、实施日期"""
    page_list = runtime.context.page_list
    page_index = state.page_index
    page_content = _get_content(page_index, 1, page_list)
    if not runtime.context.document_state.document.release_date and _has_release_date(page_content):
        runtime.context.document_state.document.release_date = _get_release_date(page_content)
    if not runtime.context.document_state.document.effective_date and _has_effective_date(page_content):
        runtime.context.document_state.document.effective_date = _get_effective_date(page_content)
    if not runtime.context.document_state.document.approved_by and _has_approved_by(page_content):
        runtime.context.document_state.document.approved_by = _get_approved_by(page_content)
    return {}


if __name__ == "__main__":
    print(_has_effective_date("实施日期：2015年01月01日"))
    print(_get_effective_date("实施日期：2015年01月01日"))
