from graph.main.state.main_state import MainState
import os
from pathlib import Path
from parser.document_parser import DocumentParser
from graph.document.index import invoke
import logging
from model.standard_specification_config import StandardSpecificationConfig

logger = logging.getLogger(__name__)


def _get_file_path_by_name(standard_specification_config: StandardSpecificationConfig, file_name: str) -> Path:
    """根据文件名获取文件路径"""
    document_base_dir = os.getenv("DOCUMENT_BASE_DIR")
    domain_path = Path(document_base_dir) / "解析结果" /standard_specification_config.domain
    document_dir = list(domain_path.glob(f"{file_name}*"))
    if len(document_dir) == 0 or len(document_dir) > 1:
        raise FileNotFoundError(f"文件【{file_name}】不存在或有多个匹配")
    return document_dir[0]


def standard_specification_config_parser(state: MainState):
    """解析标准规范配置"""
    standard_specification_config = state.standard_specification_config
    file_names = standard_specification_config.file_names
    document_list = state.document_list
    for file_name in file_names:
        file_path = _get_file_path_by_name(standard_specification_config, file_name)
        document_parser = DocumentParser(file_name=file_name, document_dir=file_path)
        origin_document = document_parser.parse()
        logger.info(f"开始解析文件:{origin_document.name}")
        document_state = invoke(specification_code=standard_specification_config.code, document_name=file_path.name,
                                origin_document=origin_document, standard_specification=state.standard_specification)
        document_list.append(document_state.get("document"))
    return state
