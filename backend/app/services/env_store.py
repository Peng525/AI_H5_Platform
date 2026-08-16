"""读写 .env 并同步进程内配置。"""
from __future__ import annotations

import os
import re
from pathlib import Path

from app.config import Settings, settings

ENV_TO_FIELD: dict[str, str] = {
    "LLM_DEFAULT_CHANNEL": "llm_default_channel",
    "LLM_AUTO_ORDER": "llm_auto_order",
    "LLM_TIMEOUT": "llm_timeout",
    "LLM_PROVIDERS_JSON": "llm_providers_json",
    "LLM_MODEL_FREE": "llm_model_free",
    "LLM_MODEL_PRO": "llm_model_pro",
    "LLM_IMAGE_MODEL_FREE": "llm_image_model_free",
    "LLM_IMAGE_MODEL_PRO": "llm_image_model_pro",
    "FREE_QUOTA_PER_USER": "free_quota_per_user",
    "ADMIN_USERNAMES": "admin_usernames",
}

FIELD_TO_ENV = {v: k for k, v in ENV_TO_FIELD.items()}

_ENV_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def env_file_path() -> Path:
    raw = os.environ.get("ENV_PERSIST_PATH") or settings.env_persist_path
    path = Path(raw)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return f"****{value[-4:]}"


def update_env_file(updates: dict[str, str]) -> None:
    """更新 .env 文件；仅写入传入的键。"""
    path = env_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    else:
        raw_lines = []

    touched: set[str] = set()
    out: list[str] = []

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out.append(line)
            continue
        m = _ENV_LINE.match(stripped)
        if not m:
            out.append(line)
            continue
        key, _ = m.group(1), m.group(2)
        if key in updates:
            out.append(f"{key}={updates[key]}")
            touched.add(key)
        else:
            out.append(line)

    for key, val in updates.items():
        if key not in touched:
            out.append(f"{key}={val}")

    path.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")

    for key, val in updates.items():
        os.environ[key] = val


def reload_app_settings() -> None:
    fresh = Settings()
    for name in Settings.model_fields:
        setattr(settings, name, getattr(fresh, name))


def apply_settings_patch(field_values: dict[str, str | int | float]) -> None:
    """将 Pydantic 字段名映射为 .env 并持久化、热更新。"""
    env_updates: dict[str, str] = {}
    for field, val in field_values.items():
        env_key = FIELD_TO_ENV.get(field)
        if env_key is None:
            continue
        env_updates[env_key] = str(val)
    if not env_updates:
        return
    update_env_file(env_updates)
    reload_app_settings()
