from graph.document.state.document_state import DocumentState
import logging
from model.document import Document

logger = logging.getLogger(__name__)

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

def toc_parser(state: DocumentState):
    """
    目录解析
    主要功能：根据目录校准内容章节层级
    """
    document = state.document
    toc = get_toc(state.document)
    if toc is None:
        logger.warning(f"文档【{state.origin_document.name}】目录不存在！")
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
    return {}