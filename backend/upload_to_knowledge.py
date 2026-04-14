"""
将资料上传到指定的知识库中
参考配置：.env_example
"""

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from knowledge.dataset import Dataset
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

output_dir = Path(__file__).resolve().parent.parent / "output"

data_files = list(output_dir.glob("**/data.json"))

spec_data_list = []

for data_file in data_files:
    with open(data_file) as json_file:
        spec_data_list.append(json.load(json_file))

dataset = Dataset(spec_data_list)

logger.info("")

dataset.import_data()
