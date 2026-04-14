from graph.paragraph.state.paragraph_context import ParagraphContext
from graph.paragraph.state.paragraph_state import ParagraphState
from model.image import Image
from langgraph.runtime import Runtime

from utils.document_util import get_doc_page_index


def _get_caption(image_caption: list[str]) -> str:
    """从图片标题中提取图片编号"""
    # if not image_caption or len(image_caption) > 1:
    #    raise ValueError("图片标题中只能包含一个编号")
    if len(image_caption) < 1:
        return ""
    return image_caption[0]


def _get_code(image_caption: list[str]) -> str:
    """从图片标题中提取图片编号"""
    caption = _get_caption(image_caption)
    items = caption.split(" ")
    if len(items) == 1:
        return ""
        # raise ValueError("图片标题未包含空格，无法提取编号")
    code = items[0]
    if code.startswith("图"):
        # 去除编号中所有的空格
        return code.replace(" ", "")
    else:
        return ""
        # raise ValueError("图片标题中必须包含图")


def _get_title(image_caption: list[str]) -> str:
    """从图片标题中提取图片名称"""
    caption = _get_caption(image_caption)
    items = caption.split(" ")
    if len(items) == 1:
        return items[0]
        # raise ValueError("图片标题未包含空格，无法提取名称")
    return items[1]


def image_parser(state: ParagraphState, runtime: Runtime[ParagraphContext]):
    """图片解析"""
    context = runtime.context
    page_index = context.page_index
    paragraph = state.paragraph
    image_path = paragraph.get("img_path", "")
    image_caption = paragraph.get("image_caption", [])
    # 移除image_caption中的空字符串及None值
    image_caption = [caption.strip() for caption in image_caption if caption.strip()]
    image_footnote = paragraph.get("image_footnote", [])
    doc_page_index = get_doc_page_index(page_index, 1, context.page_list)
    return {
        "result": Image(
            page_index=page_index,
            doc_page_index=doc_page_index[0] if doc_page_index else -1,
            path=image_path,
            code=_get_code(image_caption),
            title=_get_title(image_caption),
            footer_notes=image_footnote
        )
    }


if __name__ == "__main__":
    print(image_parser(state=ParagraphState(paragraph={
        "type": "image",
        "img_path": "images/f49f2e96d3827dc9dcfbdeba0c021a0cf3c27297b8716fb9573f8bb1f2985308.jpg",
        "image_caption": [
            "图3.0.1 车路协同拓展应用系统（ETC2.0）框架图"
        ],
        "image_footnote": [],
        "bbox": [
            169,
            322,
            830,
            561
        ],
        "page_idx": 9
    })))
