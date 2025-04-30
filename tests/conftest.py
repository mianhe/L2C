# Standard library imports
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import text

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# 设置测试环境变量 (这必须在导入任何应用模块之前)
os.environ["TESTING"] = "1"

from app.config.options import CustomerSize  # noqa: E402

# 以下导入必须在设置环境变量和Python路径之后
# 这是一个有效的例外，因为这些模块依赖于上面的配置
from app.db.database import SessionLocal, engine, set_test_db  # noqa: E402
from app.db.models import Base, Customer  # noqa: E402

# 创建表结构
Base.metadata.create_all(bind=engine)

# 创建测试会话
test_session = SessionLocal()

# 设置测试数据库会话
set_test_db(test_session)

from fastapi.testclient import TestClient  # noqa: E402

# 导入 FastAPI 应用 (必须在设置测试数据库后)
from main import app  # noqa: E402


# 每个测试开始前清空所有表
@pytest.fixture(autouse=True)
def clean_db():
    """清空测试数据库中的所有表数据"""
    # 提交现有事务
    test_session.commit()

    # 删除所有表中的数据
    test_session.execute(text("DELETE FROM customers"))

    # 尝试重置自增ID (如果存在)
    try:
        test_session.execute(text("DELETE FROM sqlite_sequence WHERE name='customers'"))
    except Exception:
        pass

    # 提交删除操作
    test_session.commit()
    yield
    # 测试结束回滚
    test_session.rollback()


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """提供数据库会话"""
    test_session.commit()  # 确保会话干净
    try:
        yield test_session
    finally:
        test_session.rollback()  # 回滚任何未提交的更改


@pytest.fixture
def test_customer(db_session):
    """创建测试客户数据"""
    customer = Customer(
        name="Test Customer",
        city="Test City",
        industry="Test Industry",
        cargo_type="Test Cargo",
        size=CustomerSize.SMALL,
    )
    db_session.add(customer)
    db_session.commit()
    return customer
