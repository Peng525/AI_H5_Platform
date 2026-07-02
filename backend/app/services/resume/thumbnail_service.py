"""Generate resume list thumbnails as PNG previews."""
from __future__ import annotations

import io
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from app.config import settings
from app.services.resume.visual_compiler import normalize_structured

WIDTH = 360
HEIGHT = 480
MARGIN = 24
BG = (255, 255, 255)
TITLE_COLOR = (22, 28, 45)
BODY_COLOR = (71, 85, 105)
ACCENT = (37, 99, 235)
LINE_COLOR = (226, 232, 240)


def _data_root() -> Path:
    root = Path(settings.resume_data_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _font_candidates() -> list[Path]:
    return [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/msyhbd.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
    ]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _font_candidates():
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    wrap_width: int,
    line_height: int,
) -> int:
    for para in (text or "").split("\n"):
        if not para.strip():
            y += line_height // 2
            continue
        for line in textwrap.wrap(para, width=wrap_width):
            if y > HEIGHT - MARGIN:
                return y
            draw.text((x, y), line, font=font, fill=fill)
            y += line_height
    return y


def render_thumbnail_png(structured: dict[str, Any], visual: dict[str, Any] | None = None) -> bytes:
    data = normalize_structured(structured)
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 4], fill=ACCENT)

    basics = data.get("basics") or {}
    title_font = _load_font(16)
    body_font = _load_font(11)
    small_font = _load_font(10)

    y = MARGIN
    draw.text((MARGIN, y), "个人简历", font=title_font, fill=TITLE_COLOR)
    y += 24
    draw.rectangle([MARGIN, y, WIDTH - MARGIN, y + 16], fill=ACCENT)
    draw.text((MARGIN + 6, y + 2), "基本信息", font=small_font, fill=(255, 255, 255))
    y += 24

    name = str(basics.get("name") or "我的简历").strip()
    draw.text((MARGIN, y), name[:20], font=body_font, fill=TITLE_COLOR)
    y += 18
    contact = " · ".join(filter(None, [basics.get("phone"), basics.get("email")]))
    if contact:
        draw.text((MARGIN, y), contact[:38], font=small_font, fill=BODY_COLOR)
        y += 18

    if y < HEIGHT - 60:
        draw.rectangle([MARGIN, y, WIDTH - MARGIN, y + 16], fill=ACCENT)
        draw.text((MARGIN + 6, y + 2), "工作经历", font=small_font, fill=(255, 255, 255))
        y += 22
        for item in (data.get("experience") or [])[:2]:
            if not isinstance(item, dict) or y > HEIGHT - MARGIN - 16:
                break
            header = " | ".join(filter(None, [item.get("period"), item.get("company")]))
            if header:
                draw.text((MARGIN, y), header[:36], font=small_font, fill=TITLE_COLOR)
                y += 16

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def save_thumbnail(user_id: int, public_id: str, structured: dict[str, Any], visual: dict[str, Any] | None = None) -> str:
    data = render_thumbnail_png(structured, visual)
    rel = f"{user_id}/thumbnails/{public_id}.png"
    path = _data_root() / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return rel


def read_thumbnail(rel_path: str) -> bytes:
    path = _data_root() / rel_path
    if not path.is_file():
        raise FileNotFoundError(rel_path)
    return path.read_bytes()


def refresh_profile_thumbnail(
    profile: ResumeProfile,
    structured: dict[str, Any],
    visual: dict[str, Any] | None = None,
) -> None:
    old = profile.thumbnail_path
    profile.thumbnail_path = save_thumbnail(profile.user_id, profile.public_id, structured, visual)
    if old and old != profile.thumbnail_path:
        delete_file(old)
