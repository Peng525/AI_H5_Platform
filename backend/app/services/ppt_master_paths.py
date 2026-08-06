"""ppt-master subproject path helpers."""
from __future__ import annotations

from pathlib import Path

from app.config import settings


def ppt_master_root() -> Path | None:
    configured = (settings.ppt_master_root or "").strip()
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            # Relative to backend working directory (uvicorn cwd)
            backend_cwd = Path(__file__).resolve().parents[2]
            path = (backend_cwd / path).resolve()
        return path if path.is_dir() else None

    here = Path(__file__).resolve()
    for base in (here.parents[3], here.parents[2]):
        candidate = base / "ppt-master-main"
        if candidate.is_dir():
            return candidate
    return None


def pipeline_available() -> bool:
    root = ppt_master_root()
    if not root:
        return False
    skill = root / "skills" / "ppt-master" / "SKILL.md"
    return skill.is_file()
