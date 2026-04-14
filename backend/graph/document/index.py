from model.origin_document import OriginDocument
from graph.document.state.document_state import DocumentState
from graph.page.index import invoke as page_invoke
from model.document import Document
import logging
from model.standard_specification import StandardSpecification

logger = logging.getLogger(__file__)

def get_toc(document: Document):
    """获取目录"""
    for content in document.content_list:
        if content.type == "toc":
            return content
    return None

def enhance_toc_item_title(prefix: str, title: str):
    """增强目录项标题"""
    title = title.replace(" ", "")
    return title if prefix == "" else prefix + "_^_" + title


def iter_toc_item(toc_item_list, prefix="", level=1):
    result_map = {}
    for toc_item in toc_item_list or []:
        key = enhance_toc_item_title(prefix, toc_item.title)
        result_map[key] = level
        result_map.update(iter_toc_item(toc_item.children, key, level+1))
    return result_map

def get_text_level(key: str, toc_level_map: dict) -> tuple[int, str|None]:
    if key in toc_level_map:
        return toc_level_map[key], key
    elif "_^_" in key:
        pairs = key.split("_^_")
        if len(pairs) == 2:
            return get_text_level(pairs[1], toc_level_map)
        else:
            new_key = "_^_".join([*pairs[:-2], pairs[-1]])
            return get_text_level(new_key, toc_level_map)
    else:
        return 0, None


def resolve_toc_level(document_state: DocumentState):
    """处理目录等级"""
    document = document_state.document
    toc = get_toc(document_state.document)
    if toc is None:
        logger.warning(f"文档【{document_state.origin_document.name}】目录不存在！")
    else:
        toc_item_list = toc.items
        toc_level_map = iter_toc_item(toc_item_list)
        prefix = ""
        in_toc_area = False
        for content in document.content_list:
            if content.type == "text":
                key = enhance_toc_item_title(prefix, content.content)
                level, new_prefix = get_text_level(key, toc_level_map)
                if level > 0:
                    in_toc_area = True
                    content.text_level = level
                    prefix = new_prefix
                elif in_toc_area:
                    content.text_level = 0



def invoke(specification_code: str, document_name: str, origin_document: OriginDocument, standard_specification: StandardSpecification) -> DocumentState:
    """调用文档解析图"""
    page_list = origin_document.page_list
    document = Document.from_original_document(origin_document)
    document_state: DocumentState = DocumentState(origin_document=origin_document, document=document)
    page_index = 0
    page_size = len(page_list)
    while page_index < page_size:
        # logger.info(f"正在解析第{page_index+1}/{page_size}页")
        page = page_list[page_index]
        page_state = page_invoke(page_content=page, specification_code=specification_code, document_name=document_name,
                                 page_index=page_index, page_list=page_list, document_state=document_state, standard_specification=standard_specification)
        page_index += page_state.get("page_step")
    resolve_toc_level(document_state)
    return document_state
