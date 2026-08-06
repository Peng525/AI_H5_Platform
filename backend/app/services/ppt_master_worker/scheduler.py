"""Async scheduling for premium deck jobs."""
from __future__ import annotations

import asyncio
import logging

from app.config import settings
from app.services.ppt_master_worker.orchestrator import run_premium_job

logger = logging.getLogger(__name__)

_semaphore: asyncio.Semaphore | None = None
_running: set[int] = set()


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        limit = max(1, int(settings.ppt_master_max_concurrent or 1))
        _semaphore = asyncio.Semaphore(limit)
    return _semaphore


async def _run_guarded(job_id: int) -> None:
    sem = _get_semaphore()
    async with sem:
        try:
            await asyncio.wait_for(
                run_premium_job(job_id),
                timeout=float(settings.ppt_master_job_timeout_sec or 1800),
            )
        except asyncio.TimeoutError:
            from app.services.ppt_master_worker.job_store import update_job

            await update_job(
                job_id,
                stage="failed",
                status="failed",
                error="生成超时，请稍后重试或缩短页数",
                success=0,
            )
        finally:
            _running.discard(job_id)


def enqueue_premium_job(job_id: int) -> None:
    if job_id in _running:
        return
    _running.add(job_id)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_run_guarded(job_id))
    except RuntimeError:
        logger.warning("No running event loop; cannot enqueue premium job %s", job_id)
