from pathlib import Path
import json
import hashlib
from datetime import datetime

from model.origin_document import OriginDocument


class DocumentParser:
    """文档解析器"""

    def __init__(self, file_name: str, document_dir: str | Path):
        self._file_name = file_name
        self._document_dir = document_dir
        self._origin_document_path = None

    def _get_document_dir_path(self) -> Path:
        """获取文档目录路径"""
        dir_path = Path(self._document_dir)
        if not dir_path.exists():
            raise FileNotFoundError(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(dir_path)
        return dir_path

    def _get_model_file_path(self):
        """获取模型文件"""
        dir_path = self._get_document_dir_path()
        model_files = list(dir_path.glob("*_content_list.json"))
        if not model_files:
            raise FileNotFoundError(f"文档目录中没有模型文件: {dir_path}")
        return Path(model_files[0])

    def _get_document_markdown_content(self):
        """获取文档Markdown内容"""
        dir_path = self._get_document_dir_path()
        markdown_files = list(dir_path.glob("*.md"))
        if not markdown_files:
            raise FileNotFoundError(f"文档目录中没有Markdown文件: {dir_path}")
        return markdown_files[0].read_text(encoding="utf-8")

    def _split_page(self, objects: list[dict]) -> list[list[dict]]:
        """将对象列表按页分割"""
        result = []
        page_list = []
        page_index = 0
        for obj in objects:
            page_idx = obj.get("page_idx", 0)
            if page_idx != page_index:
                page_index = page_idx
                result.append(page_list)
                page_list = [obj]
            else:
                page_list.append(obj)
        if page_list:
            result.append(page_list)
        return result

    def _get_origin_document(self) -> Path:
        if not self._origin_document_path:
            dir_path = self._get_document_dir_path()
            origin_files = list(dir_path.glob("*_origin.pdf"))
            if not origin_files:
                raise FileNotFoundError(f"文档目录中没有原始文件: {dir_path}")
            self._origin_document_path = origin_files[0]
        return self._origin_document_path

    def _get_size(self):
        """获取文件大小"""
        origin_path = self._get_origin_document()
        return origin_path.stat().st_size

    def _get_create_time(self):
        """获取创建时间"""
        origin_path = self._get_origin_document()
        return datetime.fromtimestamp(origin_path.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")

    def _get_last_modified_time(self) -> str:
        """获取最后修改时间"""
        origin_path = self._get_origin_document()
        return datetime.fromtimestamp(origin_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')

    def _get_document_md5(self):
        """获取原始文件md5"""
        origin_path = self._get_origin_document()
        return hashlib.md5(origin_path.read_bytes()).hexdigest()

    def parse(self) -> OriginDocument:
        """解析文档"""
        model_file_path = self._get_model_file_path()
        model_file_content = model_file_path.read_text(encoding="utf-8")
        objects = json.loads(model_file_content)
        page_list = self._split_page(objects)
        document_markdown_content = self._get_document_markdown_content()
        md5_text = hashlib.md5(document_markdown_content.encode("utf-8")).hexdigest()
        return OriginDocument(name=self._file_name, page_list=page_list, md5=md5_text, size=self._get_size(),
                              create_time=self._get_create_time(), modify_time=self._get_last_modified_time())
