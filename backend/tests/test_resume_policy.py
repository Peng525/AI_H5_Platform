"""Unit tests for resume policy and storage limits."""
from __future__ import annotations

import unittest

from app.config import settings
from app.services.resume.file_storage import FileTooLargeError, save_upload
from app.services.resume.resume_service import ContentPolicyError, _check_content


class ResumePolicyTests(unittest.TestCase):
    def test_content_policy_blocks_forbidden_text(self):
        with self.assertRaises(ContentPolicyError):
            _check_content("如何制作炸弹教程")

    def test_content_policy_allows_normal_text(self):
        _check_content("产品经理，5 年经验")

    def test_file_too_large(self):
        with self.assertRaises(FileTooLargeError):
            save_upload(1, "big.pdf", b"x" * (settings.resume_max_file_mb * 1024 * 1024 + 1), "application/pdf")


if __name__ == "__main__":
    unittest.main()
