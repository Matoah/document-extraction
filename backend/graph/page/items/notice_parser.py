from graph.page.state.page_context import PageContext
from graph.page.state.page_state import PageState
from langgraph.runtime import Runtime

from model.organization import Organization
from role.notice import Notice, NoticeInfo
from utils.document_util import get_doc_page_index
from utils.paragraph_util import to_text
from model.notice import Notice as NoticeModel
from cache.cache import cache_notice, get_notice, exist_notice_cache
import logging

logger = logging.getLogger(__name__)


def _get_notice_page_count(page_index: int, page_list: list[list[dict]]) -> int:
    """获取通知页数"""
    page_count = 1
    for index in range(page_index + 1, len(page_list)):
        page = page_list[index]
        has_top_level_text = False
        for paragraph in page:
            if paragraph.get("type") == "text" and paragraph.get("text_level") == 1:
                has_top_level_text = True
                break
        if has_top_level_text:
            break
        else:
            page_count += 1
    return page_count


def _to_organization(organization_name: str) -> Organization | None:
    if organization_name and organization_name.strip() != "":
        return Organization(name=organization_name)
    return None


def _get_content(page_index: int, page_count: int, page_list: list[list[dict]]) -> str:
    """获取通知内容"""
    page_content = []
    for delta in range(0, page_count):
        page = page_list[page_index + delta]
        page_content.append(to_text(page))
    return "\n".join(page_content)


def notice_parser(state: PageState, runtime: Runtime[PageContext]):
    """通知解析"""
    page_list = runtime.context.page_list
    page_index = state.page_index
    page_count = _get_notice_page_count(page_index, page_list)
    notice_content = _get_content(page_index, page_count, page_list)
    document_name = runtime.context.document_state.origin_document.name
    # 检查是否存在缓存
    if exist_notice_cache(state.specification_code, document_name, notice_content):
        cache_data = get_notice(state.specification_code, document_name, notice_content)
        response = NoticeInfo(**cache_data)
    else:
        logger.info(f"正在调用大模型解析通知，请稍候...")
        notice = Notice()
        response: NoticeInfo = notice.ask(notice_content)
        cache_notice(state.specification_code, document_name, notice_content, response.model_dump())
    doc_page_index = get_doc_page_index(page_index, page_count, runtime.context.page_list)
    return {
        "page_step": page_count,
        "result": [NoticeModel(
            page_index=[page_index + delta for delta in range(0, page_count)],
            doc_page_index=doc_page_index,
            title=response.title,
            code=response.code,
            content=response.content,
            release_org=_to_organization(response.release_org),
            release_date=response.release_date,
        )],
    }
