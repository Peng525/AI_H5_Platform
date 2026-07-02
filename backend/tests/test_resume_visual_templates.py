"""Tests for visual template registry."""
from __future__ import annotations

import unittest

from app.services.resume.visual_compiler import TEMPLATE_CLASSIC_BLUE


class ResumeVisualTemplateTests(unittest.TestCase):
    def test_classic_blue_template_id(self):
        self.assertEqual(TEMPLATE_CLASSIC_BLUE, "classic-blue")


if __name__ == "__main__":
    unittest.main()
