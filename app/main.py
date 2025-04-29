from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .mcp.router import router as mcp_router

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="app/templates")

# 引入MCP路由
app.include_router(mcp_router)

@app.get("/")
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/info")
async def info(request: Request):
    """信息页面"""
    return templates.TemplateResponse("info.html", {"request": request}) 