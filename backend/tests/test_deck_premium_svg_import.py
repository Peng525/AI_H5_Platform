"""Tests for premium SVG → H5 canvas import."""
from pathlib import Path

from app.services.deck_premium_svg_import import (
    build_slides_from_svgs,
    list_premium_svg_files,
    resolve_premium_svg_dir,
)


def test_build_slides_from_svgs_creates_full_canvas_image(tmp_path: Path):
    svg_dir = tmp_path / "svg_final"
    svg_dir.mkdir()
    svg_path = svg_dir / "01_cover.svg"
    svg_path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">'
        '<text x="100" y="100">Hello</text></svg>',
        encoding="utf-8",
    )
    pages = [{"title": "封面", "brief": "test"}]
    slides = build_slides_from_svgs([svg_path], pages)
    assert len(slides) == 1
    assert slides[0]["title"] == "封面"
    elements = slides[0]["canvas_elements"]
    assert len(elements) == 1
    el = elements[0]
    assert el["type"] == "image"
    assert el["width"] == 1280
    assert el["height"] == 720
    assert el["content"].startswith("data:image/svg+xml;base64,")


def test_resolve_premium_svg_dir_prefers_final(tmp_path: Path):
    (tmp_path / "svg_output").mkdir()
    (tmp_path / "svg_output" / "01.svg").write_text("<svg/>", encoding="utf-8")
    final = tmp_path / "svg_final"
    final.mkdir()
    (final / "01.svg").write_text("<svg/>", encoding="utf-8")
    assert resolve_premium_svg_dir(tmp_path) == final


def test_list_premium_svg_files_natural_sort(tmp_path: Path):
    svg_dir = tmp_path / "svg_final"
    svg_dir.mkdir()
    for name in ("10_page.svg", "02_page.svg", "01_cover.svg"):
        (svg_dir / name).write_text("<svg/>", encoding="utf-8")
    files = list_premium_svg_files(tmp_path)
    assert [p.name for p in files] == ["01_cover.svg", "02_page.svg", "10_page.svg"]
