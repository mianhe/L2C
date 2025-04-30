from enum import Enum
from typing import Dict, List


class CustomerSize(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    EXTRA_LARGE = "EXTRA_LARGE"

    @classmethod
    def get_options(cls) -> List[Dict[str, str]]:
        """获取所有选项，格式为前端需要的格式"""
        return [{"value": size.name, "label": size.name.replace("_", " ").title()} for size in cls]
