"""Prompt assembly for Strategist / Executor stages."""
from __future__ import annotations

from pathlib import Path

from app.services.ppt_master_paths import ppt_master_root


def _read_reference(name: str, *, max_chars: int = 12000) -> str:
    root = ppt_master_root()
    if not root:
        return ""
    path = root / "skills" / "ppt-master" / "references" / name
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[... truncated ...]"
    return text


def build_strategist_system(language: str) -> str:
    base = _read_reference("strategist.md", max_chars=8000)
    return (
        "You are the Strategist for ppt-master deck generation inside an automated worker.\n"
        "Skip blocking confirmations; apply product defaults.\n"
        f"Output language: {language}.\n"
        "Respond with a single JSON object only (no markdown fence).\n"
        "Schema:\n"
        '{"pages":[{"file":"01_cover.svg","layout_file":"01_cover.svg","title":"...","brief":"..."}]}\n'
        "Each page must have unique sequential file names like 01_cover.svg, 02_....svg.\n"
        "layout_file must be an existing template SVG basename.\n\n"
        + base
    )


def build_strategist_user(
    *,
    topic: str,
    page_count: int,
    language: str,
    layout_files: list[str],
    extra_content: str = "",
) -> str:
    layouts = ", ".join(layout_files) if layout_files else "(free layout)"
    extra = f"\n\nAdditional user content:\n{extra_content.strip()}" if extra_content.strip() else ""
    return (
        f"Topic: {topic}\n"
        f"Target page count: {page_count}\n"
        f"Language: {language}\n"
        f"Available layout SVG basenames: {layouts}\n"
        "Plan exactly the target page count. First page cover, last page ending/closing."
        f"{extra}"
    )


def build_executor_system() -> str:
    base = _read_reference("executor-base.md", max_chars=6000)
    shared = _read_reference("shared-standards.md", max_chars=4000)
    return (
        "You are the Executor generating one complete SVG slide for ppt-master.\n"
        "Return ONLY the raw SVG element (<svg>...</svg>), no markdown.\n"
        "Canvas: ppt169 (1280x720). Embed text in SVG; do not use external fonts.\n\n"
        + base
        + "\n\n"
        + shared
    )


def build_executor_user(
    *,
    page_index: int,
    total_pages: int,
    page_title: str,
    page_brief: str,
    topic: str,
    language: str,
    layout_svg: str,
    spec_lock: str,
) -> str:
    layout_excerpt = layout_svg
    if len(layout_excerpt) > 14000:
        layout_excerpt = layout_excerpt[:14000] + "\n<!-- truncated -->"
    return (
        f"Deck topic: {topic}\n"
        f"Language: {language}\n"
        f"Page {page_index}/{total_pages}: {page_title}\n"
        f"Content brief: {page_brief}\n\n"
        "spec_lock.md:\n"
        f"{spec_lock.strip()}\n\n"
        "Reference layout SVG (inherit structure/colors, replace text/content):\n"
        f"{layout_excerpt}\n\n"
        "Output the final SVG for this page only."
    )


def write_spec_lock(project_dir: Path, pages: list[dict], defaults: dict) -> None:
    lines = [
        "# spec_lock",
        "",
        "## meta",
        f"- canvas: {defaults.get('canvas_format', 'ppt169')}",
        f"- language: {defaults.get('language', '简体中文')}",
        f"- topic: {defaults.get('topic', '')}",
        "",
        "## page_layouts",
    ]
    for i, page in enumerate(pages, 1):
        layout = page.get("layout_file") or page.get("file") or f"{i:02d}_page.svg"
        lines.append(f"P{i:02d}: {layout}")
    lines.extend(["", "## pages"])
    for i, page in enumerate(pages, 1):
        title = page.get("title") or f"Page {i}"
        brief = page.get("brief") or ""
        lines.append(f"P{i:02d}: {title} — {brief}")
    (project_dir / "spec_lock.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
