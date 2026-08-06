"""Main ppt-master worker orchestration."""
from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import User
from app.services.ppt_master_paths import pipeline_available, ppt_master_root
from app.services.ppt_master_worker.executor import ExecutorError, generate_page_svg
from app.services.ppt_master_worker.job_store import update_job
from app.services.ppt_master_worker.strategist import run_strategist
from app.services.ppt_master_worker.subprocess_runner import export_pptx, finalize_project, init_project

logger = logging.getLogger(__name__)


async def _set_stage(job_id: int, stage: str, **kwargs: Any) -> None:
    await update_job(job_id, stage=stage, status=stage, **kwargs)


async def run_premium_job(job_id: int) -> None:
    started = time.monotonic()
    try:
        async with SessionLocal() as db:
            from app.models import GenerationLog
            import json

            row = await db.scalar(select(GenerationLog).where(GenerationLog.id == job_id))
            if not row:
                return
            try:
                payload = json.loads(row.message or "{}")
            except json.JSONDecodeError:
                payload = {}

        if payload.get("status") in ("completed", "failed"):
            return

        if not pipeline_available():
            raise RuntimeError("ppt-master pipeline unavailable; configure PPT_MASTER_ROOT")

        user_id = int(payload.get("user_id") or 0)
        topic = str(payload.get("topic") or "").strip()
        page_count = max(1, min(30, int(payload.get("page_count") or 8)))
        language = str(payload.get("language") or "简体中文")
        extra_content = str(payload.get("extra_content") or "")
        channel = str(payload.get("channel") or "auto")
        model = str(payload.get("model") or "")
        template_source = payload.get("ppt_template_source_path")

        async with SessionLocal() as db:
            user = await db.scalar(select(User).where(User.id == user_id))
            if not user:
                raise RuntimeError("Job owner not found")
            tier = user.tier or "free"

        await _set_stage(job_id, "preparing", total_pages=page_count, current_page=0)
        slug = f"h5-job-{job_id}"
        project_dir = await init_project(slug, canvas_format="ppt169")
        await update_job(job_id, project_dir=str(project_dir))

        await _set_stage(job_id, "strategist", total_pages=page_count)
        pages, _defaults = await run_strategist(
            project_dir=project_dir,
            topic=topic,
            page_count=page_count,
            language=language,
            template_source_path=template_source,
            extra_content=extra_content,
            channel=channel,
            tier=tier,
            model=model,
        )
        total = len(pages)

        await _set_stage(job_id, "generating", total_pages=total, current_page=0)
        for idx, page in enumerate(pages, 1):
            await update_job(job_id, current_page=idx, total_pages=total, stage="generating", status="generating")
            await generate_page_svg(
                project_dir=project_dir,
                page=page,
                page_index=idx,
                total_pages=total,
                topic=topic,
                language=language,
                template_source_path=template_source,
                channel=channel,
                tier=tier,
                model=model,
            )

        await _set_stage(job_id, "postprocessing", current_page=total, total_pages=total)
        await finalize_project(project_dir)

        await _set_stage(job_id, "importing", current_page=total, total_pages=total)
        from app.services.deck_premium_svg_import import import_premium_svgs, list_premium_svg_files

        svg_files = list_premium_svg_files(project_dir)
        pptx_path = None
        try:
            pptx_path = await export_pptx(project_dir)
        except RuntimeError as exc:
            logger.warning("Premium job %s pptx export skipped: %s", job_id, exc)

        async with SessionLocal() as db:
            user = await db.scalar(select(User).where(User.id == user_id))
            if not user:
                raise RuntimeError("Job owner not found")
            project = await import_premium_svgs(
                db,
                user,
                svg_files,
                pages=pages,
                title=topic[:80] or "AI 演示",
                project_dir=project_dir,
            )
            await db.commit()
            public_id = project.public_id

        elapsed_ms = int((time.monotonic() - started) * 1000)
        await update_job(
            job_id,
            stage="completed",
            status="completed",
            current_page=total,
            total_pages=total,
            project_public_id=public_id,
            success=1,
            duration_ms=elapsed_ms,
            extra={
                "hint": "生成完成，正在进入编辑器…",
                "pptx_file": pptx_path.name if pptx_path else None,
                "import_source": "svg",
                "svg_count": len(svg_files),
                "ppt_master_root": str(ppt_master_root() or ""),
            },
        )
        logger.info("Premium job %s completed project=%s in %sms", job_id, public_id, elapsed_ms)
    except (ExecutorError, RuntimeError, OSError, ValueError) as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        logger.exception("Premium job %s failed", job_id)
        await update_job(
            job_id,
            stage="failed",
            status="failed",
            error=str(exc)[:800],
            success=0,
            duration_ms=elapsed_ms,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = int((time.monotonic() - started) * 1000)
        logger.exception("Premium job %s unexpected failure", job_id)
        await update_job(
            job_id,
            stage="failed",
            status="failed",
            error=f"内部错误：{exc}"[:800],
            success=0,
            duration_ms=elapsed_ms,
        )
