"""Import external PPTX as ppt-master deck templates for the generate page."""
from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

from app.config import settings
from app.services.ppt_master_paths import ppt_master_root

logger = logging.getLogger(__name__)


def _preview_api_url(kind: str, slug: str) -> str:
    return f"/api/v1/演示/ppt-模板/preview/{kind}/{quote(slug, safe='')}"

DECK_TITLES: dict[str, str] = {
    "global_ai_capital_2026": "Global AI Capital 2026",
    "pritzker_2026": "Pritzker 2026",
    "swiss_grid_systems": "Swiss Grid Systems",
    "sugar_rush_memphis": "Sugar Rush Memphis",
    "indie_bookstore_zine_guide": "Indie Bookstore Zine",
    "glassmorphism_demo": "Glassmorphism Demo",
}

MAX_PPTX_BYTES = 20 * 1024 * 1024


class DeckTemplateImportError(Exception):
    pass


def normalize_slug(name: str) -> str:
    stem = Path(name).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return slug or "deck"


def imported_decks_root() -> Path:
    configured = (getattr(settings, "imported_deck_templates_dir", None) or "").strip()
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            backend_cwd = Path(__file__).resolve().parents[3]
            path = (backend_cwd / path).resolve()
    else:
        backend_cwd = Path(__file__).resolve().parents[3]
        path = (backend_cwd / "data" / "imported_deck_templates").resolve()
    (path / "decks").mkdir(parents=True, exist_ok=True)
    return path


def builtin_decks_root() -> Path | None:
    root = ppt_master_root()
    if not root:
        return None
    path = root / "skills" / "ppt-master" / "templates" / "decks"
    return path if path.is_dir() else None


def _import_script() -> Path:
    root = ppt_master_root()
    if not root:
        raise DeckTemplateImportError("PPT_MASTER_ROOT 未配置或不可用")
    script = root / "skills" / "ppt-master" / "scripts" / "pptx_template_import.py"
    if not script.is_file():
        raise DeckTemplateImportError(f"缺少 pptx_template_import.py: {script}")
    return script


def _run_pptx_import(pptx_path: Path, output_dir: Path) -> None:
    script = _import_script()
    root = ppt_master_root()
    cmd = [
        sys.executable,
        str(script),
        str(pptx_path),
        "-o",
        str(output_dir),
        "--inheritance-mode",
        "both",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[:1200]
        raise DeckTemplateImportError(f"pptx_template_import 失败: {detail}")


def _slide_flat_path(import_dir: Path, manifest: dict[str, Any], index: int) -> Path | None:
    for slide in manifest.get("slides") or []:
        if int(slide.get("index") or 0) != index:
            continue
        for key in ("flatSvgFile", "svgFile"):
            rel = slide.get(key)
            if not rel:
                continue
            candidate = import_dir / str(rel)
            if candidate.is_file():
                return candidate
    flat_dir = import_dir / "svg-flat"
    for pattern in (f"slide_{index:02d}.svg", f"slide_{index}.svg"):
        matches = list(flat_dir.glob(pattern))
        if matches:
            return matches[0]
    svg_dir = import_dir / "svg"
    for pattern in (f"slide_{index:02d}.svg", f"slide_{index}.svg"):
        matches = list(svg_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


def _pick_indices(manifest: dict[str, Any]) -> tuple[int, int | None, int | None, int]:
    slides = manifest.get("slides") or []
    n = len(slides) or 1
    candidates = manifest.get("pageTypeCandidates") or {}

    def first_in(*types: str) -> int | None:
        for t in types:
            vals = candidates.get(t) or []
            if vals:
                return int(vals[0])
        return None

    cover = 1
    ending = int(slides[-1]["index"]) if slides else 1
    toc = first_in("toc", "chapter", "section", "agenda")
    content = first_in("content", "body", "text", "bullet")
    if toc is None and n >= 2:
        toc = int(slides[1]["index"]) if len(slides) > 1 else 2
    if content is None and n >= 3:
        content = int(slides[max(1, n // 2)]["index"])
    elif content is None:
        content = cover
    return cover, toc, content, ending


def _primary_color(manifest: dict[str, Any]) -> str:
    theme = manifest.get("theme") or {}
    colors = theme.get("colors") or {}
    for key in ("accent1", "dk1", "accent2", "lt1"):
        val = colors.get(key)
        if isinstance(val, str) and val.startswith("#"):
            return val
    return "#2563EB"


def _write_design_spec(dest: Path, *, slug: str, title: str, manifest: dict[str, Any]) -> None:
    primary = _primary_color(manifest)
    summary = f"Imported deck template from {manifest.get('source', {}).get('name', slug)}."
    front = (
        f"---\n"
        f"deck_id: {slug}\n"
        f"kind: deck\n"
        f"summary: {summary}\n"
        f"canvas_format: ppt169\n"
        f"page_count: 5\n"
        f"primary_color: \"{primary}\"\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"Auto-imported deck template (ppt169, 1280×720).\n"
    )
    dest.write_text(front, encoding="utf-8")


def _copy_mapped_svgs(import_dir: Path, manifest: dict[str, Any], deck_dir: Path) -> None:
    cover, toc, content, ending = _pick_indices(manifest)
    mapping: list[tuple[str, int]] = [("01_cover.svg", cover), ("04_ending.svg", ending)]
    if toc is not None:
        mapping.insert(1, ("02_toc.svg", toc))
    if content is not None:
        mapping.append(("03_content.svg", content))

    deck_dir.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    for filename, index in mapping:
        if filename in seen:
            continue
        seen.add(filename)
        src = _slide_flat_path(import_dir, manifest, index)
        if not src:
            raise DeckTemplateImportError(f"无法找到第 {index} 页 SVG")
        shutil.copy2(src, deck_dir / filename)


def _update_index(index_path: Path, slug: str, *, title: str, manifest: dict[str, Any]) -> None:
    data: dict[str, Any] = {}
    if index_path.is_file():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data[slug] = {
        "summary": f"{title} — imported deck template.",
        "canvas_format": "ppt169",
        "page_count": 5,
        "primary_color": _primary_color(manifest),
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _resolve_unique_slug(base: str, decks_parent: Path) -> str:
    slug = base
    n = 2
    while (decks_parent / slug).is_dir():
        slug = f"{base}-{n}"
        n += 1
    return slug


def render_preview_png(cover_svg: Path, png_path: Path) -> bool:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import cairosvg  # type: ignore

        cairosvg.svg2png(url=str(cover_svg), write_to=str(png_path), output_width=640)
        return True
    except Exception:
        pass
    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (640, 360), (248, 250, 252))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 640, 48], fill=(37, 99, 235))
        label = cover_svg.parent.name.replace("_", " ")
        draw.text((24, 160), label[:48], fill=(30, 41, 59))
        img.save(png_path, "PNG")
        return True
    except Exception as exc:
        logger.warning("Preview render failed for %s: %s", cover_svg, exc)
        return False


def export_preview_for_slug(slug: str, *, kind: str = "deck", decks_parent: Path | None = None) -> None:
    if decks_parent is None:
        decks_parent = builtin_decks_root() or (imported_decks_root() / "decks")
    cover = decks_parent / slug / "01_cover.svg"
    if not cover.is_file():
        return
    backend_cwd = Path(__file__).resolve().parents[3]
    for rel in (
        backend_cwd / "frontend" / "public" / "deck-templates",
        backend_cwd / "backend" / "static" / "deck-templates",
    ):
        render_preview_png(cover, rel / f"{kind}-{slug}.png")


def import_pptx_to_deck_dir(
    pptx_path: Path,
    *,
    target_decks_root: Path,
    slug: str | None = None,
    title: str | None = None,
    imported: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Import PPTX into target_decks_root/{slug}/ and update sibling decks_index.json."""
    if not pptx_path.is_file():
        raise DeckTemplateImportError(f"文件不存在: {pptx_path}")
    if pptx_path.suffix.lower() != ".pptx":
        raise DeckTemplateImportError("仅支持 .pptx 文件")

    base_slug = normalize_slug(slug or pptx_path.stem)
    if overwrite:
        slug = base_slug
    else:
        slug = _resolve_unique_slug(base_slug, target_decks_root)
    display_title = title or DECK_TITLES.get(base_slug) or DECK_TITLES.get(slug) or pptx_path.stem.replace("_", " ").title()

    with tempfile.TemporaryDirectory(prefix="pptx_deck_import_") as tmp:
        import_dir = Path(tmp) / "import"
        import_dir.mkdir()
        _run_pptx_import(pptx_path.resolve(), import_dir)
        manifest_path = import_dir / "manifest.json"
        if not manifest_path.is_file():
            raise DeckTemplateImportError("import 未生成 manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        deck_dir = target_decks_root / slug
        if deck_dir.exists():
            shutil.rmtree(deck_dir)
        _copy_mapped_svgs(import_dir, manifest, deck_dir)
        _write_design_spec(deck_dir / "design_spec.md", slug=slug, title=display_title, manifest=manifest)

    index_path = (
        target_decks_root.parent / "decks_index.json"
        if imported
        else target_decks_root / "decks_index.json"
    )
    _update_index(index_path, slug, title=display_title, manifest=manifest)
    export_preview_for_slug(slug, decks_parent=target_decks_root)

    source_path = f"imported/decks/{slug}" if imported else f"templates/decks/{slug}"
    return {
        "slug": slug,
        "title": display_title,
        "kind": "deck",
        "id": f"deck:{slug}",
        "source_path": source_path,
        "preview_url": _preview_api_url("deck", slug),
        "canvas_format": "ppt169",
        "page_count": 5,
        "imported": imported,
    }


def import_pptx_bytes_to_user_deck(
    raw: bytes,
    *,
    filename: str,
    title: str | None = None,
) -> dict[str, Any]:
    if len(raw) > MAX_PPTX_BYTES:
        raise DeckTemplateImportError(f"PPTX 超过 {MAX_PPTX_BYTES // (1024 * 1024)}MB 限制")
    root = imported_decks_root()
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)
    try:
        return import_pptx_to_deck_dir(
            tmp_path,
            target_decks_root=root / "decks",
            title=title or Path(filename).stem.replace("_", " ").title(),
            imported=True,
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def import_pptx_to_builtin_deck(pptx_path: Path, *, title: str | None = None, overwrite: bool = False) -> dict[str, Any]:
    decks_root = builtin_decks_root()
    if not decks_root:
        raise DeckTemplateImportError("内置 templates/decks 目录不可用")
    return import_pptx_to_deck_dir(
        pptx_path,
        target_decks_root=decks_root,
        title=title,
        imported=False,
        overwrite=overwrite,
    )


def catalog_row_from_slug(slug: str, meta: dict[str, Any], *, imported: bool) -> dict[str, Any] | None:
    if imported:
        decks_root = imported_decks_root() / "decks"
        source_path = f"imported/decks/{slug}"
    else:
        decks_root = builtin_decks_root()
        if not decks_root:
            return None
        source_path = f"templates/decks/{slug}"
    cover = decks_root / slug / "01_cover.svg"
    if not cover.is_file():
        return None
    title = DECK_TITLES.get(slug, slug.replace("_", " ").title())
    return {
        "id": f"deck:{slug}",
        "kind": "deck",
        "slug": slug,
        "title": title,
        "description": str(meta.get("summary") or "").strip(),
        "preview_url": _preview_api_url("deck", slug),
        "canvas_format": str(meta.get("canvas_format") or "ppt169"),
        "page_count": int(meta.get("page_count") or 5),
        "source_path": source_path,
        "imported": imported,
    }
