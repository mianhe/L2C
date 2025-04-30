import logging
import os
import sys

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import customers
from app.db.database import init_db
from app.mcp.router import router as mcp_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,  # 强制重新配置日志
)

# 确保所有的日志处理器都不使用缓冲
for handler in logging.root.handlers:
    handler.flush()
    if hasattr(handler, "stream"):
        handler.stream.flush()

logger = logging.getLogger(__name__)

# 立即打印一条消息来测试日志是否正常工作
print("Starting application...", flush=True)
logger.info("Logger initialized")

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Base directory: {BASE_DIR}")

# 创建 FastAPI 应用
app = FastAPI(title="L2C API")

# 设置模板和静态文件目录
TEMPLATE_DIR = os.path.join(BASE_DIR, "app", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")

logger.info(f"Template directory: {TEMPLATE_DIR}")
logger.info(f"Static directory: {STATIC_DIR}")

# 挂载静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 配置模板
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# 初始化数据库
init_db()

# 包含路由器
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(mcp_router)


@app.get("/info", response_class=HTMLResponse)
async def info_page(request: Request):
    """信息页面，包含项目介绍和API文档"""
    return templates.TemplateResponse("info.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """客户管理页面作为主页"""
    try:
        logger.info("Attempting to render index.html")
        logger.info(f"Template directory during render: {TEMPLATE_DIR}")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering customer management page: {str(e)}")
        logger.exception("Full traceback:")
        return "Error loading customer management page"
