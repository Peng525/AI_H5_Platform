"""ppt-master project workspace paths."""
from __future__ import annotations

import re
from pathlib import Path

from app.config import settings
from app.services.ppt_master_paths import ppt_master_root


def workspace_root() -> Path:
    configured = (settings.ppt_master_workspace or "").strip()
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            backend_cwd = Path(__file__).resolve().parents[3]
            path = (backend_cwd / path).resolve()
    else:
        backend_cwd = Path(__file__).resolve().parents[3]
        path = (backend_cwd / "data" / "ppt_master_projects").resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def scripts_dir() -> Path:
    root = ppt_master_root()
    if not root:
        raise RuntimeError("ppt-master root not found; set PPT_MASTER_ROOT")
    skill_scripts = root / "skills" / "ppt-master" / "scripts"
    if not skill_scripts.is_dir():
        raise RuntimeError(f"ppt-master scripts missing: {skill_scripts}")
    return skill_scripts


def templates_root() -> Path:
    root = ppt_master_root()
    if not root:
        raise RuntimeError("ppt-master root not found")
    path = root / "skills" / "ppt-master" / "templates"
    if not path.is_dir():
        raise RuntimeError(f"ppt-master templates missing: {path}")
    return path


def resolve_template_dir(source_path: str | None) -> Path | None:
    if not source_path:
        return None
    if source_path.startswith("imported/decks/"):
        from app.services.deck.pptx_deck_template_import import imported_decks_root

        slug = source_path.removeprefix("imported/decks/").strip("/")
        candidate = imported_decks_root() / "decks" / slug
        return candidate if candidate.is_dir() else None
    rel = source_path.removeprefix("templates/").strip("/")
    try:
        candidate = templates_root() / rel
    except RuntimeError:
        return None
    return candidate if candidate.is_dir() else None


def list_layout_svgs(template_dir: Path) -> list[str]:
    files = sorted(p.name for p in template_dir.glob("*.svg") if p.is_file())
    return files


def pick_layout_for_page(layout_files: list[str], page_index: int, total: int) -> str:
    """Map page index (1-based) to a layout SVG basename."""
    if not layout_files:
        return f"{page_index:02d}_page.svg"

    cover = next((f for f in layout_files if "cover" in f.lower()), layout_files[0])
    ending = next((f for f in layout_files if "ending" in f.lower()), layout_files[-1])
    toc = next((f for f in layout_files if "toc" in f.lower() or "chapter" in f.lower()), None)
    content = next((f for f in layout_files if "content" in f.lower()), None)

    if page_index == 1:
        return cover
    if page_index == total:
        return ending
    if page_index == 2 and toc:
        return toc
    if content:
        return content
    mid = [f for f in layout_files if f not in {cover, ending, toc} and f]
    if mid:
        return mid[(page_index - 2) % len(mid)]
    return layout_files[min(page_index - 1, len(layout_files) - 1)]


def parse_init_stdout(stdout: str) -> Path | None:
    for line in stdout.splitlines():
        m = re.search(r"Project created:\s*(.+)", line)
        if m:
            return Path(m.group(1).strip())
        m = re.search(r"\[OK\] Project initialized:\s*(.+)", line)
        if m:
            return Path(m.group(1).strip())
    return None
