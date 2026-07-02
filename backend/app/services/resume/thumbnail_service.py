"""Generate resume list thumbnails as PNG previews."""
from __future__ import annotations

import io
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from app.config import settings
from app.models import ResumeProfile
from app.services.resume.file_storage import delete_file

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


def render_thumbnail_png(structured: dict[str, Any]) -> bytes:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 4], fill=ACCENT)

    basics = structured.get("basics") or {}
    name = str(basics.get("name") or "我的简历").strip()
    title_font = _load_font(22)
    body_font = _load_font(14)
    small_font = _load_font(12)

    y = MARGIN + 8
    draw.text((MARGIN, y), name[:24], font=title_font, fill=TITLE_COLOR)
    y += 32

    contact = " · ".join(filter(None, [basics.get("phone"), basics.get("email")]))
    if contact:
        draw.text((MARGIN, y), contact[:40], font=small_font, fill=BODY_COLOR)
        y += 22

    draw.line([(MARGIN, y), (WIDTH - MARGIN, y)], fill=LINE_COLOR, width=1)
    y += 16

    summary = str(basics.get("summary") or "").strip()
    if summary:
        y = _draw_wrapped(draw, MARGIN, y, summary[:300], body_font, BODY_COLOR, 28, 18)

    experience = structured.get("experience") or []
    if experience and y < HEIGHT - 80:
        y += 8
        draw.text((MARGIN, y), "工作经历", font=body_font, fill=TITLE_COLOR)
        y += 20
        for item in experience[:3]:
            if not isinstance(item, dict) or y > HEIGHT - MARGIN - 20:
                break
            header = " — ".join(filter(None, [item.get("company"), item.get("title")]))
            if header:
                draw.text((MARGIN, y), header[:35], font=small_font, fill=TITLE_COLOR)
                y += 18
            for bullet in (item.get("bullets") or [])[:2]:
                if y > HEIGHT - MARGIN - 10:
                    break
                y = _draw_wrapped(
                    draw,
                    MARGIN + 8,
                    y,
                    f"• {bullet}"[:80],
                    small_font,
                    BODY_COLOR,
                    30,
                    16,
                )

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def save_thumbnail(user_id: int, public_id: str, structured: dict[str, Any]) -> str:
    data = render_thumbnail_png(structured)
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


def refresh_profile_thumbnail(profile: ResumeProfile, structured: dict[str, Any]) -> None:
    old = profile.thumbnail_path
    profile.thumbnail_path = save_thumbnail(profile.user_id, profile.public_id, structured)
    if old and old != profile.thumbnail_path:
        delete_file(old)
