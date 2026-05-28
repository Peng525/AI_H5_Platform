"""AI 智能 H5 演示平台 — FastAPI 入口。"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import projects, settings
from app.config import settings as app_settings
from app.database import init_db

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=app_settings.app_name,
    description="智能 H5 演示平台 API — 支持 auto/中转/官方 大模型通道",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(settings.router)


@app.get("/api/v1/健康", tags=["系统"])
async def health():
    return {"status": "ok", "app": app_settings.app_name}


if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        index = STATIC_DIR / "index.html"
        if full_path.startswith("api"):
            from fastapi import HTTPException

            raise HTTPException(status_code=404)
        if index.exists():
            return FileResponse(index)
        return {"message": "前端未构建，请先构建 frontend 或运行 Docker 完整镜像"}
