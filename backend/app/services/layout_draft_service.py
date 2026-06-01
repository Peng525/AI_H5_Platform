"""管理端版式可视化编辑：草稿项目与保存。"""
from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Project, User
from app.schemas import project_settings_out
from app.services.deck_generator import new_share_slug
from app.services.layout_block_service import LayoutBlockError, create_block, get_block, update_block
from app.services.template_draft_service import _seed_project_slides

LAYOUT_DRAFT_PREFIX = "layout:"


class LayoutDraftError(Exception):
    pass


def layout_source_id(block_id: str) -> str:
    return f"{LAYOUT_DRAFT_PREFIX}{block_id}"


def parse_layout_source(source: str | None) -> str | None:
    if source and source.startswith(LAYOUT_DRAFT_PREFIX):
        return source[len(LAYOUT_DRAFT_PREFIX) :]
    return None


def _is_web_viewport(viewport_id: str | None) -> bool:
    v = (viewport_id or "").lower()
    return v.startswith("web") or "1280" in v


async def get_or_create_layout_draft(
    db: AsyncSession,
    block_id: str,
    admin: User,
    seed: dict[str, Any] | None = None,
) -> Project:
    source_id = layout_source_id(block_id)
    result = await db.execute(
        select(Project)
        .where(
            Project.user_id == admin.id,
            Project.template_source_id == source_id,
        )
        .options(selectinload(Project.slides))
        .order_by(Project.updated_at.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    block = await get_block(db, block_id)
    if block:
        meta = block
        elements = block.get("elements") or []
        elements_web = block.get("elements_web") or []
        canvas_background = block.get("canvas_background") or ""
    elif seed:
        meta = seed
        elements = seed.get("elements") or []
        elements_web = seed.get("elements_web") or []
        canvas_background = seed.get("canvas_background") or ""
    else:
        raise LayoutDraftError("版式不存在，且未提供画布元素快照")

    if not elements and not elements_web:
        raise LayoutDraftError("版式至少需要手机端或网页端画布元素")

    default_settings = {
        "viewportId": "mobile-375",
        "scrollEffect": "page",
        "themeId": "zjy-minimal",
        "showScrollHint": False,
        "defaultChatTapToContinue": True,
        "bgm": {"enabled": False, "trackId": "", "url": "", "loop": True, "volume": 0.35},
    }
    project = Project(
        title=meta.get("label") or block_id,
        theme=f"layout-{block_id}",
        share_slug=new_share_slug(),
        user_id=admin.id,
        template_source_id=source_id,
        settings_json=json.dumps(default_settings, ensure_ascii=False),
    )
    db.add(project)
    await db.flush()

    slide_seed = [
        {
            "title": meta.get("label") or block_id,
            "subtitle": "版式可视化编辑",
            "layout": "bullets",
            "bullets": [],
            "canvas_elements": elements or elements_web,
            "canvas_background": canvas_background,
        }
    ]
    await _seed_project_slides(db, project, slide_seed, default_settings)
    result = await db.execute(
        select(Project).where(Project.id == project.id).options(selectinload(Project.slides))
    )
    return result.scalar_one()


async def quick_create_layout_draft(
    db: AsyncSession,
    admin: User,
    *,
    block_id: str | None = None,
    label: str = "新版式",
    group: str = "custom",
    placement: str = "more",
) -> tuple[str, Project]:
    bid = (block_id or f"custom-{uuid.uuid4().hex[:8]}").strip()
    if await get_block(db, bid):
        raise LayoutDraftError("版式 ID 已存在")

    sample_elements = [
        {
            "type": "text",
            "x": 20,
            "y": 120,
            "width": 320,
            "height": 56,
            "zIndex": 2,
            "content": label,
            "style": {
                "fontSize": 22,
                "fontWeight": "bold",
                "color": "#1b1b1c",
                "textAlign": "center",
                "background": "transparent",
            },
        }
    ]
    project = await get_or_create_layout_draft(
        db,
        bid,
        admin,
        seed={
            "label": label,
            "icon": "dashboard",
            "group": group,
            "placement": placement,
            "elements": sample_elements,
            "elements_web": [],
            "canvas_background": "",
            "sort_order": 100,
            "enabled": True,
        },
    )
    return bid, project


async def get_owned_layout_draft(
    db: AsyncSession,
    block_id: str,
    project_id: int,
    admin: User,
) -> Project:
    source_id = layout_source_id(block_id)
    result = await db.execute(
        select(Project)
        .where(
            Project.id == project_id,
            Project.user_id == admin.id,
            Project.template_source_id == source_id,
        )
        .options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise LayoutDraftError("版式草稿项目不存在或无权访问")
    return project


async def save_layout_from_project(
    db: AsyncSession,
    block_id: str,
    project_id: int,
    admin: User,
    meta: dict[str, Any] | None = None,
) -> dict:
    project = await get_owned_layout_draft(db, block_id, project_id, admin)
    slides = sorted(project.slides, key=lambda s: s.sort_order)
    if not slides:
        raise LayoutDraftError("草稿中没有页面")

    slide = slides[0]
    try:
        canvas_elements = json.loads(slide.canvas_json or "[]")
        if not isinstance(canvas_elements, list):
            canvas_elements = []
    except json.JSONDecodeError:
        canvas_elements = []

    settings = project_settings_out(project)
    bg_map = settings.slideBackgrounds or {}
    canvas_background = bg_map.get(str(slide.id)) or ""

    existing = await get_block(db, block_id)
    if _is_web_viewport(settings.viewportId):
        elements = existing.get("elements", []) if existing else []
        elements_web = canvas_elements
    else:
        elements = canvas_elements
        elements_web = existing.get("elements_web", []) if existing else []

    if not elements and not elements_web:
        raise LayoutDraftError("画布不能为空")

    payload: dict[str, Any] = {
        "label": (meta or {}).get("label") or (existing or {}).get("label") or block_id,
        "icon": (meta or {}).get("icon") or (existing or {}).get("icon") or "dashboard",
        "group": (meta or {}).get("group") or (existing or {}).get("group") or "custom",
        "placement": (meta or {}).get("placement") or (existing or {}).get("placement") or "more",
        "elements": elements,
        "elements_web": elements_web,
        "canvas_background": (meta or {}).get("canvas_background", canvas_background),
        "sort_order": int((meta or {}).get("sort_order", (existing or {}).get("sort_order", 100))),
        "enabled": (meta or {}).get("enabled", (existing or {}).get("enabled", True)),
    }

    try:
        if existing:
            row = await update_block(db, block_id, payload)
        else:
            row = await create_block(db, {"id": block_id, **payload})
            row["source"] = "override"
    except LayoutBlockError as exc:
        raise LayoutDraftError(str(exc)) from exc
    return row
