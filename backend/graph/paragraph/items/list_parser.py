from graph.paragraph.state.paragraph_context import ParagraphContext
from graph.paragraph.state.paragraph_state import ParagraphState
from model.text import Text
from langgraph.runtime import Runtime

from utils.document_util import get_doc_page_index


def list_parser(state: ParagraphState, runtime: Runtime[ParagraphContext]):
    """列表解析"""
    context = runtime.context
    page_index = context.page_index
    paragraph = state.paragraph
    list_items = paragraph.get("list_items", [])
    doc_page_index = get_doc_page_index(page_index, 1, context.page_list)
    return {
        "result": Text(
            page_index=page_index,
            doc_page_index=doc_page_index[0] if doc_page_index else -1,
            content="\n".join(list_items)
        )
    }


if __name__ == "__main__":
    print(list_parser(ParagraphState(paragraph={
        "type": "list",
        "sub_type": "text",
        "list_items": [
            "7.0.8 RSU1.0 + 与 OBU1.0、RSU1.0 + 与 OBU2.0、RSU2.0 与 OBU1.0、RSU2.0 与 OBU2.0 通信，除应符合现行《收费公路联网收费技术标准》（JTG6310）所规定的联网收费密钥体系外，还应符合本规范附录 K 的有关规定。",
            "7.0.9 车路协同拓展应用系统（ETC2.0）应采用国产密码算法实现的身份鉴别、接入认证、数据加解密等，其中密钥和数字证书应由通过国家密码管理机构认定的行业第三方系统提供。"
        ],
        "bbox": [
            109,
            103,
            887,
            250
        ],
        "page_idx": 24
    })))
