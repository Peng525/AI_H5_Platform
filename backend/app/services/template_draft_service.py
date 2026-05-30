"""管理端模板可视化编辑：草稿项目与保存预设。"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Project, Slide, User
from app.schemas import parse_project_settings, project_settings_out
from app.services.deck_generator import new_share_slug
from app.services.h5_template_service import H5TemplateError, get_template, update_template


class TemplateDraftError(Exception):
    pass


def _slide_to_template_seed(slide: Slide, canvas_background: str | None) -> dict[str, Any]:
    bullets = json.loads(slide.bullets_json or "[]")
    try:
        canvas_elements = json.loads(slide.canvas_json or "[]")
        if not isinstance(canvas_elements, list):
            canvas_elements = []
    except json.JSONDecodeError:
        canvas_elements = []
    chat_script = None
    try:
        parsed = json.loads(slide.chat_script_json or "{}")
        if isinstance(parsed, dict) and (parsed.get("enabled") or parsed.get("timeline") or parsed.get("messages")):
            chat_script = parsed
    except json.JSONDecodeError:
        chat_script = None
    seed: dict[str, Any] = {
        "title": slide.title,
        "subtitle": slide.subtitle,
        "layout": slide.layout,
        "bullets": bullets,
        "speakerNotes": slide.speaker_notes,
        "animation": slide.animation,
        "canvas_elements": canvas_elements,
    }
    if canvas_background:
        seed["canvas_background"] = canvas_background
    if chat_script:
        seed["chat_script"] = chat_script
    return seed


def project_to_template_payload(project: Project) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    slides = sorted(project.slides, key=lambda s: s.sort_order)
    settings = project_settings_out(project)
    bg_map = settings.slideBackgrounds or {}
    slides_json = [
        _slide_to_template_seed(s, bg_map.get(str(s.id)))
        for s in slides
    ]
    settings_dict = settings.model_dump()
    settings_dict.pop("slideBackgrounds", None)
    return slides_json, settings_dict


async def _seed_project_slides(
    db: AsyncSession,
    project: Project,
    slides_seed: list[dict],
    template_settings: dict,
) -> None:
    for slide in list(project.slides):
        await db.delete(slide)
    await db.flush()

    if not slides_seed:
        db.add(
            Slide(
                project_id=project.id,
                sort_order=0,
                layout="title",
                title=project.title,
                subtitle="点击右侧 AI 生图或手动编辑",
                bullets_json="[]",
            )
        )
        project.settings_json = json.dumps(template_settings or {}, ensure_ascii=False)
        await db.flush()
        return

    for idx, s in enumerate(slides_seed):
        canvas_elements = s.get("canvas_elements") or []
        chat_script = s.get("chat_script") or {}
        db.add(
            Slide(
                project_id=project.id,
                sort_order=idx,
                layout=s.get("layout", "bullets"),
                title=s.get("title", ""),
                subtitle=s.get("subtitle", ""),
                bullets_json=json.dumps(s.get("bullets", []), ensure_ascii=False),
                speaker_notes=s.get("speakerNotes", s.get("speaker_notes", "")),
                animation=s.get("animation", "fade"),
                canvas_json=json.dumps(canvas_elements, ensure_ascii=False),
                chat_script_json=json.dumps(chat_script, ensure_ascii=False),
            )
        )
    await db.flush()
    await db.refresh(project, attribute_names=["slides"])

    backgrounds: dict[str, str] = {}
    sorted_slides = sorted(project.slides, key=lambda x: x.sort_order)
    for slide, seed in zip(sorted_slides, slides_seed):
        bg = seed.get("canvas_background")
        if bg:
            backgrounds[str(slide.id)] = bg
    merged = {**(template_settings or {})}
    if backgrounds:
        merged["slideBackgrounds"] = {
            **(merged.get("slideBackgrounds") or {}),
            **backgrounds,
        }
    project.settings_json = json.dumps(merged, ensure_ascii=False)


async def get_or_create_template_draft(
    db: AsyncSession,
    template_id: str,
    admin: User,
) -> Project:
    tpl = await get_template(db, template_id)
    if not tpl:
        raise TemplateDraftError("模板不存在")

    result = await db.execute(
        select(Project)
        .where(
            Project.user_id == admin.id,
            Project.template_source_id == template_id,
        )
        .options(selectinload(Project.slides))
        .order_by(Project.updated_at.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    slides_seed = tpl.get("slides_json") or []
    template_settings = tpl.get("settings_json") or {}
    project = Project(
        title=tpl.get("title") or template_id,
        theme=template_id,
        share_slug=new_share_slug(),
        user_id=admin.id,
        template_source_id=template_id,
        settings_json=json.dumps(template_settings, ensure_ascii=False),
    )
    db.add(project)
    await db.flush()
    await _seed_project_slides(db, project, slides_seed, template_settings)
    await db.refresh(project, attribute_names=["slides"])
    return project


async def get_owned_template_draft(
    db: AsyncSession,
    template_id: str,
    project_id: int,
    admin: User,
) -> Project:
    result = await db.execute(
        select(Project)
        .where(
            Project.id == project_id,
            Project.user_id == admin.id,
            Project.template_source_id == template_id,
        )
        .options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise TemplateDraftError("模板草稿项目不存在或无权访问")
    return project


async def save_template_preset(
    db: AsyncSession,
    template_id: str,
    project_id: int,
    admin: User,
    meta: dict[str, Any] | None = None,
) -> dict:
    project = await get_owned_template_draft(db, template_id, project_id, admin)
    slides_json, settings_json = project_to_template_payload(project)
    patch: dict[str, Any] = {
        "slides_json": slides_json,
        "settings_json": settings_json,
        "pages": len(slides_json) or 1,
    }
    if meta:
        for key in (
            "title",
            "description",
            "category",
            "device",
            "premium",
            "cover_gradient",
            "default_viewport",
            "sort_order",
            "enabled",
        ):
            if key in meta and meta[key] is not None:
                patch[key] = meta[key]
    try:
        return await update_template(db, template_id, patch)
    except H5TemplateError as exc:
        raise TemplateDraftError(str(exc)) from exc


async def apply_parsed_template_to_draft(
    db: AsyncSession,
    template_id: str,
    project_id: int,
    admin: User,
    parsed: dict[str, Any],
) -> Project:
    project = await get_owned_template_draft(db, template_id, project_id, admin)
    slides_seed = parsed.get("slides_json") or []
    template_settings = parsed.get("settings_json") or parse_project_settings(project.settings_json)
    if parsed.get("default_viewport"):
        template_settings = {**template_settings, "viewportId": parsed["default_viewport"]}
    await _seed_project_slides(db, project, slides_seed, template_settings)
    if parsed.get("title"):
        project.title = parsed["title"]
    await db.flush()
    await db.refresh(project, attribute_names=["slides"])
    return project
