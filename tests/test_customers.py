import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# 以下导入必须在设置Python路径之后
from app.config.options import CustomerSize  # noqa: E402
from app.db.models import Customer  # noqa: E402


class TestSizeOptions:
    """测试客户规模选项相关的接口"""

    def test_get_size_options_should_return_all_options(self, client):
        """测试获取客户规模选项接口"""
        # 发送请求
        response = client.get("/api/customers/size-options/")
        # 验证响应状态码
        assert response.status_code == 200, "响应状态码应为 200"
        # 解析响应数据
        data = response.json()
        # 验证响应格式
        assert "options" in data, "响应应包含 options 字段"
        assert isinstance(data["options"], list), "options 应为列表"
        # 验证选项数量
        assert len(data["options"]) == len(CustomerSize), "选项数量应与枚举成员数量一致"
        # 验证每个选项
        for option in data["options"]:
            assert "value" in option, "选项应包含 value 字段"
            assert "label" in option, "选项应包含 label 字段"
            assert option["value"] in CustomerSize.__members__, f"选项值 {option['value']} 应在枚举定义中"


class TestCustomerCreate:
    """测试创建客户相关的接口"""

    def test_create_customer_with_valid_data_should_succeed(self, client, db_session):
        """测试使用有效数据创建客户应该成功"""
        # 准备测试数据
        customer_data = {
            "name": "Test Customer",
            "city": "Test City",
            "industry": "Test Industry",
            "cargo_type": "Test Cargo",
            "size": "SMALL"
        }
        # 发送请求
        response = client.post("/api/customers/", json=customer_data)
        # 验证响应
        assert response.status_code == 200, "响应状态码应为 200"
        data = response.json()
        # 验证返回数据
        assert data["name"] == customer_data["name"]
        assert data["city"] == customer_data["city"]
        assert data["industry"] == customer_data["industry"]
        assert data["cargo_type"] == customer_data["cargo_type"]
        assert data["size"] == customer_data["size"]
        assert "id" in data, "返回数据应包含 id 字段"
        # 验证数据库
        customer = db_session.query(Customer).filter(Customer.id == data["id"]).first()
        assert customer is not None, "客户应存在于数据库中"
        assert customer.name == customer_data["name"]

    def test_create_customer_with_invalid_size_should_fail(self, client):
        """测试使用无效的 size 值创建客户应该失败"""
        customer_data = {
            "name": "Test Customer",
            "city": "Test City",
            "industry": "Test Industry",
            "cargo_type": "Test Cargo",
            "size": "INVALID_SIZE"
        }
        response = client.post("/api/customers/", json=customer_data)
        assert response.status_code == 422, "使用无效的 size 值应返回 422 错误"

    def test_create_customer_with_missing_fields_should_fail(self, client):
        """测试缺少必填字段创建客户应该失败"""
        customer_data = {
            "name": "Test Customer",
            # 缺少 city 字段
            "industry": "Test Industry",
            "cargo_type": "Test Cargo",
            "size": "SMALL"
        }
        response = client.post("/api/customers/", json=customer_data)
        assert response.status_code == 422, "缺少必填字段应返回 422 错误"


class TestCustomerList:
    """测试获取客户列表相关的接口"""

    def test_get_customer_list_should_return_all_customers(self, client, db_session):
        """测试获取客户列表应该返回所有客户"""
        # 创建测试数据
        customers = [
            Customer(
                name="Customer 1",
                city="City 1",
                industry="Industry 1",
                cargo_type="Cargo 1",
                size=CustomerSize.SMALL
            ),
            Customer(
                name="Customer 2",
                city="City 2",
                industry="Industry 2",
                cargo_type="Cargo 2",
                size=CustomerSize.MEDIUM
            )
        ]
        for customer in customers:
            db_session.add(customer)
        db_session.commit()
        response = client.get("/api/customers/")
        # 验证响应状态码
        assert response.status_code == 200, "响应状态码应为 200"
        # 解析响应数据
        data = response.json()
        # 验证响应格式
        assert isinstance(data, list), "响应应为列表"
        assert len(data) == len(customers), "返回的客户数量应与数据库中的数量一致"
        # 验证每个客户的数据
        for customer_data in data:
            assert "id" in customer_data, "客户数据应包含 id 字段"
            assert "name" in customer_data, "客户数据应包含 name 字段"
            assert "city" in customer_data, "客户数据应包含 city 字段"
            assert "industry" in customer_data, "客户数据应包含 industry 字段"
            assert "cargo_type" in customer_data, "客户数据应包含 cargo_type 字段"
            assert "size" in customer_data, "客户数据应包含 size 字段"

    def test_get_empty_customer_list_should_return_empty_list(self, client):
        """测试获取空客户列表应该返回空列表"""
        response = client.get("/api/customers/")
        # 验证响应状态码
        assert response.status_code == 200, "响应状态码应为 200"
        # 解析响应数据
        data = response.json()
        # 验证响应格式
        assert isinstance(data, list), "响应应为列表"
        assert len(data) == 0, "空列表应返回空列表"


class TestCustomerDetail:
    """测试获取单个客户详情相关的接口"""

    def test_get_existing_customer_should_succeed(self, client, db_session):
        """测试获取已存在的客户详情应该成功"""
        # 创建测试数据
        customer = Customer(
            name="Test Customer",
            city="Test City",
            industry="Test Industry",
            cargo_type="Test Cargo",
            size=CustomerSize.SMALL
        )
        db_session.add(customer)
        db_session.commit()
        # 发送请求
        response = client.get(f"/api/customers/{customer.id}")
        # 验证响应状态码
        assert response.status_code == 200, "响应状态码应为 200"
        # 解析响应数据
        data = response.json()
        # 验证返回数据
        assert data["id"] == customer.id
        assert data["name"] == customer.name
        assert data["city"] == customer.city
        assert data["industry"] == customer.industry
        assert data["cargo_type"] == customer.cargo_type
        assert data["size"] == customer.size.value

    def test_get_nonexistent_customer_should_fail(self, client):
        """测试获取不存在的客户详情应该失败"""
        # 发送请求
        response = client.get("/api/customers/99999")
        # 验证响应状态码
        assert response.status_code == 404, "响应状态码应为 404"
        # 验证错误信息
        data = response.json()
        assert "detail" in data, "响应应包含 detail 字段"
        assert data["detail"] == "Customer not found"

    def test_get_customer_with_invalid_id_should_fail(self, client):
        """测试使用无效的ID获取客户详情应该失败"""
        # 发送请求
        response = client.get("/api/customers/invalid_id")
        # 验证响应状态码
        assert response.status_code == 422, "使用无效的ID应返回422错误"


class TestCustomerUpdate:
    """测试更新客户信息相关的接口"""

    def test_update_existing_customer_should_succeed(self, client, db_session):
        """测试更新已存在的客户信息应该成功"""
        # 创建测试数据
        customer = Customer(
            name="Test Customer",
            city="Test City",
            industry="Test Industry",
            cargo_type="Test Cargo",
            size=CustomerSize.SMALL
        )
        db_session.add(customer)
        db_session.commit()
        # 发送请求
        response = client.put(f"/api/customers/{customer.id}", json={
            "name": "Updated Customer",
            "city": "Updated City",
            "industry": "Updated Industry",
            "cargo_type": "Updated Cargo",
            "size": "MEDIUM"
        })
        # 验证响应
        assert response.status_code == 200, "响应状态码应为 200"
        data = response.json()
        # 验证返回数据
        assert data["id"] == customer.id
        assert data["name"] == "Updated Customer"
        assert data["city"] == "Updated City"
        assert data["industry"] == "Updated Industry"
        assert data["cargo_type"] == "Updated Cargo"
        assert data["size"] == "MEDIUM"

    def test_update_nonexistent_customer_should_fail(self, client):
        """测试更新不存在的客户信息应该失败"""
        # 发送请求
        response = client.put("/api/customers/99999", json={
            "name": "Updated Customer",
            "city": "Updated City",
            "industry": "Updated Industry",
            "cargo_type": "Updated Cargo",
            "size": "MEDIUM"
        })
        # 验证响应
        assert response.status_code == 404, "响应状态码应为 404"
        # 验证错误信息
        data = response.json()
        assert "detail" in data, "响应应包含 detail 字段"
        assert data["detail"] == "Customer not found"


class TestCustomerDelete:
    """测试删除客户相关的接口"""

    def test_delete_existing_customer_should_succeed(self, client, db_session):
        """测试删除已存在的客户应该成功"""
        # 创建测试数据
        customer = Customer(
            name="Test Customer",
            city="Test City",
            industry="Test Industry",
            cargo_type="Test Cargo",
            size=CustomerSize.SMALL
        )
        db_session.add(customer)
        db_session.commit()
        # 发送请求
        response = client.delete(f"/api/customers/{customer.id}")
        # 验证响应
        assert response.status_code == 200, "响应状态码应为 200"
        data = response.json()
        # 验证返回数据
        assert data["id"] == customer.id
        assert data["name"] == customer.name


class TestCustomerListQuery:
    """测试客户列表的查询参数相关的接口"""
    pass


class TestCustomerListSort:
    """测试客户列表的排序相关的接口"""
    pass


class TestCustomerDataValidation:
    """测试客户数据的验证相关的接口"""
    pass


class TestCustomerConcurrency:
    """测试客户并发操作相关的接口"""
    pass


class TestCustomerPerformance:
    """测试客户操作性能相关的接口"""
    pass
