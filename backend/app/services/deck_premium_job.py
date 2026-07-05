"""Premium deck pipeline: ppt-master export → H5 import (Phase C skeleton)."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import GenerationLog, Project, User
from app.schemas import AiDeckGenerateRequest
from app.services.pptx_template_parser import PptxParseError, parse_pptx_bytes
from app.services.project_seed_service import seed_project_slides
from app.services.deck_generator import new_public_id

logger = logging.getLogger(__name__)

WORKFLOW_DOC = "develop/docs/ppt-master-benchmark/h5-premium-workflow.md"


def ppt_master_root() -> Path | None:
    base = Path(__file__).resolve().parents[2]
    configured = (settings.ppt_master_root or "").strip()
    if configured:
        path = Path(configured)
        return path if path.is_dir() else None
    candidate = base / "ppt-master-main"
    return candidate if candidate.is_dir() else None


def pipeline_available() -> bool:
    root = ppt_master_root()
    if not root:
        return False
    skill = root / "skills" / "ppt-master" / "SKILL.md"
    return skill.is_file()


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
    """Queue premium generation. Full agent pipeline requires ppt-master worker; returns job metadata."""
    root = ppt_master_root()
    available = pipeline_available()
    payload = {
        "status": "awaiting_pptx",
        "user_id": user.id,
        "topic": body.topic[:500],
        "page_count": body.page_count,
        "ppt_master_root": str(root) if root else None,
        "pipeline_available": available,
        "workflow_doc": WORKFLOW_DOC,
        "import_endpoint": "/api/v1/项目/premium-导入-pptx",
        "hint": "在 Cursor 中按 ppt-master SKILL 生成 PPTX 后，调用 premium-导入-pptx 或 Dashboard 导入。",
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
    return {"job_id": log.id, **payload}


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
    return {
        "job_id": row.id,
        "status": detail.get("status", "unknown"),
        "topic": detail.get("topic"),
        "page_count": detail.get("page_count"),
        "pipeline_available": bool(detail.get("pipeline_available")),
        "workflow_doc": detail.get("workflow_doc") or "",
        "import_endpoint": detail.get("import_endpoint") or "",
        "hint": detail.get("hint") or "",
    }
