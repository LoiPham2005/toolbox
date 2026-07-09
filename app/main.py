"""
ToolBox — Bộ công cụ online (video, PDF, ảnh, chuyển đổi…).
Chạy:  uvicorn app.main:app --reload   →   http://127.0.0.1:8000
"""
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .tools_registry import TOOLS, CATEGORIES, tool_by_id
from .routers import video, pdf, convert, image, misc

app = FastAPI(title="ToolBox")

app.include_router(video.router)
app.include_router(pdf.router)
app.include_router(convert.router)
app.include_router(image.router)
app.include_router(misc.router)

STATIC = os.path.join(os.path.dirname(__file__), "static")


def _page(name: str) -> str:
    with open(os.path.join(STATIC, name), encoding="utf-8") as f:
        return f.read()


@app.get("/api/tools")
def api_tools():
    """Danh mục công cụ để frontend tự dựng giao diện."""
    return {"categories": CATEGORIES, "tools": TOOLS}


@app.get("/api/tools/{tool_id}")
def api_tool(tool_id: str):
    t = tool_by_id(tool_id)
    if not t:
        raise HTTPException(404, "Không tìm thấy công cụ")
    return t


@app.get("/", response_class=HTMLResponse)
def index():
    return _page("index.html")


@app.get("/video", response_class=HTMLResponse)
def video_page():
    return _page("video.html")


@app.get("/tool", response_class=HTMLResponse)
def tool_page():
    return _page("tool.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
