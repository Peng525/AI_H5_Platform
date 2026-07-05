"""Resume business orchestration."""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import inspect as sa_inspect

from app.config import settings
from app.models import GenerationLog, ResumeFile, ResumeMessage, ResumeProfile, ResumeSidecar, ResumeVersion, User
from app.services.deck_generator import new_public_id
from app.services.llm.provider import chat_completion, extract_json
from app.services.ocr.paddle_provider import OcrUnavailableError, extract_text_from_file
from app.services.prompt_template_service import render_template
from app.services.quota import QuotaExceeded, check_and_consume
from app.services.resume import file_storage
from app.services.resume.file_storage import delete_file
from app.services.resume.thumbnail_service import refresh_profile_thumbnail
from app.services.resume.template_catalog import (
    INDUSTRIES,
    RESUME_TEMPLATES,
    VISUAL_TEMPLATES,
    ALLOWED_VISUAL_TEMPLATE_IDS,
    filter_resume_templates,
    filter_visual_templates,
    get_industry_snippet,
    normalize_template_id,
)
from app.services.resume.visual_compiler import (
    compile_visual_document,
    normalize_structured,
)

logger = logging.getLogger(__name__)

FORBIDDEN_PATTERNS = [
    r"制作.*炸弹",
    r"伪造.*证件",
    r"洗钱",
]


class ResumeLimitExceeded(Exception):
    pass


class ContentPolicyError(Exception):
    pass


class ResumeNotFoundError(Exception):
    pass


def _check_content(text: str) -> None:
    t = (text or "").lower()
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, t, re.I):
            raise ContentPolicyError("内容不符合规范，请修改后重试")


def _default_structured() -> dict[str, Any]:
    return normalize_structured({})


def _profile_versions(profile: ResumeProfile) -> list[ResumeVersion]:
    """Avoid async lazy-load when versions were not eager-loaded."""
    state = sa_inspect(profile)
    if "versions" in state.unloaded:
        return []
    return list(profile.versions)


async def count_user_profiles(db: AsyncSession, user_id: int) -> int:
    r = await db.execute(select(func.count()).select_from(ResumeProfile).where(ResumeProfile.user_id == user_id))
    return int(r.scalar() or 0)


async def get_owned_profile(db: AsyncSession, user_id: int, public_id: str) -> ResumeProfile:
    r = await db.execute(
        select(ResumeProfile)
        .where(ResumeProfile.public_id == public_id, ResumeProfile.user_id == user_id)
        .options(
            selectinload(ResumeProfile.versions),
            selectinload(ResumeProfile.messages),
            selectinload(ResumeProfile.sidecar),
        )
    )
    profile = r.scalar_one_or_none()
    if not profile:
        raise ResumeNotFoundError("简历不存在或无权访问")
    if file_storage.is_expired(profile.expires_at):
        raise ResumeNotFoundError("简历已过期，请重新创建")
    return profile


async def save_uploaded_file(db: AsyncSession, user_id: int, filename: str, content: bytes, mime: str) -> ResumeFile:
    rel, digest, size = file_storage.save_upload(user_id, filename, content, mime)
    row = ResumeFile(user_id=user_id, path=rel, mime=mime or "application/octet-stream", size_bytes=size, sha256=digest)
    db.add(row)
    await db.flush()
    return row


async def _assert_owned_file(db: AsyncSession, user_id: int, file_id: int) -> None:
    fr = await db.get(ResumeFile, file_id)
    if not fr or fr.user_id != user_id:
        raise ResumeNotFoundError("附件不存在或无权访问")


async def _file_source_text(db: AsyncSession, user_id: int, file_id: int, label: str) -> str:
    await _assert_owned_file(db, user_id, file_id)
    fr = await db.get(ResumeFile, file_id)
    raw = file_storage.read_file(fr.path)
    body = extract_text_from_file(fr.path, fr.mime, raw)
    return f"【{label}】\n{body}"


async def create_profile(
    db: AsyncSession,
    user: User,
    *,
    title: str | None = None,
    prompt: str | None = None,
    file_id: int | None = None,
    jd_file_id: int | None = None,
    template_id: str | None = None,
) -> ResumeProfile:
    count = await count_user_profiles(db, user.id)
    if count >= settings.resume_max_per_user:
        raise ResumeLimitExceeded(
            f"最多保存 {settings.resume_max_per_user} 份简历，请先在「个人简历」中删除旧简历"
        )
    if prompt:
        _check_content(prompt)
    if template_id:
        template_id = normalize_template_id(template_id)
    if template_id and template_id not in ALLOWED_VISUAL_TEMPLATE_IDS:
        raise ValueError(f"未知简历模板：{template_id}")
    profile = ResumeProfile(
        public_id=new_public_id(),
        user_id=user.id,
        title=(title or "我的简历").strip()[:255],
        status="draft",
        expires_at=file_storage.expires_at(),
    )
    db.add(profile)
    await db.flush()
    sidecar = ResumeSidecar(profile_id=profile.id, advice_json="{}", next_steps_json="[]")
    db.add(sidecar)
    if prompt and prompt.strip():
        db.add(
            ResumeMessage(
                profile_id=profile.id,
                role="user",
                content=prompt.strip(),
                message_type="prompt",
            )
        )
    if file_id:
        await _assert_owned_file(db, user.id, file_id)
    if jd_file_id:
        await _assert_owned_file(db, user.id, jd_file_id)
    if template_id:
        structured = _default_structured()
        tid = normalize_template_id(template_id) or "template1"
        visual = compile_visual_document(structured, template_id=tid)
        ver = _write_version(profile, structured, visual, version_no=1, source_file_id=file_id)
        db.add(ver)
        profile.status = "draft"
        refresh_profile_thumbnail(profile, structured, visual)
    await db.flush()
    return profile


async def _load_source_text(
    db: AsyncSession,
    user_id: int,
    prompt: str | None,
    file_id: int | None,
    jd_file_id: int | None = None,
) -> str:
    parts: list[str] = []
    if prompt and prompt.strip():
        parts.append(prompt.strip())
    if file_id:
        try:
            parts.append(await _file_source_text(db, user_id, file_id, "简历原文"))
        except OcrUnavailableError:
            logger.warning("resume file OCR unavailable file_id=%s", file_id)
    if jd_file_id:
        try:
            parts.append(await _file_source_text(db, user_id, jd_file_id, "工作描述"))
        except OcrUnavailableError:
            logger.warning("JD file OCR unavailable file_id=%s", jd_file_id)
    text = "\n\n".join(p for p in parts if p).strip()
    if not text:
        if file_id or jd_file_id:
            raise OcrUnavailableError("请提供可识别的简历内容（上传 PDF、纯文本或填写提示词）")
        raise ValueError("请填写提示词或上传简历文件")
    _check_content(text)
    return text


async def _parse_structured(source_text: str, tier: str) -> dict[str, Any]:
    messages = render_template("resume_parse.yaml", {"source_text": source_text})
    raw, _, _ = await chat_completion(messages, tier=tier)
    try:
        data = extract_json(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {**_default_structured(), "basics": {**_default_structured()["basics"], "summary": source_text[:2000]}}


async def _diagnose(structured: dict[str, Any], prompt: str, tier: str) -> str:
    messages = render_template(
        "resume_diagnose.yaml",
        {"structured_json": json.dumps(structured, ensure_ascii=False), "user_prompt": prompt},
    )
    text, _, _ = await chat_completion(messages, tier=tier)
    return text.strip()


async def _generate_resume(
    structured: dict[str, Any],
    diagnosis: str,
    prompt: str,
    tier: str,
    *,
    industry_snippet: str = "",
) -> dict[str, Any]:
    messages = render_template(
        "resume_generate.yaml",
        {
            "structured_json": json.dumps(structured, ensure_ascii=False),
            "diagnosis": diagnosis,
            "user_prompt": prompt,
            "industry_snippet": industry_snippet or "突出量化成就与岗位关键词对齐。",
        },
    )
    raw, _, _ = await chat_completion(messages, tier=tier)
    try:
        data = extract_json(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return structured


async def _sidecar_from_llm(structured: dict[str, Any], diagnosis: str, tier: str) -> tuple[dict, list]:
    messages = render_template(
        "resume_advice.yaml",
        {"structured_json": json.dumps(structured, ensure_ascii=False), "diagnosis": diagnosis},
    )
    raw, _, _ = await chat_completion(messages, tier=tier)
    try:
        data = extract_json(raw)
        if isinstance(data, dict):
            return data.get("advice") or {}, data.get("next_steps") or []
    except Exception:
        pass
    return {"summary": diagnosis[:500]}, ["Review diagnosis and refine resume"]


async def _log_generation(db: AsyncSession, user_id: int, success: bool, message: str, model: str = "") -> None:
    db.add(
        GenerationLog(
            project_id=None,
            template_id="resume",
            channel="resume",
            model=model or "resume",
            success=1 if success else 0,
            message=message[:2000],
        )
    )


async def run_generate(
    db: AsyncSession,
    user: User,
    public_id: str,
    *,
    prompt: str | None = None,
    file_id: int | None = None,
    jd_file_id: int | None = None,
    template_id: str | None = None,
    prompt_template_id: str | None = None,
    industry_id: str | None = None,
) -> dict[str, Any]:
    tid = normalize_template_id(template_id)
    if not tid:
        raise ValueError("请选择简历模板")
    if tid not in ALLOWED_VISUAL_TEMPLATE_IDS:
        raise ValueError(f"未知简历模板：{tid}")
    profile = await get_owned_profile(db, user.id, public_id)
    tier = user.tier or "free"
    source_text = await _load_source_text(db, user.id, prompt, file_id, jd_file_id)
    industry_snippet = get_industry_snippet(prompt_template_id)

    try:
        structured_in = await _parse_structured(source_text, tier)
        diagnosis = await _diagnose(structured_in, source_text, tier)
        structured_out = normalize_structured(
            await _generate_resume(structured_in, diagnosis, source_text, tier, industry_snippet=industry_snippet)
        )
        advice, next_steps = await _sidecar_from_llm(structured_out, diagnosis, tier)

        prev_visual = _latest_visual(profile) if _profile_versions(profile) else {}
        prev_visual = {**prev_visual, "template_id": tid}
        version_no = max((v.version_no for v in _profile_versions(profile)), default=0) + 1
        ver = _write_version(profile, structured_out, prev_visual, version_no=version_no, source_file_id=file_id)
        db.add(ver)

        if prompt and prompt.strip():
            db.add(
                ResumeMessage(
                    profile_id=profile.id,
                    role="user",
                    content=prompt.strip(),
                    message_type="prompt",
                )
            )
        if industry_id or prompt_template_id:
            meta = json.dumps(
                {"industry_id": industry_id, "prompt_template_id": prompt_template_id, "template_id": tid},
                ensure_ascii=False,
            )
            db.add(
                ResumeMessage(
                    profile_id=profile.id,
                    role="system",
                    content=meta,
                    message_type="meta",
                )
            )

        db.add(
            ResumeMessage(
                profile_id=profile.id,
                role="assistant",
                content=diagnosis,
                message_type="diagnosis",
            )
        )
        db.add(
            ResumeMessage(
                profile_id=profile.id,
                role="assistant",
                content="已根据诊断生成新版简历，请查看中间预览区。",
                message_type="generate",
            )
        )

        if profile.sidecar:
            profile.sidecar.advice_json = json.dumps(advice, ensure_ascii=False)
            profile.sidecar.next_steps_json = json.dumps(next_steps, ensure_ascii=False)
        profile.status = "ready"
        profile.updated_at = datetime.now(timezone.utc)
        visual_doc = compile_visual_document(structured_out, {**prev_visual, "template_id": tid})
        refresh_profile_thumbnail(profile, structured_out, visual_doc)
        await check_and_consume(db, user.id, tier)
        await _log_generation(db, user.id, True, f"generate {public_id} v{version_no}")
        await db.commit()
        profile = await get_owned_profile(db, user.id, public_id)
        return _profile_payload(profile)
    except QuotaExceeded:
        raise
    except Exception as exc:
        await _log_generation(db, user.id, False, str(exc))
        await db.rollback()
        raise


async def run_optimize(db: AsyncSession, user: User, public_id: str, prompt: str) -> dict[str, Any]:
    if not prompt or not prompt.strip():
        raise ValueError("请填写优化说明")
    _check_content(prompt)
    profile = await get_owned_profile(db, user.id, public_id)
    tier = user.tier or "free"

    current = max(_profile_versions(profile), key=lambda v: v.version_no, default=None)
    structured = _default_structured()
    if current:
        try:
            structured = json.loads(current.structured_json or "{}")
        except json.JSONDecodeError:
            pass

    db.add(ResumeMessage(profile_id=profile.id, role="user", content=prompt.strip(), message_type="optimize_request"))

    try:
        rendered = render_template(
            "resume_optimize.yaml",
            {
                "structured_json": json.dumps(structured, ensure_ascii=False),
                "user_prompt": prompt.strip(),
            },
        )
        raw, _, model = await chat_completion(rendered, tier=tier)
        try:
            structured_out = extract_json(raw)
            if not isinstance(structured_out, dict):
                structured_out = structured
        except Exception:
            structured_out = structured
        structured_out = normalize_structured(structured_out)

        diagnosis = raw if isinstance(raw, str) else json.dumps(structured_out, ensure_ascii=False)
        advice, next_steps = await _sidecar_from_llm(structured_out, diagnosis, tier)

        prev_visual = _latest_visual(profile)
        version_no = max((v.version_no for v in _profile_versions(profile)), default=0) + 1
        ver = _write_version(profile, structured_out, prev_visual, version_no=version_no)
        db.add(ver)
        db.add(
            ResumeMessage(
                profile_id=profile.id,
                role="assistant",
                content=diagnosis[:4000],
                message_type="optimize",
            )
        )
        if profile.sidecar:
            profile.sidecar.advice_json = json.dumps(advice, ensure_ascii=False)
            profile.sidecar.next_steps_json = json.dumps(next_steps, ensure_ascii=False)
        profile.updated_at = datetime.now(timezone.utc)
        visual_doc = compile_visual_document(structured_out, prev_visual)
        refresh_profile_thumbnail(profile, structured_out, visual_doc)
        await check_and_consume(db, user.id, tier)
        await _log_generation(db, user.id, True, f"optimize {public_id} v{version_no}", model=model or "")
        await db.commit()
        profile = await get_owned_profile(db, user.id, public_id)
        return _profile_payload(profile)
    except QuotaExceeded:
        raise
    except Exception as exc:
        await _log_generation(db, user.id, False, str(exc))
        await db.rollback()
        raise


def _latest_visual(profile: ResumeProfile) -> dict[str, Any]:
    versions = _profile_versions(profile)
    if not versions:
        return compile_visual_document(_default_structured())
    ver = max(versions, key=lambda v: v.version_no)
    structured = _latest_structured(profile)
    if ver.visual_document_json:
        try:
            existing = json.loads(ver.visual_document_json)
            if isinstance(existing, dict):
                return compile_visual_document(structured, existing)
        except json.JSONDecodeError:
            pass
    return compile_visual_document(structured)


def _write_version(
    profile: ResumeProfile,
    structured: dict[str, Any],
    visual: dict[str, Any],
    *,
    version_no: int | None = None,
    source_file_id: int | None = None,
) -> ResumeVersion:
    structured_norm = normalize_structured(structured)
    visual_doc = compile_visual_document(structured_norm, visual)
    payload = json.dumps(structured_norm, ensure_ascii=False)
    visual_payload = json.dumps(visual_doc, ensure_ascii=False)
    if version_no is None:
        version_no = max((v.version_no for v in _profile_versions(profile)), default=0) + 1
    ver = ResumeVersion(
        profile_id=profile.id,
        version_no=version_no,
        structured_json=payload,
        visual_document_json=visual_payload,
        source_file_id=source_file_id,
    )
    versions = _profile_versions(profile)
    db_ver = max(versions, key=lambda v: v.version_no, default=None) if versions else None
    if db_ver and version_no == db_ver.version_no:
        db_ver.structured_json = payload
        db_ver.visual_document_json = visual_payload
        if source_file_id is not None:
            db_ver.source_file_id = source_file_id
        return db_ver
    return ver


def _latest_structured(profile: ResumeProfile) -> dict[str, Any]:
    versions = _profile_versions(profile)
    if not versions:
        return _default_structured()
    ver = max(versions, key=lambda v: v.version_no)
    try:
        data = json.loads(ver.structured_json or "{}")
        return normalize_structured(data if isinstance(data, dict) else {})
    except json.JSONDecodeError:
        return _default_structured()


def _profile_payload(profile: ResumeProfile) -> dict[str, Any]:
    sidecar = profile.sidecar
    advice = {}
    next_steps = []
    if sidecar:
        try:
            advice = json.loads(sidecar.advice_json or "{}")
        except json.JSONDecodeError:
            advice = {}
        try:
            next_steps = json.loads(sidecar.next_steps_json or "[]")
        except json.JSONDecodeError:
            next_steps = []
    ver = max(_profile_versions(profile), key=lambda v: v.version_no, default=None)
    return {
        "public_id": profile.public_id,
        "title": profile.title,
        "status": profile.status,
        "version_no": ver.version_no if ver else 0,
        "structured": _latest_structured(profile),
        "visual_document": _latest_visual(profile),
        "sidecar": {"advice": advice, "next_steps": next_steps},
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


async def save_profile(
    db: AsyncSession,
    user_id: int,
    public_id: str,
    *,
    title: str | None = None,
    structured: dict[str, Any] | None = None,
    visual_document: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = await get_owned_profile(db, user_id, public_id)
    if title:
        profile.title = title.strip()[:255]
    if structured is not None or visual_document is not None:
        ver = max(_profile_versions(profile), key=lambda v: v.version_no, default=None)
        cur_structured = normalize_structured(_latest_structured(profile) if structured is None else structured)
        cur_visual = visual_document if visual_document is not None else _latest_visual(profile)
        if ver:
            _write_version(profile, cur_structured, cur_visual, version_no=ver.version_no)
        else:
            db.add(_write_version(profile, cur_structured, cur_visual, version_no=1))
        refresh_profile_thumbnail(profile, cur_structured, compile_visual_document(cur_structured, cur_visual))
    profile.updated_at = datetime.now(timezone.utc)
    await db.commit()
    profile = await get_owned_profile(db, user_id, public_id)
    return _profile_payload(profile)


def list_item_payload(profile: ResumeProfile) -> dict[str, Any]:
    thumb = f"/api/v1/resume/{profile.public_id}/thumbnail" if profile.thumbnail_path else ""
    return {
        "public_id": profile.public_id,
        "title": profile.title,
        "thumbnail_url": thumb,
        "status": profile.status,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


async def delete_profile(db: AsyncSession, user_id: int, public_id: str) -> None:
    profile = await get_owned_profile(db, user_id, public_id)
    if profile.thumbnail_path:
        delete_file(profile.thumbnail_path)
    await db.delete(profile)
    await db.flush()
