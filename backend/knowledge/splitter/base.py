import time
from abc import ABC, abstractmethod
from type.document_content_item import DocumentContentItem
from model.image import Image
from pathlib import Path
import os
from knowledge.utils.dify_util import upload_file, to_preview_url
import logging

logger = logging.getLogger(__name__)

class Splitter(ABC):
    """文档切分器"""

    def __init__(self,
     content: list[DocumentContentItem],
     min_token_count: int,
     token_count: int,
     max_token_count: int
    ):
        self.content = content
        self.min_token_count = min_token_count
        self.token_count = token_count
        self.max_token_count = max_token_count
        self.document_base_dir = Path(os.getenv("DOCUMENT_BASE_DIR"))

    def _enhance_image(self):
        """增强图片URL"""
        for content_item in self.content:
            if isinstance(content_item, Image):
                image_path = content_item.path
                if image_path:
                    image_abs_path_list = list(self.document_base_dir.glob(f"**/{image_path}"))
                    if len(image_abs_path_list) != 1:
                        raise FileNotFoundError(f"图片【{image_path}】不存在或有多个匹配")
                    else:
                        image_abs_path = image_abs_path_list[0]
                        file_id = upload_file(image_abs_path)
                        logger.info(f"上传图片【{image_path}】到Dify，文件ID: {file_id}, 防止被识别成DOS攻击，等待1秒")
                        time.sleep(1)
                        image_url = to_preview_url(file_id)
                        content_item.path = image_url

    @abstractmethod
    def _split(self) -> list[str]:
        """内部切分文档"""
        raise NotImplementedError

    def split(self) -> list[str]:
        """切分文档"""
        self._enhance_image()
        return self._split()
