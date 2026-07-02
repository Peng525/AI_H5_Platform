"""Tests for resume visual_compiler."""
from __future__ import annotations

import unittest

from app.services.resume.visual_compiler import (
    compile_visual_document,
    get_bind_value,
    normalize_structured,
    set_bind_value,
)


class VisualCompilerTests(unittest.TestCase):
    def test_normalize_fills_defaults(self):
        data = normalize_structured({"basics": {"name": "张三"}})
        self.assertEqual(data["basics"]["name"], "张三")
        self.assertIn("job_intention", data)
        self.assertTrue(data["skill_bars"])

    def test_compile_preserves_styles(self):
        structured = normalize_structured({"basics": {"name": "A"}})
        existing = {"template_id": "classic-blue", "styles": {"basics.name": {"fontSize": 14}}}
        doc = compile_visual_document(structured, existing)
        self.assertEqual(doc["template_id"], "classic-blue")
        self.assertEqual(doc["styles"]["basics.name"]["fontSize"], 14)

    def test_bind_roundtrip(self):
        data = normalize_structured({})
        set_bind_value(data, "basics.name", "李四")
        self.assertEqual(get_bind_value(data, "basics.name"), "李四")
        set_bind_value(data, "honors[0]", "奖学金")
        self.assertEqual(get_bind_value(data, "honors[0]"), "奖学金")


if __name__ == "__main__":
    unittest.main()
