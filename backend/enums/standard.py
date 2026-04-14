from enum import Enum


class StandardNature(str, Enum):
    """标准规范性质"""

    MANDATORY = "强制性标准"

    RECOMMENDED = "推荐性标准"
