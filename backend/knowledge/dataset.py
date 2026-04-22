import time
import traceback

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

    @staticmethod
    def _get_metadata_list(dataset_id: str) -> list[Metadata]:
        """获取md5元数据定义,不存在则创建一个"""
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
        return result

    def import_data(self):
        """导入数据"""
        dataset_id = get_dataset_id()
        metadata_list = Dataset._get_metadata_list(dataset_id)
        document_import_status: list[DocumentImportResult] = []
        for i, spec_data in enumerate(self._spec_data_list):
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
