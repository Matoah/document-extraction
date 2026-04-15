"""
上传到知识库, 将文档结构化数据切块后上传到知识库
"""
from pathlib import Path
import json
import logging
from knowledge.dataset import Dataset

logger = logging.getLogger(__name__)

def upload_to_knowledge():
    output_dir = Path(__file__).resolve().parent.parent / "output"

    data_files = list(output_dir.glob("**/data.json"))

    spec_data_list = []

    for data_file in data_files:
        with open(data_file) as json_file:
            spec_data_list.append(json.load(json_file))

    dataset = Dataset(spec_data_list)

    logger.info("")

    dataset.import_data()