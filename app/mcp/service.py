from typing import Any, Dict, List, Optional

from app.db.database import get_db
from app.db.models import Customer

from .errors import CustomerNotFoundError, DatabaseError, InternalServerError, InvalidParametersError, ToolNotFoundError
from .protocol import ParameterSchema, ServiceMetadata, ToolSchema


class MCPService:
    """MCP 服务实现"""

    # 服务元数据
    SERVICE_METADATA = ServiceMetadata(
        name="L2C MCP Service",
        version="1.0.0",
        description="L2C 系统的 MCP 服务，提供客户管理和查询功能",
        tools=[
            ToolSchema(
                name="query",
                description="查询客户信息",
                parameters={
                    "customer_id": ParameterSchema(type="integer", description="客户ID", required=True),
                    "fields": ParameterSchema(
                        type="array",
                        description="需要返回的字段列表",
                        required=False,
                        default=["name", "city", "industry"],
                    ),
                },
                returns={
                    "type": "object",
                    "properties": {
                        "customer": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "city": {"type": "string"},
                                "industry": {"type": "string"},
                            },
                        }
                    },
                },
            ),
            ToolSchema(
                name="query_by_name",
                description="按名称查询客户信息",
                parameters={
                    "customer_name": ParameterSchema(type="string", description="客户名称", required=True),
                    "fields": ParameterSchema(
                        type="array",
                        description="需要返回的字段列表",
                        required=False,
                        default=["name", "city", "industry"],
                    ),
                },
                returns={
                    "type": "object",
                    "properties": {
                        "customer": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "city": {"type": "string"},
                                "industry": {"type": "string"},
                            },
                        }
                    },
                },
            ),
            ToolSchema(
                name="list_tools",
                description="获取可用工具列表",
                parameters={},
                returns={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "description": {"type": "string"}},
                    },
                },
            ),
        ],
        capabilities=["customer_query", "customer_management"],
    )

    @staticmethod
    def get_service_metadata() -> Dict[str, Any]:
        """获取服务元数据"""
        try:
            return MCPService.SERVICE_METADATA.model_dump()
        except Exception as e:
            raise InternalServerError(f"获取服务元数据失败: {str(e)}")

    @staticmethod
    def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
        """获取指定工具的详细模式"""
        for tool in MCPService.SERVICE_METADATA.tools:
            if tool.name == tool_name:
                return tool.model_dump()
        raise ToolNotFoundError(tool_name)

    @staticmethod
    def query_customer(customer_id: int, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询客户信息"""
        try:
            # 验证参数
            if not isinstance(customer_id, int) or customer_id <= 0:
                raise InvalidParametersError("客户ID必须是正整数", {"customer_id": customer_id})

            # 获取数据库会话
            db = next(get_db())
            try:
                # 从数据库查询客户信息
                customer_db = db.query(Customer).filter(Customer.id == customer_id).first()

                # 如果客户不存在，抛出异常
                if not customer_db:
                    raise CustomerNotFoundError(customer_id)

                # 将 SQLAlchemy 模型转换为字典
                customer = {
                    "id": customer_db.id,
                    "name": customer_db.name,
                    "city": customer_db.city,
                    "industry": customer_db.industry,
                    "cargo_type": customer_db.cargo_type,
                    "size": str(customer_db.size),
                }

                # 如果指定了字段，只返回这些字段
                if fields is None:
                    fields = ["name", "city", "industry"]
                result = {}
                for field in fields:
                    if field in customer:
                        result[field] = customer[field]
                return {"customer": result}
            finally:
                # 确保会话关闭（非测试环境下）
                if getattr(db, "_is_test_db", False) is False:
                    db.close()
        except CustomerNotFoundError:
            # 直接抛出，不需要额外包装
            raise
        except InvalidParametersError:
            # 直接抛出，不需要额外包装
            raise
        except Exception as e:
            # 其他未知异常，包装为数据库错误或内部错误
            if "database" in str(e).lower() or "db" in str(e).lower() or "sql" in str(e).lower():
                raise DatabaseError(f"查询客户数据库操作失败: {str(e)}")
            raise InternalServerError(f"查询客户时出错: {str(e)}")

    @staticmethod
    def query_customer_by_name(customer_name: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """按名称查询客户信息"""
        try:
            # 验证参数
            if not customer_name or not isinstance(customer_name, str):
                raise InvalidParametersError("客户名称不能为空", {"customer_name": customer_name})

            # 获取数据库会话
            db = next(get_db())
            try:
                # 从数据库查询客户信息（支持模糊匹配）
                customer_db = db.query(Customer).filter(Customer.name == customer_name).first()

                # 如果客户不存在，抛出异常
                if not customer_db:
                    raise CustomerNotFoundError(customer_name, param_name="customer_name")

                # 将 SQLAlchemy 模型转换为字典
                customer = {
                    "id": customer_db.id,
                    "name": customer_db.name,
                    "city": customer_db.city,
                    "industry": customer_db.industry,
                    "cargo_type": customer_db.cargo_type,
                    "size": str(customer_db.size),
                }

                # 如果指定了字段，只返回这些字段
                if fields is None:
                    fields = ["name", "city", "industry"]
                result = {}
                for field in fields:
                    if field in customer:
                        result[field] = customer[field]
                return {"customer": result}
            finally:
                # 确保会话关闭（非测试环境下）
                if getattr(db, "_is_test_db", False) is False:
                    db.close()
        except CustomerNotFoundError:
            # 直接抛出，不需要额外包装
            raise
        except InvalidParametersError:
            # 直接抛出，不需要额外包装
            raise
        except Exception as e:
            # 其他未知异常，包装为数据库错误或内部错误
            if "database" in str(e).lower() or "db" in str(e).lower() or "sql" in str(e).lower():
                raise DatabaseError(f"查询客户数据库操作失败: {str(e)}")
            raise InternalServerError(f"查询客户时出错: {str(e)}")

    @staticmethod
    def list_tools() -> Dict[str, Any]:
        """获取可用工具列表"""
        try:
            tools = []
            for tool in MCPService.SERVICE_METADATA.tools:
                tools.append({"name": tool.name, "description": tool.description})
            return {"tools": tools}
        except Exception as e:
            raise InternalServerError(f"获取工具列表失败: {str(e)}")
