"""Executor stage: per-page SVG via LLM."""
from __future__ import annotations

import logging
import re
from pathlib import Path

from app.services.llm.provider import LlmError, chat_completion
from app.services.ppt_master_worker.prompts import build_executor_system, build_executor_user
from app.services.ppt_master_worker.workspace import resolve_template_dir

logger = logging.getLogger(__name__)


class ExecutorError(Exception):
    pass


def extract_svg(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:svg|xml)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"(<svg[\s\S]*?</svg>)", raw, re.IGNORECASE)
    if not match:
        raise ExecutorError("Model did not return valid SVG")
    return match.group(1)


def _read_layout_svg(template_dir: Path | None, layout_file: str) -> str:
    if not template_dir or not layout_file:
        return "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1280 720\"></svg>"
    path = template_dir / layout_file
    if path.is_file():
        return path.read_text(encoding="utf-8")
    fallback = next(template_dir.glob("*.svg"), None)
    return fallback.read_text(encoding="utf-8") if fallback else ""


async def generate_page_svg(
    *,
    project_dir: Path,
    page: dict,
    page_index: int,
    total_pages: int,
    topic: str,
    language: str,
    template_source_path: str | None,
    channel: str,
    tier: str,
    model: str,
    max_attempts: int = 2,
) -> Path:
    template_dir = resolve_template_dir(template_source_path)
    layout_file = str(page.get("layout_file") or page.get("file") or "")
    layout_svg = _read_layout_svg(template_dir, layout_file)
    spec_lock = (project_dir / "spec_lock.md").read_text(encoding="utf-8")
    out_name = str(page.get("file") or f"{page_index:02d}_page.svg")
    if not out_name.endswith(".svg"):
        out_name += ".svg"
    out_path = project_dir / "svg_output" / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            messages = [
                {"role": "system", "content": build_executor_system()},
                {
                    "role": "user",
                    "content": build_executor_user(
                        page_index=page_index,
                        total_pages=total_pages,
                        page_title=str(page.get("title") or ""),
                        page_brief=str(page.get("brief") or ""),
                        topic=topic,
                        language=language,
                        layout_svg=layout_svg,
                        spec_lock=spec_lock,
                    ),
                },
            ]
            text, _, _ = await chat_completion(messages, channel=channel, tier=tier, model=model or None)
            svg = extract_svg(text)
            out_path.write_text(svg, encoding="utf-8")
            return out_path
        except (LlmError, ExecutorError, OSError) as exc:
            last_err = exc
            logger.warning(
                "Executor page %s attempt %s failed: %s",
                page_index,
                attempt,
                exc,
            )
    raise ExecutorError(f"Page {page_index} failed: {last_err}")
