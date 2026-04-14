import os
from requests import get, post, exceptions, delete
from pathlib import Path
import hashlib
from knowledge.cache.file_cache import exists,get_cache,set_cache
import tempfile
import json
import re
import logging
import time
from typing import TypedDict, Any


logger = logging.getLogger(__name__)

class MetadataOperationItem(TypedDict):

    id: str

    type: str

    name: str

    value: Any

class MetadataOperationData(TypedDict):
    """
    文档元数据操作数据
    """
    document_id: str

    metadata_list: list[MetadataOperationItem]

    partial_update: bool

class Metadata(TypedDict):

    id: str

    name: str

    type: str

    use_count: int


def _post(uri: str, headers: dict, data: dict | None = None, files: dict | None = None, json: dict | None = None):
    """post请求"""
    response = post(f"{os.getenv("KNOWLEDGE_BASE_URI")}/{uri}",headers=headers,data=data,  files=files, json=json)
    response.raise_for_status()
    return response

def _get(uri: str, headers: dict, data: dict):
    """get请求"""
    response = get(f"{os.getenv("KNOWLEDGE_BASE_URI")}/{uri}",headers=headers,params=data)
    response.raise_for_status()
    return response

def get_dataset_id():
    """获取知识库ID"""
    dataset_name = os.getenv("KNOWLEDGE_DATASET")
    has_more = True
    page = 1
    while has_more:
        response = _get(
            "datasets",
            {"Authorization": f"Bearer {os.getenv("KNOWLEDGE_API_KEY")}"},
            {"keyword": dataset_name, "include_all": True, "page": page}
        )
        response_json = response.json()
        has_more = response_json.get("has_more", False)
        page += 1
        data = response_json.get("data", [])
        for dataset in data:
            if dataset["name"] == dataset_name:
                return dataset["id"]
    raise ValueError(f"知识库 {dataset_name} 不存在")

def _get_mime_type(ext: str) ->str:
    """获取文件扩展名对应的MIME类型"""
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif'
    }
    return mime_type.get(ext, "application/octet-stream")

def upload_file(abs_path: str | Path) -> str:
    """上传文件，并返回文件ID"""
    path = Path(abs_path)
    if not path.exists():
        raise FileNotFoundError(f"文件 {path} 不存在")
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    if exists(md5):
        return get_cache(md5)
    mime_type = _get_mime_type(path.suffix)
    with open(path, "rb") as file:
        files = {
            "file": (path.name, file, mime_type)
        }
        response = _post(
            uri="files/upload",
            headers = {"Authorization": f"Bearer {os.getenv('KNOWLEDGE_WORKFLOW_API_KEY')}"},
            data = {"user": os.getenv("KNOWLEDGE_USER_ID")},
            files=files
        )
        result = response.json()
        file_id = result["id"] if "id" in result else str(result)
        set_cache(md5, file_id)
        return file_id

def to_preview_url(file_id: str) -> str:
    """将文件ID转换为预览URL"""
    return f"{os.getenv('KNOWLEDGE_HOST')}/files/{file_id}/file-preview"

def _create_empty_document_by_file(dataset_id: str, document_name: str) -> str:
    """创建空文档"""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        document_file_path = os.path.join(tmp_dir_name, document_name)
        file = open(document_file_path, "wb")
        file.close()
        headers = {
            "Authorization": f"Bearer {os.getenv("KNOWLEDGE_API_KEY")}",
        }
        uri = f"datasets/{dataset_id}/document/create-by-file"
        process_rule_data = {
            "indexing_technique": "high_quality",
            "doc_form": "hierarchical_model",
            "process_rule": {
                "rules": {
                    "pre_processing_rules": [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": True}
                    ],
                    "segmentation": {
                        "separator": "###",
                        "max_tokens": 1024
                    },
                    "parent_mode": "paragraph",

                },
                "mode": "hierarchical",
                "subchunk_segmentation": {'separator': '\n', 'max_tokens': 512}
            }
        }

        data = {
            'data': json.dumps(process_rule_data)
        }
        try:
            with open(document_file_path, 'rb') as f:
                files = {
                    'file': f
                }

                response = _post(
                    uri=uri,
                    headers=headers,
                    data=data,
                    files=files
                )
                result = response.json()
                document_info = result.get('document', {})
                return document_info.get('id')
        except Exception as e:
            raise Exception(f"创建文档失败: {e}")

def get_document_status(dataset_id: str, batch: str) -> str:
    """判断文档索引是否完成"""
    uri = f"datasets/{dataset_id}/documents/{batch}/indexing-status"
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
    }
    data = {}

    response = _get(uri=uri, headers=headers, data=data)
    result = response.json()
    data = result.get("data",[])
    if not data:
        return False
    return data[0].get('indexing_status')

def _create_empty_document_by_text(dataset_id: str, document_name: str, chunk_list: list[str]) -> tuple[str, str]:
    """创建空文档"""
    headers = {
        "Authorization": f"Bearer {os.getenv("KNOWLEDGE_API_KEY")}",
        'Content-Type': 'application/json'
    }
    separator = "\n@@@@\n"
    uri = f"datasets/{dataset_id}/document/create-by-text"
    data = {
        'name': document_name,
        'text': separator.join(chunk_list),
        'doc_language': 'Chinese',
        "indexing_technique": "high_quality",
        "doc_form": "hierarchical_model",
        "process_rule": {
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True}
                ],
                "segmentation": {
                    "separator": separator,
                    "max_tokens": 1024
                },
                "parent_mode": "paragraph",
                "subchunk_segmentation": {'separator': '\n', 'max_tokens': 512}
            },
            "mode": "hierarchical",
        }
    }
    try:
        response = _post(uri=uri, headers=headers, json=data)
        result = response.json()
        document_info = result.get('document', {})
        document_id = document_info.get('id')
        batch = result.get('batch')
        return batch, document_id
    except Exception as e:
        raise Exception(f"创建文档失败: {e}")


def create_document(dataset_id: str, document_name: str, chunk_list: list[str]) -> tuple[str, str]:
    """创建文档"""
    return _create_empty_document_by_text(dataset_id, document_name, chunk_list)

# 知识库文档列表缓存
document_list: list[dict] | None = None

def get_document_list(dataset_id: str) -> list[dict]:
    """获取文档列表"""
    global document_list
    if document_list is None:
        uri = f"datasets/{dataset_id}/documents"
        headers = {
            'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
        }
        data = {
            "limit": 1000
        }
        response = _get(uri=uri, headers=headers, data=data)
        document_list = response.json().get("data", [])
    return document_list

def upload_document_segments(dataset_id: str, document_id: str, segments: list[str]) -> str:
    """创建文档段落"""
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
        'Content-Type': 'application/json'
    }
    segments = [{"content": segment} for segment in segments]
    # 构造请求数据
    data = {
        "segments": segments
    }
    try:
        response = _post(
            uri=f"datasets/{dataset_id}/documents/{document_id}/segments",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        if 'data' in result:
            for segment_data in result['data']:
                segment_id = segment_data.get('id')
                content = segment_data.get('content', '')
                # 先删除子分段
                # 检查内容是否超过4行需要切分
                if segment_id and content:
                    lines = content.split('\n')
                    if len(lines) > 4:
                        # 需要创建子分段
                        _create_child_chunks_simple(
                            dataset_id, document_id, segment_id, content
                        )

        return result
    except exceptions.RequestException as e:
        raise Exception(f"上传文档分段失败: {e}")


def _create_child_chunks_simple(
        dataset_id: str,
        document_id: str,
        segment_id: str,
        content: str,
        max_lines_per_chunk: int = 4
) -> None:
    """
    为长内容创建子分段（简单版本：检查HTML表格标签）
    """

    # 创建子分段
    child_chunks = _split_markdown_chunk(content)
    # 上传每个子分段
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
        'Content-Type': 'application/json'
    }

    for i, chunk_content in enumerate(child_chunks):
        if chunk_content.strip():  # 确保内容不为空
            try:
                payload = {
                    "content": chunk_content.strip()
                }
                response = _post(
                    uri=f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                logger.info(f"成功创建子分段 {i + 1}/{len(child_chunks)}: {segment_id}")
            except exceptions.RequestException as e:
                raise Exception(f"创建子分段失败 {segment_id}: {e}")
            except Exception as e:
                raise Exception(f"创建子分段时发生错误: {e}")


def _split_markdown_chunk(chunk: str, max_length: int = 30) -> list[str]:
    """
    将已拆分的markdown块进一步细分，保持语义完整性
    """
    sentences = _split_text_to_sentences(chunk, max_length=max_length)
    if len(sentences) > 1:
        if len(chunk) < 300:
            sentences.append(chunk)
    return sentences


def _split_text_to_sentences(text: str, max_length: int) -> list[str]:
    """
    更智能的文本到句子的切分
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    # 使用正则表达式进行句子切分（中英文混合）
    sentences = re.split(r'(?<=[.!?。！？])\s+', text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # 对于过长的句子，进一步处理
    final_sentences = []
    for sentence in sentences:
        if len(sentence) > max_length:  # 如果句子太长
            # 按逗号、分号等进一步切分
            sub_sentences = re.split(r'(?<=[，,；;:])\s*', sentence)
            if len(sub_sentences) > 1:
                # 如果能成功切分，使用子句
                for sub_sentence in sub_sentences:
                    if sub_sentence.strip():
                        final_sentences.append(sub_sentence.strip())
            else:
                # 对于中文，按句号切分
                if re.search(r'[\u4e00-\u9fff]', sentence):  # 包含中文
                    sub_sentences = re.split(r'(?<=[。])', sentence)
                    final_sentences.extend([s.strip() for s in sub_sentences if s.strip()])
                else:
                    final_sentences.append(sentence)
        else:
            final_sentences.append(sentence)

    return [s for s in final_sentences if s]

def get_dataset_metadata(dataset_id: str) -> list[dict]:
    """获取数据集元数据"""
    uri = f"datasets/{dataset_id}/metadata"
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
    }
    try:
        response = _get(uri=uri, headers=headers, data={})
        result = response.json()
        return result
    except exceptions.RequestException as e:
        raise Exception(f"获取数据集元数据失败: {e}")

def delete_document(dataset_id: str, document_id: str) -> None:
    """删除文档"""
    uri = f"{os.getenv("KNOWLEDGE_BASE_URI")}/datasets/{dataset_id}/documents/{document_id}"
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
    }
    try:
        response = delete(url=uri, headers=headers)
        response.raise_for_status()
        logger.info(f"成功删除文档 {document_id}")
    except exceptions.RequestException as e:
        raise Exception(f"删除文档失败: {e}")

def get_dataset_metadata_list(dataset_id: str) -> list[Metadata]:
    """获取数据集元数据列表"""
    uri = f"datasets/{dataset_id}/metadata"
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
    }
    data = {}
    response = _get(uri=uri, headers=headers, data=data)
    result = response.json()
    return [Metadata(**item) for item in result.get("doc_metadata", [])]

def create_dataset_metadata(dataset_id: str, metadata: dict) -> Metadata:
    """创建数据集元数据"""
    uri = f"datasets/{dataset_id}/metadata"
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
        'Content-Type': 'application/json'
    }
    response = _post(uri=uri, headers=headers, json=metadata)
    result = response.json()
    return Metadata(**result)


def update_document_metadata(dataset_id: str, metadata: list[MetadataOperationData]) -> None:
    """更新文档元数据"""
    uri = f"datasets/{dataset_id}/documents/metadata"
    headers = {
        'Authorization': f'Bearer {os.getenv("KNOWLEDGE_API_KEY")}',
        'Content-Type': 'application/json'
    }
    data = {
        "operation_data": metadata
    }
    try:
        _post(uri=uri, headers=headers, json=data)
    except exceptions.RequestException as e:
        raise Exception(f"更新文档元数据失败：{e}")