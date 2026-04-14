import tiktoken
encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """统计Token数量"""
    if text is None or text == "":
        return 0
    try:
        return len(encoder.encode(text))
    except Exception:
        return 0