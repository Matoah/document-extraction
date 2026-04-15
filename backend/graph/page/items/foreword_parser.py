from graph.page.state.page_context import PageContext
from graph.page.state.page_state import PageState
from model.organization import Organization
from model.person import Person
from utils.document_util import get_doc_page_index, merge_doc_organization_list, merge_doc_person_list
from utils.paragraph_util import to_text
from utils.mineru_util import enhance
from langgraph.runtime import Runtime
from role.foreword import Foreword, ForewordInfo
from model.foreword import Foreword as ForewordModel
from cache.cache import cache_foreword, get_foreword, exist_foreword_cache
import logging

logger = logging.getLogger(__name__)


def _get_foreword_page_count(page_index: int, page_list: list[list[dict]]) -> int:
    """获取前言页数"""
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
    """获取前言内容"""
    page_content = []
    for delta in range(0, page_count):
        page = page_list[page_index + delta]
        page_content.append(to_text(page))
    return "\n".join(page_content)

def _to_person(person_name: str) -> Person | None:
    """将人员名称转换为人员对象"""
    if person_name and person_name.strip() != "":
        return Person(name=person_name)
    return None

def _to_person_list(person_names: str) -> list[Person]:
    """将人员名称转换为人员对象列表"""
    person_list = []
    if person_names and person_names.strip() != "":
        person_names = person_names.strip()
        for person_name in person_names.split(","):
            person = _to_person(person_name)
            if person is not None:
                person_list.append(person)
    return person_list

def _to_organization(organization_name: str) -> Organization | None:
    if organization_name and organization_name.strip() != "":
        return Organization(name=organization_name)
    return None

def _to_organization_list(organization_names: str) -> list[Organization]:
    """将单位名称转换为单位对象列表"""
    organization_list = []
    if organization_names and organization_names.strip() != "":
        organization_names = organization_names.strip()
        for organization_name in organization_names.split(","):
            organization = _to_organization(organization_name)
            if organization is not None:
                organization_list.append(organization)
    return organization_list

def foreword_parser(state: PageState, runtime: Runtime[PageContext]):
    """前言解析"""
    page_list = runtime.context.page_list
    page_index = state.page_index
    page_count = _get_foreword_page_count(page_index, page_list)
    foreword_content = _get_content(page_index, page_count, page_list)
    foreword_content = enhance(foreword_content)
    document_name = runtime.context.document_state.origin_document.name
    # 检查是否存在缓存
    if exist_foreword_cache(state.specification_code, document_name, foreword_content):
        cache_data = get_foreword(state.specification_code, document_name, foreword_content)
        response = ForewordInfo(**cache_data)
    else:
        logger.info(f"正在调用大模型解析前言，请稍候...")
        foreword = Foreword()
        response: ForewordInfo = foreword.ask(foreword_content)
        cache_foreword(state.specification_code, document_name, foreword_content, response.model_dump())
    doc_page_index = get_doc_page_index(page_index, page_count, runtime.context.page_list)
    contract_person = _to_person(response.contact_person)
    contact_address = response.contact_address
    postal_code = response.postal_code
    phone = response.phone
    fax = response.fax
    email = response.email
    contact_organization = _to_organization(response.contact_organization)
    if contact_organization:
        contact_organization.address = contact_address
        contact_organization.postal_code = postal_code
        contact_organization.phone = phone
        contact_organization.fax = fax
        contact_organization.email = email
    chief_editor_organization = _to_organization_list(response.chief_editor_organization)
    participating_organization = _to_organization_list(response.participating_organizations)
    chief_reviewer = _to_person_list(response.chief_reviewer)
    review_participants = _to_person_list(response.review_participants)
    chief_editor = _to_person_list(response.chief_editor)
    main_contributors = _to_person_list(response.main_contributors)
    contributors = _to_person_list(response.contributors)
    document = runtime.context.document_state.document
    # 合并联系人
    merge_doc_person_list([contract_person], document.contact_person)
    merge_doc_person_list(contributors, document.contributors)
    merge_doc_person_list(chief_editor, document.chief_editor)
    merge_doc_person_list(main_contributors, document.main_contributors)
    merge_doc_person_list(chief_reviewer, document.chief_reviewer)
    merge_doc_person_list(review_participants, document.reviewing_participant)
    merge_doc_organization_list(participating_organization, document.participating_organization)
    merge_doc_organization_list(chief_editor_organization, document.chief_editor_organization)
    merge_doc_organization_list(participating_organization, document.participating_organization)
    merge_doc_organization_list([contact_organization], document.contact_organization)

    runtime.context.document_state.document.content_list.append(ForewordModel(
        content = foreword_content,
        contact_person= contract_person,
        contact_address= contact_address,
        contact_organization= contact_organization,
        postal_code= postal_code,
        phone= phone,
        fax= fax,
        email= email,
        chief_editor_organization= chief_editor_organization,
        participating_organization= participating_organization,
        chief_reviewer= chief_reviewer,
        review_participants= review_participants,
        chief_editor= chief_editor,
        main_contributors= main_contributors,
        contributors= contributors,
        page_index=[page_index + delta for delta in range(0, page_count)],
        doc_page_index=doc_page_index
    ))
    return {
        "page_step": page_count
    }
