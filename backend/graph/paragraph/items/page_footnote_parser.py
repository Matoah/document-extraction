from graph.paragraph.state.paragraph_state import ParagraphState


def page_footnote_parser(state: ParagraphState):
    """脚注解析，忽略页脚注"""
    return {}