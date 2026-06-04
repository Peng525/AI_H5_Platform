"""项目幻灯片种子写入。"""
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Project, Slide


async def seed_project_slides(
    db: AsyncSession,
    project: Project,
    slides_seed: list[dict],
    template_settings: dict,
) -> None:
    if not slides_seed:
        db.add(
            Slide(
                project=project,
                sort_order=0,
                layout="title",
                title=project.title,
                subtitle="点击右侧 AI 生图或手动编辑",
                bullets_json="[]",
            )
        )
        return

    for idx, s in enumerate(slides_seed):
        canvas_elements = s.get("canvas_elements") or []
        chat_script = s.get("chat_script") or {}
        structured = s.get("structured") or {}
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
                structured_json=json.dumps(structured, ensure_ascii=False),
            )
        )
    await db.flush()
    backgrounds: dict[str, str] = {}
    slide_rows = await db.execute(
        select(Slide).where(Slide.project_id == project.id).order_by(Slide.sort_order)
    )
    sorted_slides = list(slide_rows.scalars().all())
    for slide, seed in zip(sorted_slides, slides_seed):
        bg = seed.get("canvas_background")
        if bg:
            backgrounds[str(slide.id)] = bg
    if backgrounds:
        merged = {
            **template_settings,
            "slideBackgrounds": {**(template_settings.get("slideBackgrounds") or {}), **backgrounds},
        }
        project.settings_json = json.dumps(merged, ensure_ascii=False)


async def reload_project(db: AsyncSession, project_id: int) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id).options(selectinload(Project.slides))
    )
    return result.scalar_one()
