import re

def resolve_date(date_str: str) -> str:
    """解析日期字符串, 格式为：yyyy-MM-dd"""
    date_str = date_str.replace(" ","")
    if "-" in date_str:
        return date_str
    # 转换yyyy年MM月dd日格式
    match = re.search(r"(\d{4})年(\d{2})月(\d{2})日", date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return date_str