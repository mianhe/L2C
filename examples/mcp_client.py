import uuid
from typing import Any, Dict, List, Optional

import requests


class MCPClient:
    """MCP 客户端实现"""

    def __init__(self, server_url: str):
        """
        初始化MCP客户端

        参数:
            server_url (str): MCP服务器URL，如 http://localhost:8000
        """
        self.server_url = server_url.rstrip("/")
        self.api_endpoint = f"{self.server_url}/api/mcp"

    def _generate_request_id(self) -> str:
        """生成唯一请求ID"""
        return str(uuid.uuid4())

    def _call_api(self, tool: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调用API

        参数:
            tool (str): 工具名称
            parameters (Optional[Dict[str, Any]]): 工具参数

        返回:
            Dict[str, Any]: API响应

        抛出:
            Exception: 如果API调用失败
        """
        request_id = self._generate_request_id()
        request_data = {"tool": tool, "parameters": parameters or {}, "request_id": request_id}

        response = requests.post(self.api_endpoint, json=request_data)

        response_data = response.json()

        # 检查响应状态
        if response.status_code >= 400 or response_data.get("status") == "error":
            error = response_data.get("error", {})
            error_code = error.get("code", "UNKNOWN_ERROR")
            error_message = error.get("message", "Unknown error occurred")
            raise Exception(f"API错误: {error_code} - {error_message}")

        return response_data.get("data", {})

    def query_customer(self, customer_id: int, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询客户信息

        参数:
            customer_id (int): 客户ID
            fields (Optional[List[str]]): 需要返回的字段列表

        返回:
            Dict[str, Any]: 客户信息
        """
        parameters: Dict[str, Any] = {"customer_id": customer_id}
        if fields:
            parameters["fields"] = fields

        return self._call_api("query", parameters)

    def query_customer_by_name(self, customer_name: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """按名称查询客户信息

        参数:
            customer_name (str): 客户名称
            fields (Optional[List[str]]): 需要返回的字段列表

        返回:
            Dict[str, Any]: 客户信息
        """
        parameters: Dict[str, Any] = {"customer_name": customer_name}
        if fields:
            parameters["fields"] = fields

        return self._call_api("query_by_name", parameters)

    def list_tools(self) -> List[Dict[str, str]]:
        """获取可用工具列表

        返回:
            List[Dict[str, str]]: 工具列表
        """
        result = self._call_api("list_tools")
        tools: List[Dict[str, str]] = result.get("tools", [])
        return tools

    def get_service_metadata(self) -> Dict[str, Any]:
        """获取服务元数据

        返回:
            Dict[str, Any]: 服务元数据
        """
        response = requests.get(f"{self.api_endpoint}/metadata")

        if response.status_code >= 400:
            raise Exception(f"获取元数据失败: HTTP {response.status_code}")

        return response.json()

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """获取工具模式

        参数:
            tool_name (str): 工具名称

        返回:
            Dict[str, Any]: 工具模式
        """
        response = requests.get(f"{self.api_endpoint}/tools/{tool_name}")

        if response.status_code >= 400:
            response_data = response.json()
            error = response_data.get("error", {})
            error_message = error.get("message", f"获取工具'{tool_name}'模式失败")
            raise Exception(error_message)

        return response.json()


# 使用示例
if __name__ == "__main__":
    # 创建客户端实例
    client = MCPClient("http://localhost:8000")

    try:
        # 获取服务元数据
        metadata = client.get_service_metadata()
        print("服务信息:")
        print(f"  名称: {metadata['name']}")
        print(f"  版本: {metadata['version']}")
        print(f"  描述: {metadata['description']}")
        print()

        # 获取工具列表
        tools = client.list_tools()
        print("可用工具:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        print()

        # 尝试按ID查询客户
        try:
            customer_id = 1  # 使用实际存在的客户ID
            customer_data = client.query_customer(customer_id)
            print("客户信息(按ID查询):")
            for key, value in customer_data.get("customer", {}).items():
                print(f"  {key}: {value}")
            print()
        except Exception as e:
            print(f"按ID查询出错: {str(e)}")
            print()

        # 尝试按名称查询客户
        try:
            customer_name = "Test Customer"  # 使用实际存在的客户名称
            customer_data = client.query_customer_by_name(customer_name)
            print("客户信息(按名称查询):")
            for key, value in customer_data.get("customer", {}).items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"按名称查询出错: {str(e)}")

    except Exception as e:
        print(f"错误: {str(e)}")
