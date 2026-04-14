from graph.paragraph.state.paragraph_context import ParagraphContext
from graph.paragraph.state.paragraph_state import ParagraphState
from model.table import Table
from langgraph.runtime import Runtime

from utils.document_util import get_doc_page_index


def _get_caption(image_caption: list[str]) -> str:
    """从表格标题中提取表格编号"""
    #if not image_caption or len(image_caption) > 1:
    #    raise ValueError("表格标题中只能包含一个编号")
    if len(image_caption) < 1:
        return ""
    return image_caption[0]


def _get_code(table_caption: list[str]) -> tuple[str, bool]:
    """从表格标题中提取表格编号"""
    table_caption = [caption.strip() for caption in table_caption]
    caption = _get_caption(table_caption)
    items = caption.split(" ")
    if len(items) == 1:
        return "", False
        #raise ValueError("表格标题未包含空格，无法提取编号")
    if len(items) > 2:
        first_item = "".join(items[:-1])
        last_item = items[-1]
        items = [first_item, last_item]
    code = items[0]
    if code.startswith("表"):
        # 去除编号中所有的空格
        return code.replace(" ", ""), False
    elif code.startswith("续表"):
        return code.replace(" ", ""), True
    elif code:
        return code, False
    else:
        raise ValueError("表格标题中必须包含表")


def _get_title(image_caption: list[str]) -> str:
    """从表格标题中提取表格标题"""
    caption = _get_caption(image_caption)
    items = caption.split(" ")
    if len(items) == 1:
        return items[0]
        # raise ValueError("表格标题未包含空格，无法提取名称")
    if len(items) > 2:
        first_item = "".join(items[:-1])
        last_item = items[-1]
        items = [first_item, last_item]
    return items[1]


def table_parser(state: ParagraphState, runtime: Runtime[ParagraphContext]):
    """表格解析"""
    context = runtime.context
    page_index = context.page_index
    paragraph = state.paragraph
    img_path = paragraph.get("img_path", "")
    table_caption = paragraph.get("table_caption", [])
    table_footnote = paragraph.get("table_footnote", [])
    table_body = paragraph.get("table_body", "")
    doc_page_index = get_doc_page_index(page_index, 1, context.page_list)
    code, is_continued = _get_code(table_caption)
    return {
        "result": Table(
            page_index=page_index,
            doc_page_index=doc_page_index[0] if doc_page_index else -1,
            img_path=img_path,
            code=code,
            is_continued=is_continued,
            title=_get_title(table_caption),
            table_body=table_body,
            footer_notes=table_footnote
        )
    }


if __name__ == "__main__":
    print(table_parser(ParagraphState(paragraph={
        "type": "table",
        "img_path": "images/637c149de52a48abef533e00f2d57bdc0e9b53f2f204f466c6b48e698bfc33bd.jpg",
        "table_caption": [
            "表 A. 0.1 服务场景类型及代码"
        ],
        "table_footnote": [],
        "table_body": "<table><tr><td>场景类型</td><td>场景类型代码</td><td colspan=\"2\">场景子类型</td><td>场景子类型代码</td></tr><tr><td rowspan=\"13\">特殊路段行车风险预警</td><td rowspan=\"13\">01</td><td colspan=\"2\">急弯路段</td><td>01001</td></tr><tr><td colspan=\"2\">陡坡路段</td><td>01002</td></tr><tr><td colspan=\"2\">连续长陡下坡路段</td><td>01003</td></tr><tr><td colspan=\"2\">易发崩塌路段</td><td>01004</td></tr><tr><td colspan=\"2\">易发滑坡路段</td><td>01005</td></tr><tr><td colspan=\"2\">临崖路段</td><td>01006</td></tr><tr><td colspan=\"2\">临河湖路段</td><td>01007</td></tr><tr><td colspan=\"2\">临深沟路段</td><td>01008</td></tr><tr><td colspan=\"2\">分合流(出入口)区路段</td><td>01009</td></tr><tr><td colspan=\"2\">构造物节点</td><td>01010</td></tr><tr><td colspan=\"2\">特大桥梁路段</td><td>01011</td></tr><tr><td colspan=\"2\">隧道路段</td><td>01012</td></tr><tr><td colspan=\"2\">其他特殊路段</td><td>01100</td></tr><tr><td rowspan=\"2\">特定限行路段通行预警</td><td rowspan=\"2\">02</td><td colspan=\"2\">专用车道行驶</td><td>02001</td></tr><tr><td colspan=\"2\">其他特定限行路段</td><td>02010</td></tr><tr><td rowspan=\"4\">计划性交通事件管控服务</td><td rowspan=\"4\">03</td><td colspan=\"2\">养护施工</td><td>03001</td></tr><tr><td colspan=\"2\">改扩建施工</td><td>03002</td></tr><tr><td colspan=\"2\">重大活动</td><td>03003</td></tr><tr><td colspan=\"2\">其他计划性交通事件</td><td>03010</td></tr><tr><td rowspan=\"4\">突发性交通事件预警服务</td><td rowspan=\"4\">04</td><td rowspan=\"4\">交通事故</td><td>单车事故</td><td>04110</td></tr><tr><td>多车事故</td><td>04120</td></tr><tr><td>危险品事故</td><td>04130</td></tr><tr><td>其他交通事故</td><td>04190</td></tr></table>",
        "bbox": [
            112,
            318,
            885,
            839
        ],
        "page_idx": 26
    })))
