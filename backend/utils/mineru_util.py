import re

def _resolve_section(content: str) ->str:
    """增强处理节编号显示异常问题，将1?? 替换成1."""
    content = re.sub(r"(\w+)\?{2}\s*", r"\1.", content)
    prev = None
    while prev != content:
        prev = content
        content = re.sub(r"(\d+)\.\s+(\d+)", r"\1.\2", content)
    return content


def _resolve_semicolon(content: str) -> str:
    """处理分号：ꎻ->;"""
    return content.replace("ꎻ", ";")

def _resolve_comma(content: str) -> str:
    """处理逗号：ꎬ->，"""
    return content.replace("ꎬ","，")

def _resolve_period(content: str) -> str:
    """处理句号：ꎮ-> 。"""
    return content.replace("ꎮ","。")

def _resolve_code(content: str) -> str:
    """处理编号：6￣1->6-1"""
    return re.sub(r"￣", r"-", content)

def _resolve_book_mark(content: str) -> str:
    """处理书名号:«»->《》"""
    return content.replace("«","《").replace("»","》")

def enhance(content: str) -> str:
    """增强处理mineru结果"""
    if content.strip() == "":
        return content
    content = _resolve_section(content)
    content = _resolve_semicolon(content)
    content = _resolve_comma(content)
    content = _resolve_period(content)
    content = _resolve_code(content)
    content = _resolve_book_mark(content)
    return content


if __name__ == "__main__":
    #JTG D81—2017
    result = _resolve_section("1?? 0??4 研究表明:产生道路交通事故的原因中")
    print(result=="1.0.4 研究表明:产生道路交通事故的原因中")
    result = _resolve_section("12?? 1 防风栅 39")
    print(result=="12.1 防风栅 39")
    result = _resolve_section("2. 0. 21 减速丘 speed hump ")
    print(result=="2.0.21 减速丘 speed hump ")
    result = _resolve_section("网 址: http: / / www?? ccpress?? com?? cn")
    print(result=="网 址: http: / / www.ccpress.com.cn")
    result = _resolve_section("表3??5??1 公路交通安全设施结构设计采用的作用")
    print(result=="表3.5.1 公路交通安全设施结构设计采用的作用")
    result = _resolve_semicolon("(1) 将“交通标志”“交通标线”的编排顺序前置ꎬ突出主动引导设施的功能ꎻ")
    print(result=="(1) 将“交通标志”“交通标线”的编排顺序前置ꎬ突出主动引导设施的功能;")
    result = _resolve_comma("研究表明:产生道路交通事故的原因中ꎬ约")
    print(result=="研究表明:产生道路交通事故的原因中，约")
    result = _resolve_period("(6) 新增“其他交通安全设施”一章ꎬ包括“防风栅、防雪栅、积雪标杆、限高架、减速丘和凸面镜”等ꎮ")
    print(result=="(6) 新增“其他交通安全设施”一章ꎬ包括“防风栅、防雪栅、积雪标杆、限高架、减速丘和凸面镜”等。")
    result = _resolve_code("表 6￣1 中此次修订变化的说明如下:")
    print(result=="表 6-1 中此次修订变化的说明如下:")
    result = _resolve_book_mark("«公路交通安全设施设计规范»( — ) 及 «公路交通安全设施设计细则» (JTG/T D81—2017) 的管理权和解释权归交通运输部")
    print(result=="《公路交通安全设施设计规范》( — ) 及 《公路交通安全设施设计细则》 (JTG/T D81—2017) 的管理权和解释权归交通运输部")