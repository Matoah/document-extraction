from bs4 import BeautifulSoup
from knowledge.utils.token_util import count_tokens
import copy
import logging

logger = logging.getLogger(__name__)

def split_table_by_token_count(table_html: str, offset_count: int, token_count: int, max_token_count: int) -> list[str]:
    """根据表格内容大小，对表格内容进行拆分"""
    """
        将HTML表格按字符串数量拆分成多个表格。

        :param table_html: 包含单个<table>标签的HTML字符串
        :param offset_count: 偏移量
        :param min_strings: 每个拆分后表格应包含的最少字符串数量（最后一个可小于此值）
        :param max_strings: 每个拆分后表格允许的最大字符串数量
        :return: 拆分后的表格HTML字符串列表
        :raises ValueError: 当某行单元格数超过max_strings，或无法组成满足[min,max]的中间组时抛出
        """
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')
    if not table:
        raise ValueError("输入HTML中未找到<table>标签")

    # 获取所有行（保持原始顺序）
    rows = table.find_all('tr', recursive=True)
    if not rows:
        return [table_html]  # 空表格，无内容可拆分

    # 统计每行的字符串个数（即单元格数量）
    row_counts = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        count = count_tokens("".join([str(cell) for cell in cells]))
        if count > max_token_count:
            logger.warning(f"某行包含{count}个字符串，超过最大限制{max_token_count}")
        row_counts.append(count)

    # 贪心分组：每组的累计字符串数尽量接近max_strings，且中间组必须≥min_strings
    groups = []
    cur_group = []  # 当前组中的行对象列表
    cur_sum = offset_count  # 当前组累计字符串数

    for i, row in enumerate(rows):
        cnt = row_counts[i]
        if not cur_group:
            # 开始新组
            cur_group.append(row)
            cur_sum = cnt
        else:
            if cur_sum + cnt <= max_token_count:
                # 可以加入当前行
                cur_group.append(row)
                cur_sum += cnt
            else:
                # 当前组已满，检查是否满足最小要求
                if cur_sum < token_count:
                    logger.warning(f"无法形成满足条件的中间组：当前组总字符串数{cur_sum} < {token_count}，"
                        f"且加入下一行会超过{max_token_count}")
                groups.append(cur_group)
                # 开始新组
                cur_group = [row]
                cur_sum = cnt

    # 处理最后一组（允许其字符串数小于min_strings）
    if cur_group:
        groups.append(cur_group)

    # 为每组构建新的表格，保留原表格属性
    original_attrs = table.attrs
    result = []

    for group_rows in groups:
        # 创建新<table>，复制原表格属性
        new_table = soup.new_tag('table', **original_attrs)
        tbody = soup.new_tag('tbody')
        for row in group_rows:
            # 深拷贝行，避免多个表格共用同一节点
            row_copy = copy.deepcopy(row)
            tbody.append(row_copy)
        new_table.append(tbody)
        result.append(str(new_table))

    return result