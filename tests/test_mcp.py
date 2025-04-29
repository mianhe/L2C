import pytest
from app.mcp.service import MCPService
from app.mcp.protocol import MCPProtocol
from app.mcp.errors import CustomerNotFoundError, ToolNotFoundError, InvalidParametersError, DatabaseError
from app.db.models import Customer
from app.config.options import CustomerSize
from unittest.mock import MagicMock

class TestMCPEdgeCases:
    """MCP 边缘情况和异常处理测试"""
    
    def test_query_customer_invalid_id(self):
        """测试无效的客户ID - 验证参数校验逻辑，接口测试难以全面覆盖边界值"""
        # 直接使用无效ID调用方法
        with pytest.raises(InvalidParametersError) as excinfo:
            MCPService.query_customer(customer_id=-1)
        
        # 验证异常
        assert "客户ID必须是正整数" in str(excinfo.value)
        assert excinfo.value.code == "INVALID_PARAMETERS"
    
    def test_query_customer_by_name_with_empty_name(self):
        """测试使用空名称查询客户 - 验证边界情况的处理"""
        # 使用空名称调用方法，应该抛出异常
        with pytest.raises(InvalidParametersError) as excinfo:
            MCPService.query_customer_by_name(customer_name="")
        
        # 验证异常
        assert "客户名称不能为空" in str(excinfo.value)
        assert excinfo.value.code == "INVALID_PARAMETERS"
    
    def test_query_customer_db_error(self, monkeypatch):
        """测试数据库错误 - 模拟数据库连接失败，接口测试难以模拟此场景"""
        # 创建模拟数据库会话
        mock_db = MagicMock()
        mock_db._is_test_db = True  # 避免关闭连接
        mock_db.query.side_effect = Exception("database connection error")
        
        # 模拟 get_db 生成器
        def mock_get_db():
            yield mock_db
        
        # 应用补丁
        monkeypatch.setattr("app.mcp.service.get_db", mock_get_db)
        
        # 执行查询，应该抛出异常
        with pytest.raises(DatabaseError) as excinfo:
            MCPService.query_customer(customer_id=1)
        
        # 验证异常
        assert "数据库操作失败" in str(excinfo.value)
        assert excinfo.value.code == "DATABASE_ERROR"


class TestMCPProtocol:
    """MCP 协议测试 - 测试协议解析和格式化逻辑，独立于接口实现"""
    
    def test_parse_request_success(self):
        """测试解析请求成功"""
        # 构造请求
        request = {
            "tool": "query",
            "parameters": {"customer_id": 1},
            "request_id": "test-123"
        }
        
        # 解析请求
        result = MCPProtocol.parse_request(request)
        
        # 验证结果
        assert result["tool"] == "query"
        assert result["parameters"]["customer_id"] == 1
        assert result["request_id"] == "test-123"
    
    def test_parse_request_missing_tool(self):
        """测试解析缺少工具名称的请求"""
        # 构造请求
        request = {
            "parameters": {"customer_id": 1},
            "request_id": "test-123"
        }
        
        # 解析请求，应该抛出异常
        with pytest.raises(Exception) as excinfo:
            MCPProtocol.parse_request(request)
        
        # 验证异常
        assert "缺少工具名称" in str(excinfo.value)
    
    def test_format_response(self):
        """测试格式化响应"""
        # 构造数据
        data = {"customer": {"id": 1, "name": "测试客户"}}
        request_id = "test-123"
        
        # 格式化响应
        result = MCPProtocol.format_response(data, request_id)
        
        # 验证结果
        assert result["status"] == "success"
        assert result["data"] == data
        assert result["request_id"] == request_id 