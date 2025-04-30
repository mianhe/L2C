from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .errors import ErrorCode, MCPError


class ParameterSchema(BaseModel):
    """参数模式定义"""

    type: str
    description: str
    required: bool = False
    default: Any = None


class ToolSchema(BaseModel):
    """工具模式定义"""

    name: str
    description: str
    parameters: Dict[str, ParameterSchema]
    returns: Dict[str, Any]


class ServiceMetadata(BaseModel):
    """服务元数据定义"""

    name: str
    version: str
    description: str
    tools: List[ToolSchema]
    capabilities: List[str]


class MCPProtocol:
    """MCP 协议实现"""

    @staticmethod
    def parse_request(request: Dict[str, Any]) -> Dict[str, Any]:
        """解析请求"""
        if not request:
            raise MCPError(code=ErrorCode.INVALID_REQUEST, message="请求为空", status_code=400)

        tool = request.get("tool")
        if not tool:
            raise MCPError(
                code=ErrorCode.INVALID_REQUEST,
                message="缺少工具名称",
                details={"required_field": "tool"},
                status_code=400,
            )

        return {"tool": tool, "parameters": request.get("parameters", {}), "request_id": request.get("request_id")}

    @staticmethod
    def format_response(response: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """格式化响应"""
        return {"status": "success", "data": response, "request_id": request_id}

    @staticmethod
    def format_error(error: MCPError, request_id: Optional[str] = None) -> Dict[str, Any]:
        """格式化错误响应"""
        return {"status": "error", "error": error.to_dict(), "request_id": request_id}

    @staticmethod
    def format_exception(e: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
        """格式化异常为错误响应"""
        if isinstance(e, MCPError):
            return MCPProtocol.format_error(e, request_id)

        # 未知错误处理
        return {
            "status": "error",
            "error": {"code": ErrorCode.INTERNAL_ERROR, "message": str(e)},
            "request_id": request_id,
        }
