"""项目与页面 API。"""
import asyncio
import json
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps.auth import get_current_user
from app.deps.projects import get_owned_project, get_owned_slide, resolve_owned_project_ref
from app.models import Project, Slide, User
from app.schemas import (
    AiDeckGenerateRequest,
    AiSlideGenerateRequest,
    DeckPremiumJobOut,
    GenerateImageRequest,
    GenerateImageResponse,
    GenerationMetaOut,
    ProjectCreate,
    ProjectOut,
    ProjectSettingsUpdate,
    ProjectUpdate,
    SlideCreate,
    SlideCanvasUpdate,
    SlideOut,
    SlideUpdate,
    parse_project_settings,
    project_settings_out,
)
from app.services.deck_generation_service import (
    compute_insert_sort_order,
    generate_deck_from_ai,
    generate_single_slide_into_project,
    shift_slide_sort_orders_from,
)
from app.services.deck_premium_job import (
    get_premium_job_status,
    import_premium_pptx,
    submit_premium_deck_job,
)
from app.services.deck_generator import new_public_id
from app.services.h5_template_service import get_template as get_h5_template
from app.services.image_generator import generate_slide_image
from app.services.llm.provider import LlmError, QuotaLlmError
from app.services.project_seed_service import reload_project, seed_project_slides
from app.services.prompt_template_service import list_templates
from app.services.pptx_template_parser import PptxParseError, parse_pptx_bytes

router = APIRouter(prefix="/api/v1", tags=["项目"])
logger = logging.getLogger(__name__)


def _generation_meta_from_project(project: Project) -> GenerationMetaOut | None:
    try:
        data = json.loads(project.settings_json or "{}")
    except json.JSONDecodeError:
        return None
    meta = data.get("generationMeta")
    if not isinstance(meta, dict):
        return None
    return GenerationMetaOut(
        model=str(meta.get("model") or ""),
        channel=str(meta.get("channel") or ""),
        duration_ms=meta.get("duration_ms"),
        background_preset=str(meta.get("background_preset") or ""),
    )


def _project_out(project: Project) -> ProjectOut:
    slides = sorted(project.slides, key=lambda s: s.sort_order)
    settings = project_settings_out(project)
    bg_map = settings.slideBackgrounds or {}
    return ProjectOut(
        id=project.id,
        public_id=project.public_id,
        title=project.title,
        theme=project.theme,
        share_slug=project.share_slug,
        settings=settings,
        slides=[
            SlideOut.from_orm_slide(s, canvas_background=bg_map.get(str(s.id)))
            for s in slides
        ],
        updated_at=project.updated_at,
        generation_meta=_generation_meta_from_project(project),
    )


def _merge_settings(project: Project, patch: dict) -> None:
    current = parse_project_settings(project.settings_json)
    for key, val in patch.items():
        if val is not None:
            current[key] = val
    project.settings_json = json.dumps(current, ensure_ascii=False)


async def _seed_project_slides(
    db: AsyncSession,
    project: Project,
    slides_seed: list[dict],
    template_settings: dict,
) -> None:
    await seed_project_slides(db, project, slides_seed, template_settings)


async def _reload_project(db: AsyncSession, project_id: int) -> Project:
    return await reload_project(db, project_id)


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
        .where(Project.user_id == user.id, Project.template_source_id.is_(None))
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
    template_settings: dict = {}
    if body.template_id:
        tpl = await get_h5_template(db, body.template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="模板不存在")
        theme = body.template_id
        slides_seed = tpl.get("slides_json") or []
        template_settings = tpl.get("settings_json") or {}

    pid = new_public_id()
    project = Project(
        title=body.title,
        theme=theme,
        public_id=pid,
        share_slug=pid,
        user_id=user.id,
        settings_json=json.dumps(template_settings, ensure_ascii=False),
    )
    db.add(project)
    await db.flush()

    await _seed_project_slides(db, project, slides_seed, template_settings)

    await db.commit()
    project = await _reload_project(db, project.id)
    return _project_out(project)


@router.post("/项目/导入-pptx", response_model=ProjectOut, summary="上传 PPTX 并创建演示项目")
async def import_project_pptx(
    file: UploadFile = File(...),
    device: str = Form("mobile"),
    title: str | None = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw = await file.read()
    inferred_title = title or (file.filename or "导入的演示").rsplit(".", 1)[0]
    try:
        parsed = parse_pptx_bytes(
            raw,
            device=device if device in ("mobile", "web") else "mobile",
            title=inferred_title,
        )
    except PptxParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    slides_seed = parsed.get("slides_json") or []
    template_settings = parsed.get("settings_json") or {}
    pid = new_public_id()
    project = Project(
        title=parsed.get("title") or inferred_title,
        theme="imported",
        public_id=pid,
        share_slug=pid,
        user_id=user.id,
        settings_json=json.dumps(template_settings, ensure_ascii=False),
    )
    db.add(project)
    await db.flush()
    await _seed_project_slides(db, project, slides_seed, template_settings)
    await db.commit()
    project = await _reload_project(db, project.id)
    return _project_out(project)


@router.post("/项目/premium-导入-pptx", response_model=ProjectOut, summary="导入 ppt-master 高质量 PPTX")
async def import_premium_project_pptx(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw = await file.read()
    inferred_title = title or (file.filename or "ppt-master 导入").rsplit(".", 1)[0]
    try:
        project = await import_premium_pptx(
            db,
            user,
            raw,
            title=inferred_title,
            filename=file.filename or "",
        )
    except PptxParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await db.commit()
    project = await _reload_project(db, project.id)
    return _project_out(project)


@router.post("/项目/ai-生成-premium", response_model=DeckPremiumJobOut, summary="提交 ppt-master 高质量生成任务")
async def ai_generate_premium_project(
    body: AiDeckGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await submit_premium_deck_job(db, user, body)
    except Exception as exc:
        await db.rollback()
        logger.exception("ai_generate_premium_project failed user_id=%s", user.id)
        raise HTTPException(status_code=500, detail=f"提交失败：{exc}") from exc
    await db.commit()
    from app.services.ppt_master_worker.scheduler import enqueue_premium_job

    enqueue_premium_job(result["job_id"])
    return DeckPremiumJobOut(**result)


@router.get("/项目/ai-生成-premium/{job_id}", response_model=DeckPremiumJobOut, summary="查询高质量生成任务状态")
async def get_premium_deck_job(
    job_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await get_premium_job_status(db, job_id, user.id)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")
    return DeckPremiumJobOut(**result)


@router.post("/项目/ai-生成", response_model=ProjectOut, summary="AI 全量生成演示项目")
async def ai_generate_project(
    body: AiDeckGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 强制严格模板模式 — 关闭旧AI生图管线，确保秒级响应
    body.strict_template_mode = True

    try:
        # 硬超时 90 秒 — 超时直接报错，不无限等待
        project = await asyncio.wait_for(
            generate_deck_from_ai(db, user, body),
            timeout=90.0,
        )
    except asyncio.TimeoutError:
        await db.rollback()
        raise HTTPException(
            status_code=504,
            detail="生成超时（90秒）。请减少页数或缩短内容后重试。",
        )
    except QuotaLlmError as exc:
        await db.rollback()
        raise HTTPException(status_code=402, detail=str(exc)) from exc
    except LlmError as exc:
        await db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("ai_generate_project failed user_id=%s page_count=%s", user.id, body.page_count)
        raise HTTPException(status_code=500, detail=f"生成落库失败：{exc}") from exc
    return _project_out(project)


@router.get("/项目/resolve/{ref}", summary="解析项目引用（数字 id 或 public_id）")
async def resolve_project_ref(
    ref: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await resolve_owned_project_ref(ref, user, db)
    return {"public_id": project.public_id}


@router.get("/项目/{public_id}", response_model=ProjectOut, summary="获取项目")
async def get_project(project: Project = Depends(get_owned_project)):
    return _project_out(project)


@router.put("/项目/{public_id}", response_model=ProjectOut, summary="更新项目")
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


@router.put("/项目/{public_id}/设置", response_model=ProjectOut, summary="保存项目播放设置")
async def update_project_settings(
    body: ProjectSettingsUpdate,
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
):
    patch = body.model_dump(exclude_unset=True)
    _merge_settings(project, patch)
    await db.commit()
    await db.refresh(project)
    return _project_out(project)


@router.delete("/项目/{public_id}", summary="删除项目")
async def delete_project(
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(project)
    await db.commit()
    return {"message": "已删除"}


@router.post("/项目/{public_id}/页面", response_model=SlideOut, summary="新增页面")
async def add_slide(
    body: SlideCreate,
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
):
    new_order = compute_insert_sort_order(list(project.slides), body.insert_after_slide_id)
    if body.insert_after_slide_id is not None:
        await shift_slide_sort_orders_from(db, project.id, new_order)
    slide = Slide(
        project_id=project.id,
        sort_order=new_order,
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
    settings = project_settings_out(project)
    bg_map = settings.slideBackgrounds or {}
    return SlideOut.from_orm_slide(slide, canvas_background=bg_map.get(str(slide.id)))


@router.post("/项目/{public_id}/页面/ai-生成", response_model=SlideOut, summary="AI 生成单页并插入")
async def ai_generate_slide(
    body: AiSlideGenerateRequest,
    project: Project = Depends(get_owned_project),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        slide = await generate_single_slide_into_project(db, user, project, body)
    except QuotaLlmError as exc:
        await db.rollback()
        raise HTTPException(status_code=402, detail=str(exc)) from exc
    except LlmError as exc:
        await db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("ai_generate_slide failed project_id=%s", project.id)
        raise HTTPException(status_code=500, detail=f"生成落库失败：{exc}") from exc
    settings = project_settings_out(project)
    bg_map = settings.slideBackgrounds or {}
    return SlideOut.from_orm_slide(slide, canvas_background=bg_map.get(str(slide.id)))


@router.put("/项目/{public_id}/页面/{slide_id}", response_model=SlideOut, summary="更新页面")
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
    if body.chat_script is not None:
        slide.chat_script_json = json.dumps(body.chat_script, ensure_ascii=False)
    await db.commit()
    await db.refresh(slide)
    return SlideOut.from_orm_slide(slide)


@router.put("/项目/{public_id}/页面/{slide_id}/画布", response_model=SlideOut, summary="保存页面画布元素")
async def update_slide_canvas(
    body: SlideCanvasUpdate,
    slide: Slide = Depends(get_owned_slide),
    db: AsyncSession = Depends(get_db),
):
    slide.canvas_json = json.dumps(body.elements, ensure_ascii=False)
    await db.commit()
    await db.refresh(slide)
    return SlideOut.from_orm_slide(slide)


@router.delete("/项目/{public_id}/页面/{slide_id}", summary="删除页面")
async def delete_slide(slide: Slide = Depends(get_owned_slide), db: AsyncSession = Depends(get_db)):
    await db.delete(slide)
    await db.commit()
    return {"message": "已删除"}


@router.post(
    "/项目/{public_id}/生成/配图",
    response_model=GenerateImageResponse,
    summary="AI 生图",
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


@router.get("/分享/{public_id}", response_model=ProjectOut, summary="通过分享链接预览")
async def share_preview(public_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .where(Project.public_id == public_id)
        .options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        result = await db.execute(
            select(Project)
            .where(Project.share_slug == public_id)
            .options(selectinload(Project.slides))
        )
        project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="分享链接无效")
    return _project_out(project)
