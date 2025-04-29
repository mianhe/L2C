# L2C (Leads to Cash) System
![Python Tests](https://github.com/mianhe/L2C/actions/workflows/python-test.yml/badge.svg)

一个用于物流软件销售过程的客户管理系统，提供客户信息查询和机器控制协议(MCP)接口。

## 主要特性

- **客户信息管理**：存储和管理客户的基本信息、需求和互动历史
- **MCP协议支持**：通过统一的协议接口支持工具调用，便于系统集成
- 特性持续开发中

## 技术栈
- **后端框架**：FastAPI
- **数据库**：SQLite/SQLAlchemy
- **文档生成**：自定义docstring文档生成器
- **测试框架**：Pytest

## 安装和设置

1. 克隆仓库：
```bash
git clone https://github.com/mianhe/L2C.git
cd L2C
```
2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows系统: venv\Scripts\activate
```
3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
uvicorn main:app --reload
```

应用将在 http://localhost:8000 上运行。

## 开发指南

### 代码质量和CI

本项目使用GitHub Actions进行持续集成，包括以下检查：

- **单元测试**：使用pytest运行所有测试
- **代码覆盖率**：要求至少75%的代码覆盖率
- **代码风格**：使用black和flake8检查代码风格
- **类型检查**：使用mypy进行静态类型检查

### 本地开发工具

1. 安装开发依赖：
```bash
pip install -r requirements-dev.txt
```

2. 安装pre-commit钩子：
```bash
pre-commit install
```

3. 运行测试和代码覆盖率检查：
```bash
pytest --cov=app
```

4. 查看HTML格式的覆盖率报告：
```bash
pytest --cov=app --cov-report=html
# 然后打开 htmlcov/index.html
```

### 主干开发流程

本项目采用主干开发(Trunk-Based Development)流程：

1. 所有开发直接在`main`分支进行
2. 每次提交前运行测试确保不破坏现有功能
3. 使用特性标记(Feature Flags)控制未完成功能的可见性
4. 确保每次提交是小而完整的变更

### Pull Request流程

尽管采用主干开发，但对于较大的变更，建议：

1. 创建一个短期特性分支
2. 完成开发后提交Pull Request
3. CI检查通过后合并到main分支
4. 立即删除特性分支

