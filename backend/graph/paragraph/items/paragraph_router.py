from graph.paragraph.state.paragraph_state import ParagraphState


def paragraph_router(state: ParagraphState):
    """段落路由"""
    paragraph = state.paragraph
    paragraph_type = paragraph.get("type","text")
    return paragraph_type
