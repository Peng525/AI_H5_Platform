#!/usr/bin/env python3
"""Export ppt-master template cover SVGs to PNG previews for the generate page."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PPT_MASTER = ROOT / "ppt-master-main" / "skills" / "ppt-master" / "templates"
OUT_DIR = ROOT / "frontend" / "public" / "deck-templates"
BACKEND_OUT = ROOT / "backend" / "static" / "deck-templates"


def _load_index(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _entries() -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for slug in _load_index(PPT_MASTER / "layouts" / "layouts_index.json"):
        items.append(("layout", slug))
    for slug in _load_index(PPT_MASTER / "decks" / "decks_index.json"):
        items.append(("deck", slug))
    return items


def _render_svg(svg_path: Path, png_path: Path) -> bool:
    try:
        import cairosvg  # type: ignore

        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=640)
        return True
    except Exception:
        pass

    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (640, 360), (248, 250, 252))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 640, 48], fill=(37, 99, 235))
        label = png_path.stem.replace("-", " / ", 1)
        draw.text((24, 160), label[:40], fill=(30, 41, 59))
        draw.text((24, 200), svg_path.parent.name, fill=(100, 116, 139))
        img.save(png_path, "PNG")
        return True
    except Exception as exc:
        print(f"FAIL placeholder {png_path.name}: {exc}", file=sys.stderr)
        return False


def main() -> int:
    if not PPT_MASTER.is_dir():
        print(f"ppt-master templates not found: {PPT_MASTER}", file=sys.stderr)
        return 1

    for out in (OUT_DIR, BACKEND_OUT):
        out.mkdir(parents=True, exist_ok=True)

    ok = 0
    for kind, slug in _entries():
        rel_kind = "layouts" if kind == "layout" else "decks"
        cover = PPT_MASTER / rel_kind / slug / "01_cover.svg"
        if not cover.is_file():
            print(f"SKIP missing cover: {cover}")
            continue
        name = f"{kind}-{slug}.png"
        for out in (OUT_DIR, BACKEND_OUT):
            dest = out / name
            if _render_svg(cover, dest):
                ok += 1
                print(f"OK {quote(name)}")
            else:
                print(f"FAIL {name}", file=sys.stderr)
                return 1

    print(f"Exported {ok // 2} previews to {OUT_DIR} and {BACKEND_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
