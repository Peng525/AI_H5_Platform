"""Unit tests for OCR graceful fallback in _load_source_text."""
from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, patch

from app.services.ocr.paddle_provider import OcrUnavailableError
from app.services.resume.resume_service import _load_source_text


class ResumeOcrFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_skips_jd_ocr_when_prompt_and_resume_pdf_available(self) -> None:
        db = AsyncMock()
        with patch(
            "app.services.resume.resume_service._file_source_text",
            new_callable=AsyncMock,
        ) as mock_file:
            mock_file.side_effect = [
                "【简历原文】\nPDF 简历内容",
                OcrUnavailableError("当前环境未启用图片 OCR"),
            ]
            text = await _load_source_text(db, 1, "优化方向：突出项目", file_id=10, jd_file_id=20)
        self.assertIn("优化方向", text)
        self.assertIn("PDF 简历内容", text)
        self.assertEqual(mock_file.await_count, 2)

    async def test_raises_when_only_jpg_and_no_prompt(self) -> None:
        db = AsyncMock()
        with patch(
            "app.services.resume.resume_service._file_source_text",
            new_callable=AsyncMock,
            side_effect=OcrUnavailableError("当前环境未启用图片 OCR"),
        ):
            with self.assertRaises(OcrUnavailableError):
                await _load_source_text(db, 1, None, file_id=10, jd_file_id=None)


if __name__ == "__main__":
    unittest.main()
