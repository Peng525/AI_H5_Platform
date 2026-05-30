"""AI 智能 H5 演示平台 — FastAPI 入口。"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, auth, bgm, commerce, image_prompt_templates, layout_blocks, projects, settings, templates_catalog
from app.services.bgm_service import resolve_bgm_dir
from app.config import settings as app_settings
from app.database import init_db
from app.seed import seed_demo_user

# app/main.py -> parents[1] = backend 目录
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
# 个人收款码放此目录，不会被前端 build 清空（Docker 可挂载）
PAY_ASSETS_DIR = Path(__file__).resolve().parents[1] / "pay_assets"
MEDIA_DIR = Path(__file__).resolve().parents[1] / "media"


def _wechat_qr_image_path() -> Path | None:
    for candidate in (
        PAY_ASSETS_DIR / "wechat-pay-qr.png",
        STATIC_DIR / "wechat-pay-qr.png",
    ):
        if candidate.is_file():
            return candidate
    return None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    await seed_demo_user()
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

app.include_router(auth.router)
app.include_router(commerce.router)
app.include_router(admin.router)
app.include_router(templates_catalog.router)
app.include_router(projects.router)
app.include_router(settings.router)
app.include_router(bgm.router)
app.include_router(layout_blocks.router)
app.include_router(image_prompt_templates.router)


@app.get("/api/v1/健康", tags=["系统"])
async def health():
    return {"status": "ok", "app": app_settings.app_name}


if STATIC_DIR.exists():
    index_file = STATIC_DIR / "index.html"
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/static/wechat-pay-qr.png", include_in_schema=False)
    async def wechat_pay_qr_image():
        from fastapi import HTTPException

        path = _wechat_qr_image_path()
        if not path:
            raise HTTPException(status_code=404, detail="收款码图片未配置")
        return FileResponse(path, media_type="image/png")

    bgm_dir = resolve_bgm_dir()
    if bgm_dir is not None:
        app.mount("/static/bgm", StaticFiles(directory=bgm_dir), name="static_bgm")

    @app.get("/", include_in_schema=False)
    async def spa_index():
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "前端未构建，请先构建 frontend 或运行 Docker 完整镜像"}

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if full_path.startswith("api"):
            from fastapi import HTTPException

            raise HTTPException(status_code=404)
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "前端未构建，请先构建 frontend 或运行 Docker 完整镜像"}
else:

    @app.get("/", include_in_schema=False)
    async def spa_missing():
        return {"message": "前端未构建，请运行 npm run build 或 docker compose build"}
