from graph.paragraph.state.paragraph_state import ParagraphState
from model.code import Code
from langgraph.runtime import Runtime
from graph.paragraph.state.paragraph_context import ParagraphContext
from utils.document_util import get_doc_page_index


def code_parser(state: ParagraphState, runtime: Runtime[ParagraphContext]):
    """代码解析"""
    context = runtime.context
    paragraph = state.paragraph
    code_caption = paragraph.get("code_caption", [])
    code_body = paragraph.get("code_body", "")
    code_language = paragraph.get("guess_lang", "")
    doc_page_index = get_doc_page_index(context.page_index, 1, context.page_list)
    return {
        "result": Code(
            page_index=context.page_index,
            doc_page_index=doc_page_index[0] if doc_page_index else -1,
            code_caption=code_caption,
            code_body=code_body,
            code_language=code_language
        )
    }


if __name__ == '__main__':
    print(code_parser(ParagraphState(paragraph={
        "type": "code",
        "sub_type": "code",
        "code_caption": [],
        "code_body": "MessageFrame::=CHOICE{ rsiEtcFrame[0] EtcRoadSideInformation, --路侧消息播报 megEtcFrame[1] EtcMessage, --纯文本消息播报 virEtcFrame[2] EtcVehicleAncillaryInformation, --车辆附属信息 binaryInfo[3] EtcBinaryInformation, --二进制数据 slti[4] SleepTimeIndication, --休眠时间指示 config[5] RunConfig, --配置信息",
        "guess_lang": "txt",
        "bbox": [
            132,
            319,
            623,
            639
        ],
        "page_idx": 67
    })))
