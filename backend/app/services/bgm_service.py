"""BGM 曲目目录：合并静态 catalog 与本地 mp3 文件。"""
import json
import re
from pathlib import Path
from typing import Any

# app/services -> parents[2] = backend
BACKEND_DIR = Path(__file__).resolve().parents[2]
CATALOG_PATH = BACKEND_DIR / "data" / "bgm_catalog.json"
MEDIA_BGM = BACKEND_DIR / "media" / "bgm"
STATIC_BGM = BACKEND_DIR / "static" / "bgm"


def _slug_id(name: str) -> str:
    base = Path(name).stem.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or "track"


def _load_catalog() -> list[dict[str, Any]]:
    if not CATALOG_PATH.is_file():
        return []
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _discover_mp3_files() -> dict[str, Path]:
    """filename -> path under backend/static/bgm."""
    found: dict[str, Path] = {}
    if not STATIC_BGM.is_dir():
        return found
    for path in sorted(STATIC_BGM.glob("*.mp3")):
        found[path.name] = path
    return found


def list_bgm_tracks() -> list[dict[str, Any]]:
    catalog = _load_catalog()
    on_disk = _discover_mp3_files()
    by_filename: dict[str, dict[str, Any]] = {}

    for entry in catalog:
        filename = str(entry.get("filename") or "").strip()
        if not filename:
            continue
        track_id = str(entry.get("id") or _slug_id(filename))
        available = filename in on_disk
        by_filename[filename] = {
            "id": track_id,
            "title": str(entry.get("title") or filename),
            "filename": filename,
            "url": f"/static/bgm/{filename}",
            "available": available,
            "mood": entry.get("mood") if isinstance(entry.get("mood"), list) else [],
            "defaultVolume": float(entry.get("defaultVolume", 0.35)),
            "description": str(entry.get("description") or ""),
        }

    for filename, _path in on_disk.items():
        if filename in by_filename:
            continue
        by_filename[filename] = {
            "id": _slug_id(filename),
            "title": Path(filename).stem.replace("-", " ").replace("_", " "),
            "filename": filename,
            "url": f"/static/bgm/{filename}",
            "available": True,
            "mood": [],
            "defaultVolume": 0.35,
            "description": "本地曲目",
        }

    tracks = list(by_filename.values())
    tracks.sort(key=lambda t: (not t["available"], t["title"]))
    return tracks


def resolve_bgm_dir() -> Path | None:
    """挂载 backend/static/bgm 供 StaticFiles 使用。"""
    if STATIC_BGM.is_dir():
        return STATIC_BGM
    if MEDIA_BGM.is_dir():
        return MEDIA_BGM
    return None
