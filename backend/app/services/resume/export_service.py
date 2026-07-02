"""Export resume to PDF/DOCX."""
from __future__ import annotations

import io
from typing import Any


def structured_to_plain_text(structured: dict[str, Any]) -> str:
    lines: list[str] = []
    basics = structured.get("basics") or {}
    if basics.get("name"):
        lines.append(str(basics["name"]))
    contact = " · ".join(filter(None, [basics.get("phone"), basics.get("email")]))
    if contact:
        lines.append(contact)
    if basics.get("summary"):
        lines.append("")
        lines.append(str(basics["summary"]))

    exp = structured.get("experience") or []
    if exp:
        lines.append("")
        lines.append("工作经历")
        for item in exp:
            if not isinstance(item, dict):
                continue
            header = " — ".join(filter(None, [item.get("company"), item.get("title"), item.get("period")]))
            if header:
                lines.append(header)
            for b in item.get("bullets") or []:
                lines.append(f"  • {b}")

    edu = structured.get("education") or []
    if edu:
        lines.append("")
        lines.append("教育背景")
        for item in edu:
            if isinstance(item, dict):
                lines.append(" — ".join(filter(None, [item.get("school"), item.get("degree"), item.get("period")])))

    skills = structured.get("skills") or []
    if skills:
        lines.append("")
        lines.append("技能")
        if isinstance(skills, list):
            lines.append(", ".join(str(s) for s in skills))
        else:
            lines.append(str(skills))
    return "\n".join(lines).strip()


def export_docx_bytes(structured: dict[str, Any]) -> bytes:
    from docx import Document

    doc = Document()
    basics = structured.get("basics") or {}
    if basics.get("name"):
        doc.add_heading(str(basics["name"]), level=0)
    if basics.get("summary"):
        doc.add_paragraph(str(basics["summary"]))
    for item in structured.get("experience") or []:
        if not isinstance(item, dict):
            continue
        doc.add_heading(
            " — ".join(filter(None, [item.get("company"), item.get("title")])),
            level=2,
        )
        for b in item.get("bullets") or []:
            doc.add_paragraph(str(b), style="List Bullet")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def export_pdf_bytes(structured: dict[str, Any]) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 50
    for line in structured_to_plain_text(structured).split("\n"):
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line[:120])
        y -= 14
    c.save()
    return buf.getvalue()
