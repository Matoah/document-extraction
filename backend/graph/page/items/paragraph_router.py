from graph.page.state.page_state import PageState

def _is_announcement_page(page_data: list[dict]) -> bool:
    """
        判断是否是公告页
        判断条件：
            1、公告页单独为一页
            2、公告页的段落类型为"title"，内容为"公告"
        判断结果：
            True：是公告页
            False：不是公告页
    """
    if len(page_data) < 2:
        return False
    paragraph = page_data[1]
    if paragraph:
        type = paragraph.get("type", "text")
        if type == "title" or type == "text":
            content = paragraph.get("text", "").replace(" ", "")
            if content == "公告":
                return True
    return False

def _is_notice_page(page_data: list[dict]) -> bool:
    """判断是否是通知页"""
    if len(page_data) < 2:
        return False
    paragraph = page_data[1]
    if paragraph and paragraph.get("type", "text") == "title" and paragraph.get("content", "") == "通知":
        return True
    return False

def _is_foreword_page(page_data: list[dict], page_state: PageState) -> bool:
    """
        判断是否是前言页
        判断条件：
            1、前言页单独为一页
            2、前言页的段落类型为"title"，内容为"前言"
        判断结果：
            True：是前言页
            False：不是前言页
    :param page_data:
    :return:
    """
    if page_state.page_index > 10:
        # 只在前5页查找前言，超过10页的页码，认为不是前言页（如JTG 1003 一－ 2023中，后面有前言模板）
        return False
    if page_data and len(page_data) >0:
        text = page_data[0].get("text","").replace(" ", "")
        if text == "目次":
            return False
    for paragraph in page_data:
        if paragraph and (paragraph.get("type", "text") == "title" and paragraph.get("content", "") == "前言") or (paragraph.get("type", "text") == "text" and paragraph.get("text", "").replace(" ", "") == "前言"):
            return True
    return False

def _is_toc_page(page_data: list[dict]) -> bool:
    """判断是否是段落页"""
    for paragraph in page_data:
        if paragraph and paragraph.get("type", "text") == "text" and paragraph.get("text", "").replace(" ", "") in ["目次", "目录"]:
            return True
    return False

def paragraph_router(state: PageState):
    """段落路由"""
    page_data = state.page_data
    if _is_announcement_page(page_data):
        return "announcement"
    elif _is_notice_page(page_data):
        return "notice"
    elif _is_foreword_page(page_data, state):
        return "foreword"
    elif _is_toc_page(page_data):
        return "toc"
    else:
        return "paragraph"







