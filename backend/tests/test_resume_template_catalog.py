"""Tests for resume template catalog and generate validation."""
from __future__ import annotations

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.resume.template_catalog import (
    ALLOWED_VISUAL_TEMPLATE_IDS,
    RESUME_TEMPLATES,
    VISUAL_TEMPLATES,
    filter_resume_templates,
    filter_visual_templates,
    get_industry_snippet,
    normalize_template_id,
)
from app.services.resume.visual_compiler import compile_visual_document


class TemplateCatalogTests(unittest.TestCase):
    def test_resume_templates_count(self):
        self.assertGreaterEqual(len(RESUME_TEMPLATES), 12)

    def test_visual_templates_seven(self):
        self.assertEqual(len(VISUAL_TEMPLATES), 7)
        ids = {t["id"] for t in VISUAL_TEMPLATES}
        self.assertIn("template4", ids)
        for t in VISUAL_TEMPLATES:
            self.assertTrue(t.get("preview_url"))

    def test_classic_blue_alias(self):
        self.assertEqual(normalize_template_id("classic-blue"), "template1")
        self.assertIn("classic-blue", ALLOWED_VISUAL_TEMPLATE_IDS)

    def test_industry_filter_prompt_templates(self):
        tech = filter_resume_templates("tech")
        self.assertTrue(all(t.get("industry_id") == "tech" for t in tech))
        self.assertGreater(len(tech), 0)

    def test_industry_filter_visual_templates(self):
        design = filter_visual_templates("design")
        self.assertTrue(all("design" in (t.get("industry_tags") or []) for t in design))

    def test_industry_snippet(self):
        snippet = get_industry_snippet("backend")
        self.assertIn("后端", snippet)

    def test_compile_normalizes_template_id(self):
        doc = compile_visual_document({}, template_id="classic-blue")
        self.assertEqual(doc["template_id"], "template1")


class RunGenerateTemplateTests(unittest.TestCase):
    def test_run_generate_requires_template_id(self):
        from app.services.resume import resume_service

        async def _run():
            db = AsyncMock()
            user = MagicMock(id=1, tier="free")
            with patch.object(resume_service, "get_owned_profile", new=AsyncMock()):
                with self.assertRaises(ValueError) as ctx:
                    await resume_service.run_generate(db, user, "abc", template_id=None)
                self.assertIn("请选择简历模板", str(ctx.exception))

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
