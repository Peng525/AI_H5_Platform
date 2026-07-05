"""Resume module API — English paths only."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import ResumeProfile, User
from app.services.ocr.paddle_provider import OcrUnavailableError
from app.services.quota import QuotaExceeded
from app.services.resume import file_storage
from app.services.resume.export_service import export_docx_bytes, export_pdf_bytes
from app.services.resume.thumbnail_service import read_thumbnail
from app.services.resume.template_catalog import (
    INDUSTRIES,
    filter_resume_templates,
    filter_visual_templates,
)
from app.services.resume.resume_service import (
    ContentPolicyError,
    ResumeLimitExceeded,
    ResumeNotFoundError,
    _latest_structured,
    _latest_visual,
    _profile_payload,
    create_profile,
    delete_profile,
    get_owned_profile,
    list_item_payload,
    run_generate,
    run_optimize,
    save_profile,
    save_uploaded_file,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/resume", tags=["resume"])


class CreateResumeBody(BaseModel):
    title: str | None = None
    prompt: str | None = None
    file_id: int | None = None
    jd_file_id: int | None = None
    template_id: str | None = None
    prompt_template_id: str | None = None
    industry_id: str | None = None


class GenerateBody(BaseModel):
    template_id: str = Field(..., min_length=1, description="视觉模板 ID，必填")
    prompt: str | None = None
    file_id: int | None = None
    jd_file_id: int | None = None
    prompt_template_id: str | None = None
    industry_id: str | None = None


class OptimizeBody(BaseModel):
    prompt: str = Field(..., min_length=1)


class UpdateResumeBody(BaseModel):
    title: str | None = None
    structured: dict | None = None
    visual_document: dict | None = None


def _quota_http(exc: QuotaExceeded):
    raise HTTPException(status_code=402, detail=str(exc))


@router.get("/industries")
async def list_industries():
    return {"items": INDUSTRIES}


@router.get("/templates")
async def list_templates(industry: str | None = Query(default=None)):
    return {"items": filter_resume_templates(industry)}


@router.get("/visual-templates")
async def list_visual_templates(industry: str | None = Query(default=None)):
    return {"items": filter_visual_templates(industry)}


@router.post("/files")
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    try:
        row = await save_uploaded_file(db, user.id, file.filename or "upload", content, file.content_type or "")
        await db.commit()
    except file_storage.FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    return {
        "file_id": row.id,
        "filename": file.filename,
        "mime": row.mime,
        "size_bytes": row.size_bytes,
    }


@router.post("")
async def create_resume(
    body: CreateResumeBody,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await create_profile(
            db,
            user,
            title=body.title,
            prompt=body.prompt,
            file_id=body.file_id,
            jd_file_id=body.jd_file_id,
            template_id=body.template_id,
        )
        await db.commit()
        await db.refresh(profile)
        return {"public_id": profile.public_id, "title": profile.title}
    except ResumeLimitExceeded as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ContentPolicyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OperationalError as exc:
        logger.exception("create_resume db schema error user_id=%s", user.id)
        raise HTTPException(status_code=503, detail="数据库结构需同步，请重启服务") from exc
    except Exception as exc:
        logger.exception("create_resume failed user_id=%s", user.id)
        raise HTTPException(status_code=500, detail=f"创建失败：{exc}") from exc


@router.get("")
async def list_resumes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(
        select(ResumeProfile)
        .where(ResumeProfile.user_id == user.id)
        .order_by(ResumeProfile.updated_at.desc())
    )
    items = [list_item_payload(p) for p in r.scalars().all() if not file_storage.is_expired(p.expires_at)]
    return {"items": items}


@router.get("/{public_id}")
async def get_resume(
    public_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await get_owned_profile(db, user.id, public_id)
        return _profile_payload(profile)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{public_id}/messages")
async def get_messages(
    public_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await get_owned_profile(db, user.id, public_id)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    items = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "message_type": m.message_type,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in sorted(profile.messages, key=lambda x: x.id)
    ]
    return {"items": items}


@router.post("/{public_id}/generate")
async def generate_resume(
    public_id: str,
    body: GenerateBody,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await run_generate(
            db,
            user,
            public_id,
            prompt=body.prompt,
            file_id=body.file_id,
            jd_file_id=body.jd_file_id,
            template_id=body.template_id,
            prompt_template_id=body.prompt_template_id,
            industry_id=body.industry_id,
        )
    except QuotaExceeded as exc:
        _quota_http(exc)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ContentPolicyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OcrUnavailableError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("generate_resume failed public_id=%s", public_id)
        raise HTTPException(status_code=502, detail=f"生成失败：{exc}") from exc


@router.post("/{public_id}/optimize")
async def optimize_resume(
    public_id: str,
    body: OptimizeBody,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await run_optimize(db, user, public_id, body.prompt)
    except QuotaExceeded as exc:
        _quota_http(exc)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ContentPolicyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OcrUnavailableError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("optimize_resume failed public_id=%s", public_id)
        raise HTTPException(status_code=502, detail=f"优化失败：{exc}") from exc


@router.get("/{public_id}/thumbnail")
async def get_resume_thumbnail(
    public_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await get_owned_profile(db, user.id, public_id)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not profile.thumbnail_path:
        raise HTTPException(status_code=404, detail="缩略图不存在")
    try:
        data = read_thumbnail(profile.thumbnail_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="缩略图不存在") from exc
    return Response(data, media_type="image/png")


@router.put("/{public_id}")
async def update_resume(
    public_id: str,
    body: UpdateResumeBody,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await save_profile(
            db,
            user.id,
            public_id,
            title=body.title,
            structured=body.structured,
            visual_document=body.visual_document,
        )
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{public_id}/export")
async def export_resume(
    public_id: str,
    format: str = "pdf",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await get_owned_profile(db, user.id, public_id)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    structured = _latest_structured(profile)
    visual = _latest_visual(profile)
    fmt = (format or "pdf").lower()
    if fmt == "docx":
        data = export_docx_bytes(structured, visual)
        return Response(
            data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{profile.title}.docx"'},
        )
    data = export_pdf_bytes(structured, visual)
    return Response(
        data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{profile.title}.pdf"'},
    )


@router.delete("/{public_id}")
async def delete_resume(
    public_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_profile(db, user.id, public_id)
        await db.commit()
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True}
