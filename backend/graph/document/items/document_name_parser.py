from graph.document.state.document_state import DocumentState
from model.document import Document

def classify(name):
    # 一级分类
    if any(k in name for k in ["设计"]):
        level1 = "设计"
    elif any(k in name for k in ["施工"]):
        level1 = "施工"
    elif any(k in name for k in ["养护"]):
        level1 = "养护"
    elif any(k in name for k in ["试验", "检测"]):
        level1 = "试验检测"
    elif any(k in name for k in ["造价", "定额", "预算", "概算"]):
        level1 = "造价"
    elif any(k in name for k in ["信息", "模型", "智能", "自动驾驶"]):
        level1 = "信息化"
    elif any(k in name for k in ["勘测", "勘察", "地质", "水文"]):
        level1 = "勘察"
    elif any(k in name for k in ["安全", "抗震", "评价"]):
        level1 = "质量安全"
    else:
        level1 = "综合"

    # 二级分类
    if "桥" in name:
        level2 = "桥梁"
    elif "隧道" in name:
        level2 = "隧道"
    elif "路基" in name:
        level2 = "路基"
    elif "路面" in name:
        level2 = "路面"
    elif "交通" in name:
        level2 = "交通工程"
    else:
        level2 = "通用"

    return level1, level2

def extract_keywords(name):
    keywords = []
    for k in ["桥梁", "隧道", "路基", "路面", "抗震", "施工", "设计", "养护"]:
        if k in name:
            keywords.append(k)
    return keywords

def detect_type(name):
    """根据标准规范名称检测类型"""
    mapping = {
        "标准": "standard",
        "规范": "specification",
        "细则": "guideline",
        "规程": "procedure",
        "导则": "guide",
        "办法": "method",
        "定额": "quota",
        "指南": "guidance",
        "通用图": "drawing"
    }
    for k, v in mapping.items():
        if k in name:
            return v
    return "unknown"


def detect_stage(name):
    """根据标准规范名称检测生命周期阶段"""
    if "设计" in name:
        return "设计阶段"
    if "施工" in name:
        return "施工阶段"
    if "养护" in name:
        return "养护阶段"
    if "检测" in name or "试验" in name:
        return "检测阶段"
    return "全生命周期"

def document_name_parser(state: DocumentState):
    """解析文档名称"""
    document_name = state.origin_document.name
    document: Document = state.document
    level1, level2 = classify(document_name)
    document.category = level1
    document.subcategory = level2
    document.keywords = extract_keywords(document_name)
    document.type = detect_type(document_name)
    document.stage = detect_stage(document_name)
    return {}