from parser.excel_parser import parse_excel
from pathlib import Path
from graph.main.index import invoke
from dotenv import load_dotenv
import json
import logging
from utils.path_util import resolve_file_path

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv()

# 是否跳过已存在的输出文件
skip_output_exist = True

output_dir = Path(__file__).resolve().parent.parent / "output"

output_dir.mkdir(parents=True, exist_ok=True)

file_name = "现行公路工程行业标准.xlsx"

file_path = Path(__file__).resolve().parent.parent / file_name

standard_specification_config_list = parse_excel(file_path)

logger.info("")

for index,standard_specification_config in enumerate(standard_specification_config_list):
    try:
        output_file_path = resolve_file_path(output_dir, standard_specification_config.code, file_name="data.json")
        if skip_output_exist and output_file_path.exists():
            logger.info(f"标准规范【{standard_specification_config.code}】解析结果已存在，跳过处理 {index+1}/{len(standard_specification_config_list)}")
            continue
        logger.info(f"开始处理标准规范：{standard_specification_config.code}  {index+1}/{len(standard_specification_config_list)}")
        result = invoke(standard_specification_config)
        standard_specification = result.get("standard_specification")
        document_list = result.get("document_list",[])
        document_data = [document.model_dump() for document in document_list]
        data = {
            "document_list": document_data,
            "standard_specification_config": standard_specification_config.model_dump(),
            "standard_specification": standard_specification.model_dump(),
        }
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.write_text(json.dumps(data, ensure_ascii=False, indent=4))
    except Exception as e:
        logger.error(f"处理标准规范【{standard_specification_config.code}】时出错：{e}")
        continue
