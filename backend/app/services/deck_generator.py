"""演示生成服务。"""
import json
import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import GenerationLog, Project, Slide
from app.schemas import DeckJson, GenerateFullRequest, GeneratePageRequest
from app.services.llm.provider import LlmError, chat_completion, extract_json
from app.services.template_engine import render_template


async def generate_full_deck(
    db: AsyncSession,
    project_id: int,
    body: GenerateFullRequest,
) -> Project:
    messages = render_template(
        "全量生成.yaml",
        {
            "topic": body.topic,
            "audience": body.audience,
            "page_count": body.page_count,
            "style": body.style,
        },
    )
    try:
        raw, channel, model = await chat_completion(messages, body.channel, body.tier)
        data = extract_json(raw)
        deck = DeckJson.model_validate(data)
    except (LlmError, Exception) as exc:
        await _log(db, project_id, "full_deck", body.channel or "auto", False, str(exc))
        raise

    result = await db.execute(select(Project).where(Project.id == project_id).options(selectinload(Project.slides)))
    project = result.scalar_one()
    for slide in list(project.slides):
        await db.delete(slide)
    project.title = deck.title
    project.theme = deck.theme
    for idx, s in enumerate(deck.slides):
        project.slides.append(
            Slide(
                sort_order=idx,
                layout=s.get("layout", "bullets"),
                title=s.get("title", ""),
                subtitle=s.get("subtitle", ""),
                bullets_json=json.dumps(s.get("bullets", []), ensure_ascii=False),
                speaker_notes=s.get("speakerNotes", s.get("speaker_notes", "")),
                animation=s.get("animation", "fade"),
            )
        )
    if not project.share_slug:
        project.share_slug = secrets.token_urlsafe(8)
    await _log(db, project_id, "full_deck", channel, True, f"生成成功 · 模型 {model}")
    await db.commit()
    await db.refresh(project)
    return project


async def generate_single_page(
    db: AsyncSession,
    project_id: int,
    slide_id: int,
    body: GeneratePageRequest,
) -> Slide:
    result = await db.execute(
        select(Project).where(Project.id == project_id).options(selectinload(Project.slides))
    )
    project = result.scalar_one()
    slides = sorted(project.slides, key=lambda s: s.sort_order)
    target = next((s for s in slides if s.id == slide_id), None)
    if not target:
        raise ValueError("页面不存在")

    idx = slides.index(target)
    current = {
        "index": idx + 1,
        "layout": target.layout,
        "title": target.title,
        "subtitle": target.subtitle,
        "bullets": json.loads(target.bullets_json or "[]"),
        "speakerNotes": target.speaker_notes,
        "animation": target.animation,
    }
    messages = render_template(
        "单页改写.yaml",
        {
            "page_index": idx + 1,
            "current_slide_json": json.dumps(current, ensure_ascii=False),
            "style_summary": project.theme,
            "prev_title": slides[idx - 1].title if idx > 0 else "",
            "next_title": slides[idx + 1].title if idx + 1 < len(slides) else "",
            "instruction": body.instruction,
        },
    )
    try:
        raw, channel, model = await chat_completion(messages, body.channel, body.tier)
        data = extract_json(raw)
    except (LlmError, Exception) as exc:
        await _log(db, project_id, "single_page", body.channel or "auto", False, str(exc))
        raise

    target.layout = data.get("layout", target.layout)
    target.title = data.get("title", target.title)
    target.subtitle = data.get("subtitle", target.subtitle)
    target.bullets_json = json.dumps(data.get("bullets", []), ensure_ascii=False)
    target.speaker_notes = data.get("speakerNotes", data.get("speaker_notes", target.speaker_notes))
    target.animation = data.get("animation", target.animation)
    await _log(db, project_id, "single_page", channel, True, f"改写成功 · 模型 {model}")
    await db.commit()
    await db.refresh(target)
    return target


async def _log(
    db: AsyncSession,
    project_id: int,
    template_id: str,
    channel: str | None,
    success: bool,
    message: str,
) -> None:
    db.add(
        GenerationLog(
            project_id=project_id,
            template_id=template_id,
            channel=channel or "auto",
            success=1 if success else 0,
            message=message[:2000],
        )
    )


def new_share_slug() -> str:
    return uuid.uuid4().hex[:12]
