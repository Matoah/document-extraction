import time
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
import os
from langchain_core.messages import SystemMessage, HumanMessage

from utils.text_util import try_parse_json_object
import logging

logger = logging.getLogger(__name__)


class LLM(ABC):
    """基础大模型"""

    def __init__(self):
        """初始化大模型"""
        api_key = os.getenv("COMPLETION_API_KEY")
        api_url_base = os.getenv("COMPLETION_API_BASE")
        model = os.getenv("COMPLETION_MODEL")
        enable_thinking = os.getenv("COMPLETION_ENABLE_THINKING")
        temperature = float(os.getenv("COMPLETION_TEMPERATURE"))
        max_tokens = int(os.getenv("COMPLETION_MAX_TOKEN"))
        if enable_thinking == "False":
            enable_thinking = False
        else:
            enable_thinking = True
        self._client = ChatOpenAI(
            api_key=api_key,
            base_url=api_url_base,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body={
                "chat_template_kwargs":{
                    "enable_thinking": enable_thinking
                }
            }
        )

    @abstractmethod
    def _build_system_prompt(self):
        """构建系统提示"""
        raise NotImplementedError("子类必须实现_build_system_prompt方法")

    def ask(self, user_input: str):
        """向大模型提问"""
        system_prompt = self._build_system_prompt()
        human_message = HumanMessage(content=user_input)
        messages = [SystemMessage(content=system_prompt), human_message]
        start_time = time.time()
        logger.info(f"正在调用大模型，请稍候...")
        response = self._client.invoke(messages)
        logger.info(f"大模型响应时间：{time.time() - start_time}秒")
        return response.content


class JsonLLM[T](LLM):

    def __init__(self, max_retry: int = 3):
        super().__init__()
        self._max_retry = max_retry

    @abstractmethod
    def _get_json_schema(self) -> T:
        """获取JSON模式"""
        raise NotImplementedError("子类必须实现_get_json_schema方法")

    def ask(self, user_input: str) -> T:
        """向大模型提问，返回JSON对象"""
        system_prompt = self._build_system_prompt()
        error_msg = ""
        try_count = 0
        while try_count < self._max_retry:
            human_message = f"内容：\n{user_input}"
            if error_msg:
                human_message += f"\n错误信息：\n{error_msg}"
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_message)]
            try:
                start_time = time.time()
                logger.info(f"正在调用大模型，请稍候...")
                response = self._client.invoke(messages)
                logger.info(f"大模型响应时间：{time.time() - start_time}秒")
                response_content, obj = try_parse_json_object(response.content)
                constructor = self._get_json_schema()
                return constructor(**obj)
            except Exception as e:
                error_msg = str(e)
                try_count += 1
        return None
