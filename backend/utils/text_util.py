import json
import logging
import re
from json_repair import repair_json

logger = logging.getLogger(__name__)

def try_parse_json_object(text: str, verbose: bool = True) -> tuple[str, dict]:
    """
    尝试解析 JSON 字符串。

    Args
    ----
        text: str
            要解析的 JSON 字符串。
        verbose: bool, optional
            是否打印详细日志。默认值为 True。

    Returns
    -------
        生成器，生成解析后的 JSON 字符串和字典。
    """
    #是否以<think>开头
    if text.startswith("<think>"):
        #找到最后一个</think>位置
        text = text[len("<think>"):]
        try:
            index = text.rindex("</think>")
            text = text[index+8:]
        except ValueError:
            pass

    result = None
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        if verbose:
            logger.warning("解析json字符串失败，尝试修复")

    if result:
        return text, result

    pattern = r"\{(.*)\}"
    match = re.search(pattern, text, re.DOTALL)
    text = "{" + match.group(1) + "}" if match else text

    # Clean up json string.
    text = (
        text
        .replace("{{", "{")
        .replace("}}", "}")
        .replace('"[{', "[{")
        .replace('}]"', "}]")
        .replace("\\", " ")
        .replace("\\n", " ")
        .replace("\n", " ")
        .replace("\r", "")
        .strip()
    )

    if text.startswith("```json"):
        text = text[len("```json"):]
    if text.endswith("```"):
        text = text[: len(text) - len("```")]

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        text = str(repair_json(json_str=text, return_objects=False))

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            if verbose:
                logger.exception("解析json字符串失败，json=%s", text)
            return text, {}
        else:
            if not isinstance(result, dict):
                if verbose:
                    logger.exception("解析json字符串失败，json=%s:", type(result))
                return text, {}
            return text, result
    else:
        return text, result