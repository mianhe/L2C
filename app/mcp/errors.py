from enum import Enum
from typing import Dict, Any, Optional


class ErrorCode(str, Enum):
    """错误代码"""

    # 通用错误
    INVALID_REQUEST = "INVALID_REQUEST"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    INVALID_PARAMETERS = "INVALID_PARAMETERS"
    # 业务错误
    CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"


class MCPError(Exception):
    """MCP 错误基类"""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 500):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {"code": self.code, "message": self.message, "details": self.details}


class InvalidRequestError(MCPError):
    """无效请求错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(code=ErrorCode.INVALID_REQUEST, message=message, details=details, status_code=400)


class InternalServerError(MCPError):
    """内部服务器错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(code=ErrorCode.INTERNAL_ERROR, message=message, details=details, status_code=500)


class InvalidParametersError(MCPError):
    """无效参数错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(code=ErrorCode.INVALID_PARAMETERS, message=message, details=details, status_code=400)


class CustomerNotFoundError(MCPError):
    """客户未找到错误"""

    def __init__(self, value: Any, param_name: str = "customer_id"):
        details = {param_name: value}
        message = f"未找到客户: {param_name.replace('_', ' ').title()}={value}"
        super().__init__(code=ErrorCode.CUSTOMER_NOT_FOUND, message=message, details=details, status_code=404)


class ToolNotFoundError(MCPError):
    """工具未找到错误"""

    def __init__(self, tool_name: str):
        super().__init__(
            code=ErrorCode.TOOL_NOT_FOUND,
            message=f"未找到工具: {tool_name}",
            details={"tool_name": tool_name},
            status_code=404,
        )


class DatabaseError(MCPError):
    """数据库错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(code=ErrorCode.DATABASE_ERROR, message=message, details=details, status_code=500)
