"""ppt-master layout + deck template catalog for generate page."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import quote

from app.services.deck.pptx_deck_template_import import DECK_TITLES, catalog_row_from_slug, imported_decks_root
from app.services.ppt_master_paths import ppt_master_root

logger = logging.getLogger(__name__)

LAYOUT_TITLES: dict[str, str] = {
    "academic_defense": "学术答辩",
    "ai_ops": "AI 运维架构",
    "government_blue": "政务蓝",
    "government_red": "政务红",
    "medical_university": "医学学术",
    "pixel_retro": "像素复古",
    "psychology_attachment": "心理培训",
}


def preview_api_url(kind: str, slug: str) -> str:
    """Public preview URL — cover SVG served by authenticated API."""
    return f"/api/v1/演示/ppt-模板/preview/{kind}/{quote(slug, safe='')}"


def _preview_url(kind: str, slug: str) -> str:
    return preview_api_url(kind, slug)


def resolve_cover_svg_path(kind: str, slug: str) -> Path | None:
    """Resolve cover SVG for a catalog entry (whitelist via list_ppt_templates)."""
    if kind not in ("layout", "deck"):
        return None
    for row in list_ppt_templates():
        if row.get("kind") != kind or row.get("slug") != slug:
            continue
        source_path = str(row.get("source_path") or "")
        if source_path.startswith("imported/decks/"):
            rel = source_path.removeprefix("imported/decks/")
            cover = imported_decks_root() / "decks" / rel / "01_cover.svg"
        elif source_path.startswith("templates/layouts/"):
            rel = source_path.removeprefix("templates/layouts/")
            root = _builtin_templates_root()
            if not root:
                return None
            cover = root / "layouts" / rel / "01_cover.svg"
        elif source_path.startswith("templates/decks/"):
            rel = source_path.removeprefix("templates/decks/")
            root = _builtin_templates_root()
            if not root:
                return None
            cover = root / "decks" / rel / "01_cover.svg"
        else:
            return None
        return cover if cover.is_file() else None
    return None


def _load_index(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read ppt template index %s: %s", path, exc)
        return {}


def _row_from_entry(
    *,
    kind: str,
    slug: str,
    meta: dict[str, Any],
    templates_root: Path,
    imported: bool = False,
) -> dict[str, Any] | None:
    if kind == "deck" and imported:
        dir_path = templates_root / slug
        source_path = f"imported/decks/{slug}"
    else:
        rel_kind = "layouts" if kind == "layout" else "decks"
        dir_path = templates_root / rel_kind / slug
        source_path = f"templates/{rel_kind}/{slug}"

    cover = dir_path / "01_cover.svg"
    if not cover.is_file():
        return None

    if kind == "layout":
        title = LAYOUT_TITLES.get(slug, slug.replace("_", " ").title())
    else:
        title = DECK_TITLES.get(slug, slug.replace("_", " ").title())

    summary = str(meta.get("summary") or "").strip()
    return {
        "id": f"{kind}:{slug}",
        "kind": kind,
        "slug": slug,
        "title": title,
        "description": summary,
        "preview_url": _preview_url(kind, slug),
        "canvas_format": str(meta.get("canvas_format") or "ppt169"),
        "page_count": int(meta.get("page_count") or 5),
        "source_path": source_path,
        "imported": imported,
    }


def _builtin_templates_root() -> Path | None:
    root = ppt_master_root()
    if not root:
        return None
    path = root / "skills" / "ppt-master" / "templates"
    return path if path.is_dir() else None


def list_ppt_templates() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    templates_root = _builtin_templates_root()
    if templates_root:
        layouts_index = _load_index(templates_root / "layouts" / "layouts_index.json")
        for slug, meta in sorted(layouts_index.items()):
            row = _row_from_entry(
                kind="layout",
                slug=slug,
                meta=meta or {},
                templates_root=templates_root,
            )
            if row:
                items.append(row)

        decks_index = _load_index(templates_root / "decks" / "decks_index.json")
        for slug, meta in sorted(decks_index.items()):
            row = _row_from_entry(
                kind="deck",
                slug=slug,
                meta=meta or {},
                templates_root=templates_root,
            )
            if row:
                items.append(row)
    else:
        logger.info("ppt_master_root unavailable; builtin deck ppt templates skipped")

    imported_root = imported_decks_root()
    imported_decks = imported_root / "decks"
    imported_index = _load_index(imported_root / "decks_index.json")
    for slug, meta in sorted(imported_index.items()):
        row = catalog_row_from_slug(slug, meta or {}, imported=True)
        if row:
            items.append(row)
        else:
            row = _row_from_entry(
                kind="deck",
                slug=slug,
                meta=meta or {},
                templates_root=imported_decks,
                imported=True,
            )
            if row:
                items.append(row)

    return items
