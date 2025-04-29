from app.mcp.errors import ErrorCode
from app.db.models import Customer
from app.config.options import CustomerSize


class TestMCPMetaInformation:
    """测试MCP服务的元数据和自描述能力
    这组测试验证MCP服务能够正确提供自身的元数据、工具列表和工具模式等信息，
    这些信息对客户端了解服务功能至关重要。
    """

    def test_metadata_endpoint_should_return_service_info(self, client):
        """验证元数据端点返回正确的服务信息"""
        # 发送请求
        response = client.get("/api/mcp/metadata")
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "name" in result
        assert "version" in result
        assert "tools" in result
        assert len(result["tools"]) > 0
        # 验证服务名称
        assert "L2C MCP Service" in result["name"]

    def test_list_tools_endpoint_should_return_available_tools(self, client):
        """验证工具列表端点返回所有可用工具"""
        # 构造请求
        request_data = {
            "tool": "list_tools",
            "parameters": {},
            "request_id": "test-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "tools" in result["data"]
        assert len(result["data"]["tools"]) > 0
        # 验证工具列表内容
        tool_names = [tool["name"] for tool in result["data"]["tools"]]
        assert "query" in tool_names
        assert "query_by_name" in tool_names
        assert "list_tools" in tool_names
        assert result["request_id"] == "test-123"

    def test_query_tool_schema_endpoint_should_return_complete_schema(self, client):
        """验证query工具模式端点返回完整的参数和返回值模式"""
        # 发送请求
        response = client.get("/api/mcp/tools/query")
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "query"
        assert "parameters" in result
        assert "customer_id" in result["parameters"]
        # 验证参数属性
        assert result["parameters"]["customer_id"]["required"] is True
        assert result["parameters"]["customer_id"]["type"] == "integer"
        assert "fields" in result["parameters"]
        # 验证返回值模式
        assert "returns" in result
        assert "properties" in result["returns"]
        assert "customer" in result["returns"]["properties"]

    def test_query_by_name_tool_schema_endpoint_should_return_complete_schema(self, client):
        """验证query_by_name工具模式端点返回完整的参数和返回值模式"""
        # 发送请求
        response = client.get("/api/mcp/tools/query_by_name")
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "query_by_name"
        assert "parameters" in result
        assert "customer_name" in result["parameters"]
        # 验证参数属性
        assert result["parameters"]["customer_name"]["required"] is True
        assert result["parameters"]["customer_name"]["type"] == "string"
        assert "fields" in result["parameters"]
        # 验证返回值模式
        assert "returns" in result
        assert "properties" in result["returns"]
        assert "customer" in result["returns"]["properties"]

    def test_invalid_tool_schema_endpoint_should_return_error(self, client):
        """验证请求不存在的工具模式时返回正确的错误信息"""
        # 发送请求
        response = client.get("/api/mcp/tools/invalid_tool")
        # 验证响应
        assert response.status_code == 404
        result = response.json()
        assert result["status"] == "error"
        assert result["error"]["code"] == ErrorCode.TOOL_NOT_FOUND


class TestMCPQueryById:
    """测试按ID查询客户的功能
    这组测试验证客户按ID查询功能的各个方面，包括成功查询、过滤字段、
    错误处理以及边界情况等。
    """

    def test_query_existing_customer_should_return_full_info(self, client, test_customer):
        """验证按ID查询存在的客户时返回完整客户信息"""
        # 使用test_customer夹具创建的客户数据
        customer_id = test_customer.id
        # 构造请求
        request_data = {
            "tool": "query",
            "parameters": {"customer_id": customer_id},
            "request_id": "test-real-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "customer" in result["data"]
        assert result["data"]["customer"]["name"] == "Test Customer"
        assert result["data"]["customer"]["city"] == "Test City"
        assert result["data"]["customer"]["industry"] == "Test Industry"
        assert result["request_id"] == "test-real-123"

    def test_query_with_field_filtering_should_return_only_selected_fields(self, client, test_customer):
        """验证使用fields参数可以只返回指定字段"""
        # 使用test_customer夹具创建的客户数据
        customer_id = test_customer.id
        # 构造请求 - 只获取城市信息
        request_data = {
            "tool": "query",
            "parameters": {
                "customer_id": customer_id,
                "fields": ["city"]
            },
            "request_id": "test-filter-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "customer" in result["data"]
        # 验证字段过滤
        assert "city" in result["data"]["customer"]
        assert "name" not in result["data"]["customer"]
        assert "industry" not in result["data"]["customer"]
        assert result["data"]["customer"]["city"] == "Test City"

    def test_query_nonexistent_customer_should_return_error(self, client):
        """验证查询不存在的客户ID时返回适当的错误信息"""
        # 使用一个不存在的客户ID
        non_existent_id = 9999
        # 构造请求
        request_data = {
            "tool": "query",
            "parameters": {"customer_id": non_existent_id},
            "request_id": "test-not-found-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 404
        result = response.json()
        assert result["status"] == "error"
        assert result["error"]["code"] == ErrorCode.CUSTOMER_NOT_FOUND
        assert "未找到客户" in result["error"]["message"]
        assert result["request_id"] == "test-not-found-123"

    def test_query_with_invalid_id_should_return_error(self, client):
        """验证使用无效的客户ID（如负数）时返回参数错误"""
        # 构造请求 - 使用无效的客户ID
        request_data = {
            "tool": "query",
            "parameters": {"customer_id": -1},
            "request_id": "test-invalid-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 400
        result = response.json()
        assert result["status"] == "error"
        assert result["error"]["code"] == ErrorCode.INVALID_PARAMETERS
        assert "客户ID必须是正整数" in result["error"]["message"]

    def test_query_multiple_customers_should_return_correct_info(self, client, db_session):
        """验证在存在多个客户时能正确查询指定ID的客户"""
        # 创建多个测试客户
        customers = []
        for i in range(3):
            customer = Customer(
                name=f"Customer {i+1}",
                city=f"City {i+1}",
                industry=f"Industry {i+1}",
                cargo_type=f"Cargo {i+1}",
                size=CustomerSize.MEDIUM
            )
            db_session.add(customer)
            customers.append(customer)
        db_session.commit()
        # 查询第二个客户
        customer_id = customers[1].id
        # 构造请求
        request_data = {
            "tool": "query",
            "parameters": {"customer_id": customer_id},
            "request_id": "test-multi-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "customer" in result["data"]
        assert result["data"]["customer"]["name"] == "Customer 2"


class TestMCPQueryByName:
    """测试按名称查询客户的功能
    这组测试验证客户按名称查询功能的各个方面，包括成功查询、过滤字段、
    错误处理以及边界情况等。
    """

    def test_query_by_name_existing_customer_should_return_full_info(self, client, test_customer):
        """验证按名称查询存在的客户时返回完整客户信息"""
        # 使用test_customer夹具创建的客户数据
        customer_name = test_customer.name
        # 构造请求
        request_data = {
            "tool": "query_by_name",
            "parameters": {"customer_name": customer_name},
            "request_id": "test-name-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "customer" in result["data"]
        assert result["data"]["customer"]["name"] == "Test Customer"
        assert result["data"]["customer"]["city"] == "Test City"
        assert result["data"]["customer"]["industry"] == "Test Industry"
        assert result["request_id"] == "test-name-123"

    def test_query_by_name_with_field_filtering_should_return_only_selected_fields(self, client, test_customer):
        """验证按名称查询时使用fields参数可以只返回指定字段"""
        # 使用test_customer夹具创建的客户数据
        customer_name = test_customer.name
        # 构造请求 - 只获取城市信息
        request_data = {
            "tool": "query_by_name",
            "parameters": {
                "customer_name": customer_name,
                "fields": ["city"]
            },
            "request_id": "test-name-filter-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "customer" in result["data"]
        # 验证字段过滤
        assert "city" in result["data"]["customer"]
        assert "name" not in result["data"]["customer"]
        assert "industry" not in result["data"]["customer"]
        assert result["data"]["customer"]["city"] == "Test City"
        assert result["request_id"] == "test-name-filter-123"

    def test_query_by_name_nonexistent_customer_should_return_error(self, client):
        """验证按名称查询不存在的客户时返回适当的错误信息"""
        # 使用一个不存在的客户名称
        non_existent_name = "非常不存在的客户名称XYZ123"
        # 构造请求
        request_data = {
            "tool": "query_by_name",
            "parameters": {"customer_name": non_existent_name},
            "request_id": "test-name-not-found-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 404
        result = response.json()
        assert result["status"] == "error"
        assert result["error"]["code"] == ErrorCode.CUSTOMER_NOT_FOUND
        assert "未找到客户" in result["error"]["message"]
        assert result["request_id"] == "test-name-not-found-123"

    def test_query_by_name_with_empty_name_should_return_error(self, client):
        """验证使用空字符串作为客户名称时返回参数错误"""
        # 构造请求 - 使用空名称
        request_data = {
            "tool": "query_by_name",
            "parameters": {"customer_name": ""},
            "request_id": "test-empty-name-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 400
        result = response.json()
        assert result["status"] == "error"
        assert result["error"]["code"] == ErrorCode.INVALID_PARAMETERS
        assert "客户名称不能为空" in result["error"]["message"]
        assert result["request_id"] == "test-empty-name-123"


class TestMCPErrorHandling:
    """测试MCP服务的错误处理功能
    这组测试验证MCP服务在遇到各种错误情况时能够正确处理并返回适当的错误信息。
    """

    def test_invalid_tool_should_return_tool_not_found_error(self, client):
        """验证使用不存在的工具名称时返回工具未找到错误"""
        # 构造请求 - 使用不存在的工具名称
        request_data = {
            "tool": "invalid_tool",
            "parameters": {},
            "request_id": "test-invalid-tool-123"
        }
        # 发送请求
        response = client.post("/api/mcp", json=request_data)
        # 验证响应
        assert response.status_code == 404
        result = response.json()
        assert result["status"] == "error"
        assert result["error"]["code"] == ErrorCode.TOOL_NOT_FOUND
        assert "未找到工具" in result["error"]["message"]
        assert result["request_id"] == "test-invalid-tool-123"
