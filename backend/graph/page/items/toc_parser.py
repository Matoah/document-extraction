from graph.page.state.page_state import PageState
from graph.page.state.page_context import PageContext
from langgraph.runtime import Runtime
from utils.paragraph_util import to_text
from cache.cache import cache_toc, exist_toc_cache, get_toc
from role.toc import TOCInfo, TOC
from utils.document_util import get_doc_page_index
from model.toc import TOC as TOCModel
import logging
import re

logger = logging.getLogger(__name__)

def _get_toc(toc_item: str) -> str:
    """获取目录项"""
    match = re.search(r"(\d*\s*\w+)\s*\d*", toc_item)
    if match:
        return match.group(1)
    return ""

def _get_first_toc(page_index: int, page_list: list[list[dict]]) -> str:
    """获取第一个目录"""
    page_data = page_list[page_index]
    for paragraph in page_data:
        type = paragraph.get("type", "text")
        if type == "text":
            text = paragraph.get("text", "").strip()
            if text.replace(" ", "") not in ["目次", "目录"]:
                return _get_toc(text)
        elif type == "list":
            items = paragraph.get("list_items",[])
            if items:
                return _get_toc(items[0])
    return ""


def _get_toc_page_count(page_index: int, page_list: list[list[dict]]) -> int:
    """
    获取目录页数，判断逻辑：获取第一个目录，然后从后面内容中查询，如果查询到，则中间页为目录页
    """
    first_toc = _get_first_toc(page_index, page_list)
    if not first_toc:
        raise ValueError("获取第一个目录失败！")
    first_toc = first_toc.replace(" ","")
    # 目录页都是一整页，因此直接从下一页开始查询
    for index in range(page_index + 1, len(page_list)):
        page = page_list[index]
        for paragraph in page:
            if paragraph.get("type") == "text":
                # 目录都是文本类型
                text = paragraph.get("text", "").strip().replace(" ", "")
                if text.startswith(first_toc):
                    return index - page_index
    return 1

def _get_content(page_index: int, page_count: int, page_list: list[list[dict]]) -> str:
    """获取目录内容"""
    page_content = []
    for delta in range(0, page_count):
        page = page_list[page_index + delta]
        page_content.append(to_text(page))
    return "\n".join(page_content)

def _enhance_toc_items(items: list[dict])-> list[dict]:
    """遍历目录项，给目录设置id值及parent_id值等信息，同时递归处理子项。深度优先遍历"""
    id_index = 0
    def iterate(children: list[dict], parent_id: int) -> list[dict]:
        nonlocal id_index
        for item in children:
            item["id"] = id_index
            item["parent_id"] = parent_id
            id_index += 1
            if item.get("children"):
                iterate(item["children"], item["id"])
        return children
    return iterate(items, -1)

def toc_parser(state: PageState, runtime: Runtime[PageContext]):
    """解析文档目录"""
    page_list = runtime.context.page_list
    page_index = state.page_index
    page_count = _get_toc_page_count(page_index, page_list)
    toc_content = _get_content(page_index, page_count, page_list)
    document_name = runtime.context.document_state.origin_document.name
    # 检查是否存在缓存
    if exist_toc_cache(state.specification_code, document_name, toc_content):
        cache_data = get_toc(state.specification_code, document_name, toc_content)
        response = TOCInfo(**cache_data)
    else:
        logger.info(f"正在调用大模型解析目录，请稍候...")
        toc = TOC()
        response: TOCInfo = toc.ask(toc_content)
        cache_toc(state.specification_code, document_name, toc_content, response.model_dump())
    doc_page_index = get_doc_page_index(page_index, page_count, runtime.context.page_list)
    data = {
        "page_index": [page_index + delta for delta in range(0, page_count)],
        "doc_page_index": doc_page_index,
        "title": response.title,
        "items": _enhance_toc_items([item.model_dump() for item in response.items])
    }
    runtime.context.document_state.document.content_list.append(TOCModel(**data))
    return {
        "page_step": page_count
    }
