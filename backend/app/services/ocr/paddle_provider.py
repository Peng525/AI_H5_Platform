"""PaddleOCR wrapper with optional mock fallback."""
from __future__ import annotations

import io
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class OcrUnavailableError(Exception):
    """图片 OCR 不可用或无法识别文本。"""


_ocr_instance = None


def _get_ocr():
    global _ocr_instance
    if _ocr_instance is not None:
        return _ocr_instance
    if not settings.resume_paddleocr_enabled:
        return None
    try:
        from paddleocr import PaddleOCR

        _ocr_instance = PaddleOCR(use_angle_cls=True, lang=settings.resume_paddleocr_lang, show_log=False)
        return _ocr_instance
    except Exception as exc:
        logger.warning("PaddleOCR unavailable: %s", exc)
        return None


def extract_text_from_image_bytes(data: bytes) -> str:
    ocr = _get_ocr()
    if ocr is None:
        raise OcrUnavailableError("当前环境未启用图片 OCR，请上传 PDF 或纯文本文件")
    import numpy as np
    from PIL import Image

    img = Image.open(io.BytesIO(data)).convert("RGB")
    arr = np.array(img)
    result = ocr.ocr(arr, cls=True)
    lines: list[str] = []
    for block in result or []:
        for line in block or []:
            if line and len(line) > 1:
                lines.append(str(line[1][0]))
    return "\n".join(lines).strip()


def extract_text_from_pdf_bytes(data: bytes) -> str:
    """Text layer first; scan pages with OCR if enabled."""
    try:
        import fitz
    except ImportError as exc:
        raise OcrUnavailableError("PDF 解析组件未安装，请联系管理员") from exc

    doc = fitz.open(stream=data, filetype="pdf")
    parts: list[str] = []
    for page in doc:
        text = (page.get_text() or "").strip()
        if text:
            parts.append(text)
            continue
        if settings.resume_paddleocr_enabled:
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            try:
                parts.append(extract_text_from_image_bytes(img_bytes))
            except Exception as exc:
                logger.warning("OCR page failed: %s", exc)
    doc.close()
    return "\n\n".join(p for p in parts if p).strip()


def extract_text_from_file(path: str, mime: str, data: bytes) -> str:
    mime_l = (mime or "").lower()
    name_l = path.lower()
    if mime_l == "application/pdf" or name_l.endswith(".pdf"):
        return extract_text_from_pdf_bytes(data)
    if mime_l.startswith("image/") or name_l.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return extract_text_from_image_bytes(data)
    if name_l.endswith(".txt") or mime_l.startswith("text/"):
        return data.decode("utf-8", errors="replace").strip()
    raise ValueError(f"不支持的文件类型：{mime}")
