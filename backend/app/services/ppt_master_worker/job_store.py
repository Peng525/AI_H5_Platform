"""GenerationLog message read/write for premium worker jobs."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.database import SessionLocal
from app.models import GenerationLog


STAGES = (
    "queued",
    "preparing",
    "strategist",
    "generating",
    "postprocessing",
    "importing",
    "completed",
    "failed",
)


def stage_progress(stage: str, *, current_page: int = 0, total_pages: int = 0) -> int:
    if stage == "failed":
        return 0
    if stage == "completed":
        return 100
    if stage == "importing":
        return 97
    if stage == "postprocessing":
        return 92
    if stage == "generating" and total_pages > 0:
        ratio = min(1.0, max(0.0, current_page / total_pages))
        return min(90, int(round(100 * ratio)))
    pre = {
        "queued": 2,
        "preparing": 5,
        "strategist": 8,
    }
    return pre.get(stage, 0)


def stage_label(stage: str, *, current_page: int = 0, total_pages: int = 0) -> str:
    labels = {
        "queued": "准备中…",
        "preparing": "初始化项目…",
        "strategist": "规划内容与版式…",
        "postprocessing": "导出 PPTX…",
        "importing": "导入编辑器…",
        "completed": "生成完成",
        "failed": "生成失败",
    }
    if stage == "generating":
        if total_pages > 0:
            return f"正在生成第 {current_page}/{total_pages} 页…"
        return "正在生成页面…"
    return labels.get(stage, stage)


async def load_job_payload(job_id: int) -> tuple[GenerationLog, dict[str, Any]] | None:
    async with SessionLocal() as db:
        row = await db.scalar(select(GenerationLog).where(GenerationLog.id == job_id))
        if not row:
            return None
        try:
            payload = json.loads(row.message or "{}")
        except json.JSONDecodeError:
            payload = {}
        return row, payload


async def update_job(
    job_id: int,
    *,
    stage: str | None = None,
    status: str | None = None,
    current_page: int | None = None,
    total_pages: int | None = None,
    project_public_id: str | None = None,
    error: str | None = None,
    project_dir: str | None = None,
    success: int | None = None,
    duration_ms: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    async with SessionLocal() as db:
        row = await db.scalar(select(GenerationLog).where(GenerationLog.id == job_id))
        if not row:
            return
        try:
            payload = json.loads(row.message or "{}")
        except json.JSONDecodeError:
            payload = {}
        if status is not None:
            payload["status"] = status
        if stage is not None:
            payload["stage"] = stage
        if current_page is not None:
            payload["current_page"] = current_page
        if total_pages is not None:
            payload["total_pages"] = total_pages
        if project_public_id is not None:
            payload["project_public_id"] = project_public_id
        if error is not None:
            payload["error"] = error
        if project_dir is not None:
            payload["project_dir"] = project_dir
        if extra:
            payload.update(extra)
        st = payload.get("stage") or payload.get("status") or "queued"
        cp = int(payload.get("current_page") or 0)
        tp = int(payload.get("total_pages") or 0)
        payload["progress"] = stage_progress(st, current_page=cp, total_pages=tp)
        payload["stage_label"] = stage_label(st, current_page=cp, total_pages=tp)
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        row.message = json.dumps(payload, ensure_ascii=False)
        if success is not None:
            row.success = success
        if duration_ms is not None:
            row.duration_ms = duration_ms
        if project_public_id and success == 1:
            from sqlalchemy import select as sa_select
            from app.models import Project

            project = await db.scalar(
                sa_select(Project).where(Project.public_id == project_public_id)
            )
            if project:
                row.project_id = project.id
        await db.commit()


def public_job_view(payload: dict[str, Any], *, job_id: int) -> dict[str, Any]:
    stage = payload.get("stage") or payload.get("status") or "unknown"
    current_page = int(payload.get("current_page") or 0)
    total_pages = int(payload.get("total_pages") or 0)
    return {
        "job_id": job_id,
        "status": payload.get("status", stage),
        "stage": stage,
        "progress": int(payload.get("progress") or stage_progress(stage, current_page=current_page, total_pages=total_pages)),
        "stage_label": payload.get("stage_label") or stage_label(stage, current_page=current_page, total_pages=total_pages),
        "current_page": current_page,
        "total_pages": total_pages,
        "project_public_id": payload.get("project_public_id"),
        "error": payload.get("error"),
        "topic": payload.get("topic"),
        "page_count": payload.get("page_count"),
        "ppt_template_id": payload.get("ppt_template_id"),
        "ppt_template_kind": payload.get("ppt_template_kind"),
        "pipeline_available": bool(payload.get("pipeline_available")),
        "workflow_doc": payload.get("workflow_doc") or "",
        "import_endpoint": payload.get("import_endpoint") or "",
        "hint": payload.get("hint") or "",
    }
