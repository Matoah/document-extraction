import os
import traceback
import json
from enums.document_status import DocumentStatus
from knowledge.document import Document
from knowledge.utils.dify_util import get_dataset_id, create_dataset_metadata, get_document_status, Metadata, \
    get_dataset_metadata_list
import logging
from knowledge.document import DocumentImportResult

logger = logging.getLogger(__name__)

NAME_DICT = {
    DocumentStatus.NO_CHANGED: "未改变",
    DocumentStatus.ERROR: "错误",
    DocumentStatus.WAITING: "等待中",
    DocumentStatus.PARSING: "解析中",
    DocumentStatus.CLEANING: "清理中",
    DocumentStatus.SPLITTING: "切分中",
    DocumentStatus.INDEXING: "索引中",
    DocumentStatus.COMPLETED: "已完成"
}


class Dataset:
    """知识库"""

    def __init__(self, spec_data_list: list[dict]) -> None:
        self._spec_data_list = spec_data_list
        self._dataset_metadata_cache = {}
        self._dataset_id_cache = {}

    def _get_metadata_list(self, dataset_id: str) -> list[Metadata]:
        """获取md5元数据定义,不存在则创建一个"""
        if dataset_id not in self._dataset_metadata_cache:
            # 获取知识库中所有元数据定义
            metadata_list = get_dataset_metadata_list(dataset_id)
            result = []
            # 获取md5元数据定义，不存在则创建一个
            md5_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "md5"), None)
            if not md5_metadata:
                # 创建md5元数据定义
                md5_metadata = create_dataset_metadata(dataset_id, {
                    "name": "md5",
                    "type": "string",
                    "use_count": 0
                })
            result.append(md5_metadata)
            # 获取标准规范编号元数据定义，不存在则创建一个
            spec_code_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "spec_code"), None)
            if not spec_code_metadata:
                spec_code_metadata = create_dataset_metadata(dataset_id, {
                    "name": "spec_code",
                    "type": "string",
                    "use_count": 0
                })
            result.append(spec_code_metadata)
            # 获取标准规范生命周期元数据定义，不存在则创建一个
            stage_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "stage"), None)
            if not stage_metadata:
                stage_metadata = create_dataset_metadata(dataset_id, {
                    "name": "stage",
                    "type": "string",
                    "use_count": 0
                })
            result.append(stage_metadata)
            # 获取文档分类元数据定义，不存在则创建一个
            category_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "category"), None)
            if not category_metadata:
                category_metadata = create_dataset_metadata(dataset_id, {
                    "name": "category",
                    "type": "string",
                    "use_count": 0
                })
            result.append(category_metadata)
            # 获取文档子分类元数据定义，不存在则创建一个
            subcategory_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "subcategory"), None)
            if not subcategory_metadata:
                subcategory_metadata = create_dataset_metadata(dataset_id, {
                    "name": "subcategory",
                    "type": "string",
                    "use_count": 0
                })
            result.append(subcategory_metadata)
            # 获取文档子分类元数据定义，不存在则创建一个
            type_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "type"),
                                        None)
            if not type_metadata:
                type_metadata = create_dataset_metadata(dataset_id, {
                    "name": "type",
                    "type": "string",
                    "use_count": 0
                })
            result.append(type_metadata)
            # 获取文档关键字元数据定义，不存在则创建一个
            keyword_metadata = next((metadata for metadata in metadata_list if metadata.get("name") == "keyword"),
                                 None)
            if not keyword_metadata:
                keyword_metadata = create_dataset_metadata(dataset_id, {
                    "name": "keyword",
                    "type": "string",
                    "use_count": 0
                })
            result.append(keyword_metadata)
            self._dataset_metadata_cache[dataset_id] = result
        return self._dataset_metadata_cache[dataset_id]

    def _get_dataset_id(self, dataset_name: str) -> str:
        """获取数据集ID"""
        if dataset_name not in self._dataset_metadata_cache:
            self._dataset_metadata_cache[dataset_name] = get_dataset_id(dataset_name)
        return self._dataset_metadata_cache[dataset_name]

    def import_data(self):
        """导入数据"""
        document_import_status: list[DocumentImportResult] = []
        dataset_config = os.getenv("KNOWLEDGE_DATASET")
        dataset_dict = json.loads(dataset_config)
        for i, spec_data in enumerate(self._spec_data_list):
            dataset_name = dataset_dict.get(spec_data.get("standard_specification_config",{}).get("domain"))
            dataset_id = self._get_dataset_id(dataset_name)
            metadata_list = self._get_metadata_list(dataset_id)
            spec_code = spec_data.get("standard_specification").get("code")
            logger.info(f"正在处理标准规范：{spec_code} {i + 1}/{len(self._spec_data_list)}")
            document_list = spec_data.get("document_list", [])
            for document in document_list:
                doc = Document(dataset_id, spec_code, document, metadata_list)
                try:
                    result = doc.import_data()
                    document_import_status.append(result)
                except Exception as e:
                    traceback.print_exc()
                    logger.error(f"导入文档【{document.get("name")}】失败：{e}")
                    document_import_status.append(DocumentImportResult(
                        document_id="",
                        status=DocumentStatus.ERROR,
                        batch="",
                        name=document.get("name"),
                    ))
        statistics_info = {
            DocumentStatus.NO_CHANGED: 0,
            DocumentStatus.ERROR: 0,
            DocumentStatus.WAITING: 0,
            DocumentStatus.PARSING: 0,
            DocumentStatus.CLEANING: 0,
            DocumentStatus.SPLITTING: 0,
            DocumentStatus.INDEXING: 0,
            DocumentStatus.COMPLETED: 0
        }
        for doc in document_import_status:
            statistics_info[doc.status] += 1
        while True:
            doing_result = [result for result in document_import_status if
                            result.status not in [DocumentStatus.NO_CHANGED, DocumentStatus.ERROR,
                                                  DocumentStatus.COMPLETED]]
            if doing_result:
                for result in doing_result:
                    statistics_info[result.status] -= 1
                    batch = result.batch
                    if batch:
                        status = get_document_status(dataset_id, batch)
                    else:
                        status = DocumentStatus.COMPLETED
                    result.status = DocumentStatus(status)
                    statistics_info[result.status] += 1
            else:
                break
        logger.info("*" * 30)
        logger.info(f"当前文档状态统计: ")
        for key, value in statistics_info.items():
            if key == DocumentStatus.ERROR:
                logger.error(f"{NAME_DICT[key]}: {value}")
            else:
                logger.info(f"{NAME_DICT[key]}: {value}")
        logger.info("所有文档导入完成")
