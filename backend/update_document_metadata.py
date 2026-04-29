"""
更新文档元数据
主要内容：
    更新文档元数据，包括文档类型、文档关键字、文档状态等。
"""
from pathlib import Path
import json
import os
from knowledge.utils.dify_util import get_dataset_id, get_document_list, update_document_metadata
from knowledge.dataset import Dataset
from dotenv import load_dotenv

load_dotenv()

output_dir = Path(__file__).resolve().parent.parent / "output" / "公路工程"

data_files = list(output_dir.glob("**/data.json"))

spec_data_list = []

for data_file in data_files:
    with open(data_file) as json_file:
        spec_data_list.append(json.load(json_file))

dataset_config = os.getenv("KNOWLEDGE_DATASET")
dataset_dict = json.loads(dataset_config)
documents = None
for i, spec_data in enumerate(spec_data_list):
    print(f"Processing {i+1}/{len(spec_data_list)}")
    dataset_name = dataset_dict.get(spec_data.get("standard_specification_config",{}).get("domain"))
    dataset_id = get_dataset_id(dataset_name)
    metadata_list = Dataset._get_metadata_list(dataset_id)
    document_list = spec_data.get("document_list", [])
    if documents is None:
        documents = get_document_list(dataset_id)
    for document in document_list:
        document_name = document.get("name")
        document_id = next((document.get("id") for document in documents if document.get("name") == document_name), None)
        if document_id:
            md5_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "md5"), None)
            spec_code_metadata = next(
                (metadata for metadata in metadata_list if metadata.get("name") == "spec_code"), None)
            stage_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "stage"),
                                  None)
            category_metadata = next(
                (metadata for metadata in metadata_list if metadata.get("name") == "category"), None)
            subcategory_metadata = next(
                (metadata for metadata in metadata_list if metadata.get("name") == "subcategory"), None)
            keyword_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "keyword"),
                                    None)
            update_document_metadata(dataset_id, [{
                "document_id": document_id,
                "metadata_list": [
                    {
                        "id": md5_metadata.get("id"),
                        "name": "md5",
                        "type": "string",
                        "value": document.get("md5")
                    }, {
                        "id": spec_code_metadata.get("id"),
                        "name": "spec_code",
                        "type": "string",
                        "value": spec_data.get("standard_specification_config",{}).get("code")
                    }, {
                        "id": stage_metadata.get("id"),
                        "name": "stage",
                        "type": "string",
                        "value": document.get("stage")
                    }, {
                        "id": category_metadata.get("id"),
                        "name": "category",
                        "type": "string",
                        "value": document.get("category")
                    }, {
                        "id": subcategory_metadata.get("id"),
                        "name": "subcategory",
                        "type": "string",
                        "value": document.get("subcategory")
                    }, {
                        "id": keyword_metadata.get("id"),
                        "name": "keyword",
                        "type": "string",
                        "value": ",".join(document.get("keywords", []))
                    }
                ],
                "partial_update": True
            }])

