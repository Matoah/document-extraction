from enums.standard import StandardNature
from graph.main.state.main_state import MainState

def detect_standard_nature(code):
    """根据标准规范编号检测标准性质"""
    if code.startswith("JTG "):
        return StandardNature.MANDATORY
    else:
        return StandardNature.RECOMMENDED


def standard_specification_name_parser(state: MainState):
    """标准规范名称解析器"""
    state.standard_specification.standard_nature = detect_standard_nature(state.standard_specification.code)
    return {}
