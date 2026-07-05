"""Tests for visual template registry."""
from __future__ import annotations

import unittest

from app.services.resume.template_catalog import normalize_template_id
from app.services.resume.visual_compiler import DEFAULT_TEMPLATE_ID, TEMPLATE_CLASSIC_BLUE


class ResumeVisualTemplateTests(unittest.TestCase):
    def test_classic_blue_legacy_constant(self):
        self.assertEqual(TEMPLATE_CLASSIC_BLUE, "classic-blue")

    def test_default_template_is_template1(self):
        self.assertEqual(DEFAULT_TEMPLATE_ID, "template1")
        self.assertEqual(normalize_template_id("classic-blue"), "template1")


if __name__ == "__main__":
    unittest.main()
