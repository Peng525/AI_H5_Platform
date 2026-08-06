"""Premium deck pipeline: ppt-master worker → H5 import."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog, Project, User
from app.schemas import AiDeckGenerateRequest
from app.services.ppt_master_paths import pipeline_available, ppt_master_root
from app.services.ppt_master_worker.job_store import public_job_view, stage_label, stage_progress
from app.services.pptx_template_parser import PptxParseError, parse_pptx_bytes
from app.services.project_seed_service import seed_project_slides
from app.services.deck_generator import new_public_id

logger = logging.getLogger(__name__)

WORKFLOW_DOC = "develop/docs/ppt-master-benchmark/h5-premium-workflow.md"


def resolve_template_source_path(ppt_template_id: str | None) -> str | None:
    if not ppt_template_id or ":" not in ppt_template_id:
        return None
    kind, slug = ppt_template_id.split(":", 1)
    if kind not in ("layout", "deck") or not slug:
        return None
    if kind == "deck":
        from app.services.deck.pptx_deck_template_import import imported_decks_root

        imported_cover = imported_decks_root() / "decks" / slug / "01_cover.svg"
        if imported_cover.is_file():
            return f"imported/decks/{slug}"
    rel_kind = "layouts" if kind == "layout" else "decks"
    return f"templates/{rel_kind}/{slug}"


def _premium_settings(parsed_settings: dict[str, Any], *, source_file: str = "") -> dict[str, Any]:
    out = dict(parsed_settings or {})
    out["viewportId"] = "web-1280"
    meta = dict(out.get("generationMeta") or {})
    meta.update(
        {
            "source": "ppt-master",
            "premium": True,
            "imported_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    if source_file:
        meta["source_file"] = source_file
    out["generationMeta"] = meta
    out.setdefault("themeId", "zjy-minimal")
    out.setdefault("scrollEffect", "vertical")
    return out


async def import_premium_pptx(
    db: AsyncSession,
    user: User,
    raw: bytes,
    *,
    title: str | None = None,
    filename: str = "",
) -> Project:
    inferred = title or (filename or "ppt-master 导入").rsplit(".", 1)[0]
    try:
        parsed = parse_pptx_bytes(raw, device="web", title=inferred)
    except PptxParseError:
        raise

    template_settings = _premium_settings(parsed.get("settings_json") or {}, source_file=filename)
    slides_seed = parsed.get("slides_json") or []
    pid = new_public_id()
    project = Project(
        title=parsed.get("title") or inferred,
        theme="imported-premium",
        public_id=pid,
        share_slug=pid,
        user_id=user.id,
        settings_json=json.dumps(template_settings, ensure_ascii=False),
    )
    db.add(project)
    await db.flush()
    await seed_project_slides(db, project, slides_seed, template_settings)
    db.add(
        GenerationLog(
            project_id=project.id,
            template_id="premium_deck_import",
            channel="import",
            model="ppt-master",
            success=1,
            message=json.dumps({"filename": filename, "slides": len(slides_seed)}, ensure_ascii=False),
        )
    )
    return project


async def submit_premium_deck_job(
    db: AsyncSession,
    user: User,
    body: AiDeckGenerateRequest,
) -> dict[str, Any]:
    """Queue premium generation; worker runs asynchronously after commit."""
    root = ppt_master_root()
    available = pipeline_available()
    source_path = resolve_template_source_path(body.ppt_template_id)
    page_count = max(1, min(30, int(body.page_count or 8)))
    extra_content = (body.extra_content or "")[:8000]
    if body.page_contents:
        parts = [str(p).strip() for p in body.page_contents if str(p).strip()]
        if parts:
            per_page = "\n\n".join(f"第 {i + 1} 页：{text}" for i, text in enumerate(parts))
            extra_content = f"{extra_content}\n\n{per_page}".strip()[:8000]
    stage = "queued"
    payload = {
        "status": stage,
        "stage": stage,
        "progress": stage_progress(stage),
        "stage_label": stage_label(stage),
        "current_page": 0,
        "total_pages": page_count,
        "user_id": user.id,
        "topic": body.topic[:500],
        "page_count": page_count,
        "language": body.language or "简体中文",
        "extra_content": extra_content,
        "page_contents": body.page_contents or [],
        "ppt_template_id": body.ppt_template_id,
        "ppt_template_kind": body.ppt_template_kind,
        "ppt_template_source_path": source_path,
        "channel": body.channel or "auto",
        "model": body.model or "",
        "ppt_master_root": str(root) if root else None,
        "pipeline_available": available,
        "workflow_doc": WORKFLOW_DOC,
        "import_endpoint": "/api/v1/项目/premium-导入-pptx",
        "hint": "正在排队生成高质量演示…" if available else "ppt-master 未就绪，请检查 PPT_MASTER_ROOT",
        "project_public_id": None,
        "error": None,
    }
    log = GenerationLog(
        project_id=None,
        template_id="premium_deck",
        channel=body.channel or "auto",
        model=body.model or "",
        success=0,
        message=json.dumps(payload, ensure_ascii=False),
    )
    db.add(log)
    await db.flush()
    return public_job_view(payload, job_id=log.id)


async def get_premium_job_status(db: AsyncSession, job_id: int, user_id: int) -> dict[str, Any] | None:
    from sqlalchemy import select

    row = await db.scalar(select(GenerationLog).where(GenerationLog.id == job_id))
    if not row or row.template_id not in ("premium_deck", "premium_deck_import"):
        return None
    try:
        detail = json.loads(row.message or "{}")
    except json.JSONDecodeError:
        detail = {"raw_message": row.message}
    if detail.get("user_id") not in (None, user_id):
        return None
    return public_job_view(detail, job_id=row.id)
