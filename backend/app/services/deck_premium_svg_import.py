"""Import ppt-master SVG slides into H5 canvas (premium worker path)."""
from __future__ import annotations

import base64
import json
import logging
import re
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog, Project, User
from app.services.deck_premium_job import _premium_settings
from app.services.deck_generator import new_public_id
from app.services.project_seed_service import seed_project_slides

logger = logging.getLogger(__name__)

CANVAS_W = 1280
CANVAS_H = 720


def _natural_sort_key(path: Path) -> tuple:
    parts = re.split(r"(\d+)", path.stem.lower())
    return tuple(int(p) if p.isdigit() else p for p in parts)


def resolve_premium_svg_dir(project_dir: Path) -> Path:
    """Prefer finalized SVGs; fall back to executor output."""
    for name in ("svg_final", "svg_output"):
        candidate = project_dir / name
        if candidate.is_dir() and any(candidate.glob("*.svg")):
            return candidate
    raise FileNotFoundError(f"No SVG slides under {project_dir}")


def list_premium_svg_files(project_dir: Path) -> list[Path]:
    svg_dir = resolve_premium_svg_dir(project_dir)
    files = [p for p in svg_dir.glob("*.svg") if p.is_file()]
    if not files:
        raise FileNotFoundError(f"No SVG files in {svg_dir}")
    return sorted(files, key=_natural_sort_key)


def _svg_data_url(svg_path: Path) -> str:
    raw = svg_path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _slide_title(page_meta: dict[str, Any] | None, slide_idx: int, svg_path: Path) -> str:
    if page_meta:
        title = str(page_meta.get("title") or "").strip()
        if title and title not in {f"第 {slide_idx + 1} 页", f"Page {slide_idx + 1}"}:
            return title[:80]
    stem = svg_path.stem.replace("_", " ").strip()
    if stem and not re.fullmatch(r"\d+", stem):
        return stem[:80]
    return f"第 {slide_idx + 1} 页"


def build_slides_from_svgs(
    svg_files: list[Path],
    pages: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build H5 slides_json with one full-canvas SVG image per page."""
    pages = pages or []
    slides: list[dict[str, Any]] = []
    for idx, svg_path in enumerate(svg_files):
        page_meta = pages[idx] if idx < len(pages) else None
        data_url = _svg_data_url(svg_path)
        slides.append(
            {
                "title": _slide_title(page_meta, idx, svg_path),
                "subtitle": "",
                "layout": "cover" if idx == 0 else "bullets",
                "animation": "fade",
                "canvas_background": "#FFFFFF",
                "canvas_elements": [
                    {
                        "id": f"premium_{idx}_slide",
                        "type": "image",
                        "x": 0,
                        "y": 0,
                        "width": CANVAS_W,
                        "height": CANVAS_H,
                        "zIndex": 1,
                        "content": data_url,
                        "style": {"background": "transparent", "objectFit": "fill"},
                    }
                ],
                "bullets": [],
            }
        )
    return slides


async def import_premium_svgs(
    db: AsyncSession,
    user: User,
    svg_files: list[Path],
    *,
    pages: list[dict[str, Any]] | None = None,
    title: str | None = None,
    project_dir: Path | None = None,
) -> Project:
    if not svg_files:
        raise ValueError("No SVG files to import")

    slides_seed = build_slides_from_svgs(svg_files, pages)
    inferred = (title or "AI 演示").strip() or "AI 演示"
    template_settings = _premium_settings({}, source_file=str(project_dir or ""))
    pid = new_public_id()
    project = Project(
        title=inferred[:120],
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
            channel="svg",
            model="ppt-master",
            success=1,
            message=json.dumps(
                {
                    "source": "svg",
                    "slides": len(slides_seed),
                    "svg_dir": str(project_dir) if project_dir else "",
                },
                ensure_ascii=False,
            ),
        )
    )
    logger.info(
        "Premium SVG import: project=%s slides=%s from %s",
        pid,
        len(slides_seed),
        project_dir or svg_files[0].parent,
    )
    return project
