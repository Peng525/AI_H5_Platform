"""公开：演示文稿 ppt-master PPT 模板列表与导入。"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.deps.auth import get_current_user
from app.models import User
from app.services.deck.ppt_template_catalog import list_ppt_templates, resolve_cover_svg_path
from app.services.deck.pptx_deck_template_import import (
    DeckTemplateImportError,
    import_pptx_bytes_to_user_deck,
)

router = APIRouter(prefix="/api/v1/演示", tags=["演示"])


@router.get("/ppt-模板", summary="生成页可用 ppt-master PPT 模板")
async def list_deck_ppt_templates(_user: User = Depends(get_current_user)):
    return {"items": list_ppt_templates()}


@router.get("/ppt-模板/preview/{kind}/{slug}", summary="PPT 模板封面 SVG 预览")
async def get_ppt_template_preview(kind: str, slug: str):
    """Public read-only cover SVG (catalog whitelist); used by <img> without Bearer header."""
    if kind not in ("layout", "deck"):
        raise HTTPException(status_code=404, detail="模板预览不存在")
    cover = resolve_cover_svg_path(kind, slug)
    if not cover:
        raise HTTPException(status_code=404, detail="模板预览不存在")
    return FileResponse(cover, media_type="image/svg+xml")


@router.post("/ppt-模板/导入", summary="上传 PPTX 并注册为可选 deck 模板")
async def import_deck_ppt_template(
    file: UploadFile = File(...),
    title: str = Form(""),
    user: User = Depends(get_current_user),
):
    _ = user
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="请上传 .pptx 文件")
    raw = await file.read()
    try:
        result = import_pptx_bytes_to_user_deck(
            raw,
            filename=file.filename,
            title=title.strip() or None,
        )
    except DeckTemplateImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"导入失败：{exc}") from exc
    return result
