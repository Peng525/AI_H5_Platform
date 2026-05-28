"""项目与页面 API。"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps.auth import get_current_user
from app.deps.projects import get_owned_project, get_owned_slide
from app.models import Project, Slide, User
from app.schemas import (
    GenerateFullRequest,
    GenerateImageRequest,
    GenerateImageResponse,
    GeneratePageRequest,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    SlideCreate,
    SlideCanvasUpdate,
    SlideOut,
    SlideUpdate,
)
from app.services.deck_generator import generate_full_deck, generate_single_page, new_share_slug
from app.services.h5_template_service import get_template as get_h5_template
from app.services.image_generator import generate_slide_image
from app.services.llm.provider import LlmError
from app.services.prompt_template_service import list_templates

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
async def list_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user.id)
        .options(selectinload(Project.slides))
        .order_by(Project.updated_at.desc())
    )
    return [_project_out(p) for p in result.scalars().all()]


@router.post("/项目", response_model=ProjectOut, summary="创建项目")
async def create_project(
    body: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    theme = body.theme
    slides_seed: list[dict] = []
    if body.template_id:
        tpl = await get_h5_template(db, body.template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="模板不存在")
        theme = body.template_id
        slides_seed = tpl.get("slides_json") or []

    project = Project(
        title=body.title,
        theme=theme,
        share_slug=new_share_slug(),
        user_id=user.id,
    )
    db.add(project)

    if slides_seed:
        for idx, s in enumerate(slides_seed):
            db.add(
                Slide(
                    project=project,
                    sort_order=idx,
                    layout=s.get("layout", "bullets"),
                    title=s.get("title", ""),
                    subtitle=s.get("subtitle", ""),
                    bullets_json=json.dumps(s.get("bullets", []), ensure_ascii=False),
                    speaker_notes=s.get("speakerNotes", s.get("speaker_notes", "")),
                    animation=s.get("animation", "fade"),
                )
            )
    else:
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
    result = await db.execute(
        select(Project).where(Project.id == project.id).options(selectinload(Project.slides))
    )
    return _project_out(result.scalar_one())


@router.get("/项目/{project_id}", response_model=ProjectOut, summary="获取项目")
async def get_project(project: Project = Depends(get_owned_project)):
    return _project_out(project)


@router.put("/项目/{project_id}", response_model=ProjectOut, summary="更新项目")
async def update_project(
    body: ProjectUpdate,
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
):
    if body.title is not None:
        project.title = body.title
    if body.theme is not None:
        project.theme = body.theme
    await db.commit()
    await db.refresh(project)
    return _project_out(project)


@router.delete("/项目/{project_id}", summary="删除项目")
async def delete_project(
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(project)
    await db.commit()
    return {"message": "已删除"}


@router.post("/项目/{project_id}/页面", response_model=SlideOut, summary="新增页面")
async def add_slide(
    body: SlideCreate,
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
):
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
async def update_slide(body: SlideUpdate, slide: Slide = Depends(get_owned_slide), db: AsyncSession = Depends(get_db)):
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


@router.put("/项目/{project_id}/页面/{slide_id}/画布", response_model=SlideOut, summary="保存页面画布元素")
async def update_slide_canvas(
    body: SlideCanvasUpdate,
    slide: Slide = Depends(get_owned_slide),
    db: AsyncSession = Depends(get_db),
):
    slide.canvas_json = json.dumps(body.elements, ensure_ascii=False)
    await db.commit()
    await db.refresh(slide)
    return SlideOut.from_orm_slide(slide)


@router.delete("/项目/{project_id}/页面/{slide_id}", summary="删除页面")
async def delete_slide(slide: Slide = Depends(get_owned_slide), db: AsyncSession = Depends(get_db)):
    await db.delete(slide)
    await db.commit()
    return {"message": "已删除"}


@router.post("/项目/{project_id}/生成/全量", response_model=ProjectOut, summary="AI 全量生成")
async def api_generate_full(
    body: GenerateFullRequest,
    project: Project = Depends(get_owned_project),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        proj = await generate_full_deck(db, project.id, body, user_id=user.id)
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"生成失败：{exc}") from exc
    result = await db.execute(
        select(Project).where(Project.id == proj.id).options(selectinload(Project.slides))
    )
    return _project_out(result.scalar_one())


@router.post("/项目/{project_id}/页面/{slide_id}/生成/单页", response_model=SlideOut, summary="AI 单页改写")
async def api_generate_page(
    body: GeneratePageRequest,
    slide: Slide = Depends(get_owned_slide),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        updated = await generate_single_page(db, slide.project_id, slide.id, body, user_id=user.id)
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SlideOut.from_orm_slide(updated)


@router.post(
    "/项目/{project_id}/生成/配图",
    response_model=GenerateImageResponse,
    summary="AI 生成配图",
)
async def api_generate_image(
    body: GenerateImageRequest,
    project: Project = Depends(get_owned_project),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await generate_slide_image(db, project.id, body, user_id=user.id)
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return GenerateImageResponse(**result)


@router.get("/分享/{share_slug}", response_model=ProjectOut, summary="通过分享链接预览")
async def share_preview(share_slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(Project.share_slug == share_slug).options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="分享链接无效")
    return _project_out(project)
