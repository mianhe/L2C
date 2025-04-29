from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging
import os
from app.db.database import init_db
from app.api import customers
from app.mcp.router import router as mcp_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 创建 FastAPI 应用
app = FastAPI(title="L2C API")

# 挂载静态文件
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "app/static")), name="static")

# 配置模板
templates = Jinja2Templates(directory=os.path.join(current_dir, "app/templates"))

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
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering customer management page: {e}")
        return "Error loading customer management page" 