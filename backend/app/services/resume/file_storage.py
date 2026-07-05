"""Resume file storage on local disk."""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import settings


class FileTooLargeError(Exception):
    pass


def _root() -> Path:
    root = Path(settings.resume_data_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


def max_bytes() -> int:
    return settings.resume_max_file_mb * 1024 * 1024


def user_dir(user_id: int) -> Path:
    d = _root() / str(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_upload(user_id: int, filename: str, content: bytes, mime: str) -> tuple[str, str, int]:
    if len(content) > max_bytes():
        raise FileTooLargeError(f"文件超过 {settings.resume_max_file_mb}MB 限制")
    digest = hashlib.sha256(content).hexdigest()
    ext = Path(filename or "upload").suffix or ".bin"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    rel = f"{user_id}/{safe_name}"
    path = _root() / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return rel, digest, len(content)


def read_file(rel_path: str) -> bytes:
    path = _root() / rel_path
    if not path.is_file():
        raise FileNotFoundError(rel_path)
    return path.read_bytes()


def delete_file(rel_path: str) -> None:
    path = _root() / rel_path
    if path.is_file():
        path.unlink(missing_ok=True)


def expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.resume_retention_days)


def is_expired(expires: datetime | None) -> bool:
    if expires is None:
        return False
    now = datetime.now(timezone.utc)
    exp = expires if expires.tzinfo else expires.replace(tzinfo=timezone.utc)
    return now > exp
