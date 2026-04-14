from collections.abc import Callable
from typing import Any

def _aside_text(paragraph: dict)-> str|None:
    """获取侧边栏文本"""
    return None

def _code_text(paragraph: dict)-> str|None:
    """获取代码文本"""
    code_caption = paragraph.get("code_caption", [])
    code_body = paragraph.get("code_body", "")
    return "\n".join([*code_caption, code_body])

def _equation_text(paragraph: dict)-> str|None:
    """获取公式文本"""
    equation = paragraph.get("text", "").strip()
    return equation

def _footer_text(paragraph: dict)-> str|None:
    """获取页脚文本"""
    return _text_text(paragraph)

def _header_text(paragraph: dict)-> str|None:
    """获取页眉文本"""
    return _text_text(paragraph)

def _image_text(paragraph: dict)-> str|None:
    """获取图片文本"""
    image_path = paragraph.get("img_path", "")
    image_caption = paragraph.get("image_caption", [])
    image_footnote = paragraph.get("image_footnote", [])
    return "\n".join([f"![]({image_path})",*image_caption, *image_footnote])

def _list_text(paragraph: dict)-> str|None:
    """获取列表文本"""
    list_items = paragraph.get("list_items", [])
    return "\n".join(list_items)

def _page_footnote_text(paragraph: dict)-> str|None:
    """获取页脚注文本"""
    return None

def _page_number_text(paragraph: dict)-> str|None:
    """获取页码文本"""
    return None

def _table_text(paragraph: dict)-> str|None:
    """获取表格文本"""
    img_path = paragraph.get("img_path", "")
    table_caption = paragraph.get("table_caption", [])
    table_footnote = paragraph.get("table_footnote", [])
    table_body = paragraph.get("table_body", "")
    return "\n".join([*table_caption, table_body, *table_footnote])

def _text_text(paragraph: dict)-> str|None:
    """获取文本文本"""
    return paragraph.get("text", "")


dispatcher: dict[str, Callable[[Any], Any]] = {
    "aside_text": _aside_text,
    "code": _code_text,
    "footer": _footer_text,
    "header": _header_text,
    "image": _image_text,
    "list": _list_text,
    "page_footnote": _page_footnote_text,
    "page_number": _page_number_text,
    "table": _table_text,
    "text": _text_text,
    "equation": _equation_text,
}


def to_text(paragraph_list: list[dict]) -> str:
    """将段落列表转换为文本"""
    return get_content(paragraph_list)

def get_content(paragraph_list: list[dict], include_header: bool = False, include_footer: bool = False) -> str:
    """获取段落列表的文本内容"""
    text_list = []
    exclude_types = []
    if not include_header:
        exclude_types.append("header")
    if not include_footer:
        exclude_types.append("footer")
    for paragraph in paragraph_list:
        type = paragraph.get("type", "text")
        if type in exclude_types:
            continue
        if type in dispatcher:
            handler = dispatcher.get(type)
            text = handler(paragraph)
            if text is not None:
                text_list.append(text)
        else:
            raise ValueError(f"不支持的段落类型: {type}")
    return "\n".join(text_list)
