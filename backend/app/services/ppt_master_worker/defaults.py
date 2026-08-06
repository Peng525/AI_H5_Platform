"""Product defaults for ppt-master eight confirmations (auto-applied, no blocking UI)."""
from __future__ import annotations

from typing import Any


def build_design_defaults(
    *,
    topic: str,
    page_count: int,
    language: str,
    canvas_format: str = "ppt169",
    template_title: str = "",
) -> dict[str, Any]:
    return {
        "canvas_format": canvas_format,
        "page_count": max(1, min(30, page_count)),
        "language": language or "简体中文",
        "topic": topic,
        "style": template_title or "professional",
        "audience": "general",
        "tone": "clear and engaging",
        "image_policy": "minimal",
        "animation": "default_global",
    }
