"""项目与页面 API。"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Project, Slide
from app.schemas import (
    GenerateFullRequest,
    GeneratePageRequest,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    SlideCreate,
    SlideOut,
    SlideUpdate,
)
from app.services.deck_generator import generate_full_deck, generate_single_page, new_share_slug
from app.services.llm.provider import LlmError
from app.services.template_engine import list_templates

router = APIRouter(prefix="/api/v1", tags=["项目"])


def _project_out(project: Project) -> ProjectOut:
    slides = sorted(project.slides, key=lambda s: s.sort_order)
    return ProjectOut(
        id=project.id,
        title=project.title,
        theme=project.theme,
        share_slug=project.share_slug,
        slides=[SlideOut.from_orm_slide(s) for s in slides],
    )


@router.get("/模板", summary="列出提示词模板")
async def get_templates():
    return {"items": list_templates()}


@router.get("/项目", response_model=list[ProjectOut], summary="项目列表")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).options(selectinload(Project.slides)).order_by(Project.updated_at.desc()))
    return [_project_out(p) for p in result.scalars().all()]


@router.post("/项目", response_model=ProjectOut, summary="创建项目")
async def create_project(
    body: ProjectCreate,
    user_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    project = Project(title=body.title, theme=body.theme, share_slug=new_share_slug(), user_id=user_id)
    db.add(project)
    db.add(
        Slide(
            project=project,
            sort_order=0,
            layout="title",
            title=body.title,
            subtitle="点击右侧 AI 生成或手动编辑",
            bullets_json="[]",
        )
    )
    await db.commit()
    result = await db.execute(select(Project).where(Project.id == project.id).options(selectinload(Project.slides)))
    return _project_out(result.scalar_one())


@router.get("/项目/{project_id}", response_model=ProjectOut, summary="获取项目")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await _get_project(db, project_id)
    return _project_out(project)


@router.put("/项目/{project_id}", response_model=ProjectOut, summary="更新项目")
async def update_project(project_id: int, body: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    project = await _get_project(db, project_id)
    if body.title is not None:
        project.title = body.title
    if body.theme is not None:
        project.theme = body.theme
    await db.commit()
    await db.refresh(project)
    return _project_out(project)


@router.delete("/项目/{project_id}", summary="删除项目")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await _get_project(db, project_id)
    await db.delete(project)
    await db.commit()
    return {"message": "已删除"}


@router.post("/项目/{project_id}/页面", response_model=SlideOut, summary="新增页面")
async def add_slide(project_id: int, body: SlideCreate, db: AsyncSession = Depends(get_db)):
    project = await _get_project(db, project_id)
    order = len(project.slides)
    slide = Slide(
        project_id=project.id,
        sort_order=order,
        layout=body.layout,
        title=body.title,
        subtitle=body.subtitle,
        bullets_json=json.dumps(body.bullets, ensure_ascii=False),
        speaker_notes=body.speaker_notes,
        animation=body.animation,
    )
    db.add(slide)
    await db.commit()
    await db.refresh(slide)
    return SlideOut.from_orm_slide(slide)


@router.put("/项目/{project_id}/页面/{slide_id}", response_model=SlideOut, summary="更新页面")
async def update_slide(
    project_id: int, slide_id: int, body: SlideUpdate, db: AsyncSession = Depends(get_db)
):
    slide = await _get_slide(db, project_id, slide_id)
    if body.layout is not None:
        slide.layout = body.layout
    if body.title is not None:
        slide.title = body.title
    if body.subtitle is not None:
        slide.subtitle = body.subtitle
    if body.bullets is not None:
        slide.bullets_json = json.dumps(body.bullets, ensure_ascii=False)
    if body.speaker_notes is not None:
        slide.speaker_notes = body.speaker_notes
    if body.animation is not None:
        slide.animation = body.animation
    if body.sort_order is not None:
        slide.sort_order = body.sort_order
    await db.commit()
    await db.refresh(slide)
    return SlideOut.from_orm_slide(slide)


@router.delete("/项目/{project_id}/页面/{slide_id}", summary="删除页面")
async def delete_slide(project_id: int, slide_id: int, db: AsyncSession = Depends(get_db)):
    slide = await _get_slide(db, project_id, slide_id)
    await db.delete(slide)
    await db.commit()
    return {"message": "已删除"}


@router.post("/项目/{project_id}/生成/全量", response_model=ProjectOut, summary="AI 全量生成")
async def api_generate_full(
    project_id: int,
    body: GenerateFullRequest,
    user_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    await _get_project(db, project_id)
    try:
        project = await generate_full_deck(db, project_id, body, user_id=user_id)
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"生成失败：{exc}") from exc
    result = await db.execute(
        select(Project).where(Project.id == project.id).options(selectinload(Project.slides))
    )
    return _project_out(result.scalar_one())


@router.post("/项目/{project_id}/页面/{slide_id}/生成/单页", response_model=SlideOut, summary="AI 单页改写")
async def api_generate_page(
    project_id: int, slide_id: int, body: GeneratePageRequest, db: AsyncSession = Depends(get_db)
):
    try:
        slide = await generate_single_page(db, project_id, slide_id, body)
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SlideOut.from_orm_slide(slide)


@router.get("/分享/{share_slug}", response_model=ProjectOut, summary="通过分享链接预览")
async def share_preview(share_slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(Project.share_slug == share_slug).options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="分享链接无效")
    return _project_out(project)


async def _get_project(db: AsyncSession, project_id: int) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id).options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


async def _get_slide(db: AsyncSession, project_id: int, slide_id: int) -> Slide:
    result = await db.execute(select(Slide).where(Slide.id == slide_id, Slide.project_id == project_id))
    slide = result.scalar_one_or_none()
    if not slide:
        raise HTTPException(status_code=404, detail="页面不存在")
    return slide
