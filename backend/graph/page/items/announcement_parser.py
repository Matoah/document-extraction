from graph.page.state.page_state import PageState
from model.organization import Organization
from role.announcument import Announcement, AnnouncementResult
from langgraph.runtime import Runtime
from graph.page.state.page_context import PageContext
from utils.document_util import get_doc_page_index
from utils.paragraph_util import get_content
from utils.mineru_util import enhance
from model.announcement import Announcement as AnnouncementModel
from cache.cache import exist_announcement_cache, cache_announcement, get_announcement
import logging

logger = logging.getLogger(__name__)


def _get_announcement_page_count(page_index: int, page_list: list[list[dict]]) -> int:
    """获取公告页数"""
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


def _get_content(page_index: int, page_count: int, page_list: list[list[dict]]) -> str:
    """获取公告内容"""
    page_content = []
    for delta in range(0, page_count):
        page = page_list[page_index + delta]
        page_content.append(get_content(page, include_header=True, include_footer=True))
    return "\n".join(page_content)

def _to_organization(organization_str: str) -> Organization:
    return Organization(name=organization_str)


def announcement_parser(state: PageState, runtime: Runtime[PageContext]):
    """公告解析"""
    page_list = runtime.context.page_list
    page_index = state.page_index
    page_count = _get_announcement_page_count(page_index, page_list)
    announcement_content = _get_content(page_index, page_count, page_list)
    announcement_content = enhance(announcement_content)
    # 检查是否存在缓存
    document_name = runtime.context.document_state.origin_document.name
    if exist_announcement_cache(state.specification_code, document_name, announcement_content):
        cache_data = get_announcement(state.specification_code, document_name, announcement_content)
        response = AnnouncementResult(**cache_data)
    else:
        logger.info(f"正在调用大模型解析公告，请稍候...")
        announcement = Announcement()
        response: AnnouncementResult = announcement.ask(announcement_content)
        cache_announcement(state.specification_code, document_name, announcement_content, response.model_dump())
    runtime.context.document_state.document.content_list.append(AnnouncementModel(
        page_index=[page_index+delta for delta in range(0, page_count)],
        doc_page_index=get_doc_page_index(page_index, page_count, page_list),
        title=response.title,
        subject = response.subject,
        code= response.code,
        content = response.content,
        release_org = _to_organization(response.release_org),
        release_date = response.release_date,
        issue_org = _to_organization(response.issue_org),
        issue_date = response.issue_date,
    ))
    return {
        "page_step": page_count
    }
