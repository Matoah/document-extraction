import time
import logging
from requests import post as post_request, get as get_request, delete as delete_request, Response

logger = logging.getLogger(__name__)

post_request_time = {}

get_request_time = {}

delete_request_time = {}

def wait_until_valid(url: str, pool: dict):
    """等待当前url可请求,避免被服务识别成CC攻击（同一个请求60s内请求超过120次）"""
    now_time = time.time()
    if url in pool:
        pre_time = pool[url]
        if now_time - pre_time > 1:
            pool[url] = now_time
        else:
            logger.info(f"请求{url}过于频繁，将等待1s后发起请求...")
            time.sleep(1)
            now_time = time.time()
            pool[url] = now_time
    else:
        now_time = time.time()
        pool[url] = now_time

def post(url: str, **kwargs)->Response:
    """POST请求"""
    wait_until_valid(url, post_request_time)
    response = post_request(url, **kwargs)
    response.raise_for_status()
    return response

def get(url: str, **kwargs) -> Response:
    """GET请求"""
    wait_until_valid(url, get_request_time)
    response = get_request(url, **kwargs)
    response.raise_for_status()
    return response

def delete(url: str, **kwargs) -> Response:
    """DELETE请求"""
    wait_until_valid(url, delete_request_time)
    response = delete_request(url, **kwargs)
    response.raise_for_status()
    return response