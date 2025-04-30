from typing import Callable, Dict

from .protocol import ToolSchema

# 工具注册表
_tools: Dict[str, Callable] = {}


def register_tool(name: str, func: Callable) -> None:
    """注册工具"""
    _tools[name] = func


def get_tools() -> Dict[str, Callable]:
    """获取所有工具"""
    return _tools


def get_tool_schema(name: str, tool: Callable) -> ToolSchema:
    """获取工具模式"""
    # 这里需要根据实际工具的参数和返回值生成模式
    # 简化版本，实际使用时需要根据工具的具体实现来完善
    return ToolSchema(name=name, description=tool.__doc__ or "", parameters={}, returns={})
