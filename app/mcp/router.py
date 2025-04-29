from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .protocol import MCPProtocol
from .service import MCPService
from .errors import MCPError, ToolNotFoundError


router = APIRouter(prefix="/api/mcp", tags=["mcp"])


@router.post("")
async def handle_mcp_request(request: Request):
    """处理 MCP 请求"""
    request_id = None
    try:
        # 解析请求
        request_data = await request.json()
        parsed_request = MCPProtocol.parse_request(request_data)

        # 获取工具名称和参数
        tool_name = parsed_request["tool"]
        parameters = parsed_request["parameters"]
        request_id = parsed_request["request_id"]

        # 根据工具名称调用相应的服务方法
        if tool_name == "query":
            response = MCPService.query_customer(
                customer_id=parameters.get("customer_id"), fields=parameters.get("fields")
            )
        elif tool_name == "query_by_name":
            response = MCPService.query_customer_by_name(
                customer_name=parameters.get("customer_name"), fields=parameters.get("fields")
            )
        elif tool_name == "list_tools":
            response = MCPService.list_tools()
        else:
            return JSONResponse(
                status_code=404, content=MCPProtocol.format_error(ToolNotFoundError(tool_name), request_id)
            )

        # 格式化并返回响应
        return JSONResponse(content=MCPProtocol.format_response(response, request_id))
    except MCPError as e:
        # 处理已知的MCP错误
        return JSONResponse(status_code=e.status_code, content=MCPProtocol.format_error(e, request_id))
    except Exception as e:
        # 处理未知错误
        return JSONResponse(status_code=500, content=MCPProtocol.format_exception(e, request_id))


@router.get("/metadata")
async def get_metadata():
    """获取服务元数据"""
    try:
        return MCPService.get_service_metadata()
    except MCPError as e:
        return JSONResponse(status_code=e.status_code, content=MCPProtocol.format_error(e, None))
    except Exception as e:
        return JSONResponse(status_code=500, content=MCPProtocol.format_exception(e, None))


@router.get("/tools/{tool_name}")
async def get_tool_schema(tool_name: str):
    """获取指定工具的详细模式"""
    try:
        return MCPService.get_tool_schema(tool_name)
    except ToolNotFoundError as e:
        return JSONResponse(status_code=e.status_code, content=MCPProtocol.format_error(e, None))
    except Exception as e:
        return JSONResponse(status_code=500, content=MCPProtocol.format_exception(e, None))
