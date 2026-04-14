from pydantic import BaseModel, Field
from enums.document_status import DocumentStatus
import logging
import os

from knowledge.splitter.SizeSplitter import SizeSplitter
from knowledge.utils.dify_util import create_document, get_document_list, \
    delete_document, update_document_metadata, Metadata
from knowledge.cache.markdown_cache import exists as exist_markdown, get_markdown, cache_markdown
from factory.document_content_factory import create

logger = logging.getLogger(__name__)


class DocumentImportResult(BaseModel):
    """文档导入结果"""
    document_id: str = Field(description="文档id")
    name: str = Field(description="文档名称")
    status: DocumentStatus = Field(description="文档状态")
    batch: str = Field(description="批次id", default="")


class Document:

    def __init__(self, dataset_id: str, spec_code: str, data: dict, md5_metadata: Metadata) -> None:
        self._dataset_id = dataset_id
        self._spec_code = spec_code
        self._data = data
        self._md5_metadata = md5_metadata
        self.min_token_count = int(os.getenv("KNOWLEDGE_MIN_TOKEN_COUNT"))
        self.token_count = int(os.getenv("KNOWLEDGE_TOKEN_COUNT"))
        self.max_token_count = int(os.getenv("KNOWLEDGE_MAX_TOKEN_COUNT"))

    def _is_need_upload(self):
        """判断是否需要上传文档"""
        knowledge_document_list = get_document_list(self._dataset_id)
        need_upload = False
        doc_name = self._data.get("name")
        document_info = next((doc for doc in knowledge_document_list if doc.get("name") == doc_name), None)
        if document_info:
            # 已存在对应的文档，插件文档的md5和索引状态
            if document_info.get("indexing_status") == "error":
                # 索引状态为错误，需要重新上传
                need_upload = True
            else:
                doc_metadata = document_info.get("doc_metadata", [])
                if doc_metadata:
                    md5_metadata = next((metadata for metadata in document_info.get("doc_metadata", []) if
                                         metadata.get("name") == "md5"), None)
                    if not md5_metadata or md5_metadata.get("value") != self._data.get("md5"):
                        # md5元数据不存在或不匹配，需要重新上传
                        need_upload = True
                else:
                    need_upload = True
            if need_upload:
                # 先删除对应的文档
                delete_document(self._dataset_id, document_info.get("id"))
        else:
            # 不存在对应的文档，需要上传
            need_upload = True
        return need_upload

    def _update_document_md5_metadata(self, document_id: str):
        """更新文档md5元数据"""
        update_document_metadata(self._dataset_id, [{
            "document_id": document_id,
            "metadata_list": [
                {
                    "id": self._md5_metadata.get("id"),
                    "name": "md5",
                    "type": "string",
                    "value": self._data.get("md5")
                }
            ],
            "partial_update": True
        }])

    def _get_document_chunk_list(self) -> list[str]:
        """获取文档分块列表"""
        doc_name = self._data.get("name")
        splitter_str = "\n@@@@@@\n"
        if exist_markdown(self._spec_code, doc_name):
            content = get_markdown(self._spec_code, doc_name)
            chunk_list = content.split(splitter_str)
        else:
            content_list = [create(item) for item in self._data.get("content_list", [])]
            splitter = SizeSplitter(content_list, self.min_token_count, self.token_count, self.max_token_count)
            chunk_list = splitter.split()
            cache_markdown(self._spec_code, doc_name, splitter_str.join(chunk_list))
        return chunk_list

    def _import(self) -> tuple[str, str]:
        """获取文档Markdown内容"""
        chunk_list = self._get_document_chunk_list()
        batch, document_id = create_document(self._dataset_id, self._data.get("name"), chunk_list)
        self._update_document_md5_metadata(document_id)
        return batch, document_id

    def import_data(self) -> DocumentImportResult:
        """导入数据"""
        doc_name = self._data.get("name")
        logger.info(f"开始处理文档【{doc_name}】")
        need_upload = self._is_need_upload()
        knowledge_document_list = get_document_list(self._dataset_id)
        document_info = next((doc for doc in knowledge_document_list if doc.get("name") == doc_name), None)
        if need_upload:
            batch, document_id = self._import()
            return DocumentImportResult(
                document_id=document_id,
                name=doc_name,
                status=DocumentStatus.WAITING,
                batch=batch
            )
        else:
            logger.info(f"文档【{doc_name}】已存在且未改变，无需上传")
            return DocumentImportResult(
                document_id=document_info.get("id"),
                name=doc_name,
                status=DocumentStatus.NO_CHANGED,
            )
