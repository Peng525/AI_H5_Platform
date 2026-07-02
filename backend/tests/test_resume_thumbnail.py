"""Unit tests for resume thumbnail rendering."""
from __future__ import annotations

from app.config import settings
from app.services.resume.thumbnail_service import render_thumbnail_png, save_thumbnail


def test_render_thumbnail_png_returns_png_bytes():
    structured = {
        "basics": {
            "name": "张三",
            "email": "zhang@example.com",
            "phone": "13800000000",
            "summary": "5 年产品经验，擅长数据分析与跨团队协作。",
        },
        "experience": [
            {
                "company": "示例科技",
                "title": "产品经理",
                "bullets": ["负责核心功能迭代", "推动 DAU 增长 20%"],
            }
        ],
    }
    data = render_thumbnail_png(structured)
    assert data.startswith(b"\x89PNG")
    assert len(data) > 500


def test_save_thumbnail_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "resume_data_dir", str(tmp_path))
    structured = {"basics": {"name": "李四", "summary": "测试简历"}}
    rel = save_thumbnail(99, "pub123", structured)
    assert rel == "99/thumbnails/pub123.png"
    path = tmp_path / rel
    assert path.is_file()
    assert path.read_bytes().startswith(b"\x89PNG")
