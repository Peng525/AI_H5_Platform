"""
多步LLM编排器 — Strategist 规划 + 严格模板结构化输出

在现有FastAPI内实现编排，不依赖外部Agent工具：
  Phase 1: Strategist — 规划页面结构（输出 template_type + 内容）
  Phase 2: 结构化归一化 — 复用严格模板 _extract_structured_slide 产出 structured

坐标/配色交给前端 compilePptTemplateSlide + designThemes 计算，
不再让 LLM 直接生成 SVG，保证形状/文字/图片逐元素可编辑。
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog, Project, Slide, User
from app.schemas import AiDeckGenerateRequest
from app.services.deck_generation_service import (
    BACKGROUND_COLORS,
    THEME_DEFAULT_GRADIENTS,
    VALID_THEME_IDS,
    VIEWPORT_MAP,
    _build_topic,
    _build_style,
    _extract_structured_slide,
    _validate_slide_structure,
    new_public_id,
)
from app.services.deck_generator import new_public_id as gen_new_public_id
from app.services.llm.provider import LlmError, QuotaLlmError, chat_completion_with_usage, extract_json
from app.services.prompt_template_service import render_template
from app.services.project_seed_service import seed_project_slides, reload_project
from app.services.quota import QuotaExceeded, check_and_consume

logger = logging.getLogger(__name__)

# 复用 new_public_id
new_public_id = gen_new_public_id

# ── 主题色映射（镜像前端 designThemes.js）──
_THEME_COLORS: dict[str, dict[str, str]] = {
    "zjy-minimal":    {"primary": "#156082", "text": "#0E2841", "text_muted": "#44546A", "bg": "#FFFFFF", "accent2": "#5B9BD5", "style_hint": "简约商务、深蓝主色、白底"},
    "eqxiu-story":    {"primary": "#E17055", "text": "#2D3436", "text_muted": "#636E72", "bg": "#FFF8F3", "accent2": "#00B894", "style_hint": "温暖叙事、珊瑚橙主色、暖白底"},
    "tech-blue":      {"primary": "#38BDF8", "text": "#E8F4FF", "text_muted": "#94A3B8", "bg": "#0A1628", "accent2": "#6366F1", "style_hint": "科技蓝、深色背景、霓虹蓝主色"},
    "dark-pro":       {"primary": "#D4AF37", "text": "#F5F5F5", "text_muted": "#A3A3A3", "bg": "#1A1A1A", "accent2": "#F5E6A3", "style_hint": "暗黑专业、金色主色、深灰底"},
    "fresh-green":    {"primary": "#2D6A4F", "text": "#1B4332", "text_muted": "#52796F", "bg": "#F7FBF8", "accent2": "#52B788", "style_hint": "清新自然、森林绿主色、浅绿底"},
    "coral-vivid":    {"primary": "#F97316", "text": "#7C2D12", "text_muted": "#9A3412", "bg": "#FFF5F2", "accent2": "#FB923C", "style_hint": "活力珊瑚、橙红主色、暖粉底"},
    "lavender-soft":  {"primary": "#8B5CF6", "text": "#4C1D95", "text_muted": "#6D28D9", "bg": "#FAF5FF", "accent2": "#A78BFA", "style_hint": "柔和紫调、薰衣草主色、淡紫底"},
    "ocean-calm":     {"primary": "#0284C7", "text": "#0C4A6E", "text_muted": "#0369A1", "bg": "#F0F9FF", "accent2": "#06B6D4", "style_hint": "深海宁静、天蓝主色、浅蓝底"},
    "sunset-warm":    {"primary": "#D97706", "text": "#78350F", "text_muted": "#92400E", "bg": "#FFFBEB", "accent2": "#F59E0B", "style_hint": "暖阳金橙、琥珀主色、米黄底"},
    "minimal-gray":   {"primary": "#374151", "text": "#1F2937", "text_muted": "#6B7280", "bg": "#FAFAFA", "accent2": "#9CA3AF", "style_hint": "极简灰白、石墨主色、浅灰底"},
    "elegant-gold":   {"primary": "#B8860B", "text": "#3D2B1F", "text_muted": "#8B7355", "bg": "#FBF8F3", "accent2": "#DAA520", "style_hint": "优雅金棕、暗金主色、米白底"},
    "berry-bold":     {"primary": "#BE185D", "text": "#831843", "text_muted": "#9D174D", "bg": "#FFF1F2", "accent2": "#F43F5E", "style_hint": "大胆莓红、深粉主色、浅粉底"},
}


def _resolve_theme_colors(body: AiDeckGenerateRequest) -> dict[str, str]:
    """根据用户选择的 theme_id 解析主题色，默认 zjy-minimal。"""
    theme_id = (body.theme_id or "zjy-minimal").strip()
    return _THEME_COLORS.get(theme_id, _THEME_COLORS["zjy-minimal"])


# ── 数据结构 ──

@dataclass
class OrchestratorProgress:
    """编排进度（供API轮询）"""
    stage: str = "queued"  # queued | strategist | importing | completed | failed
    phase: str = ""
    current_page: int = 0
    total_pages: int = 0
    progress_pct: int = 0
    message: str = ""
    error: str = ""
    project_public_id: str = ""
    phases_meta: dict = field(default_factory=dict)


# 全局进度存储（进程内，重启丢失；后续可迁移到Redis/DB）
_progress_store: dict[str, OrchestratorProgress] = {}


def get_orchestrator_progress(job_id: str) -> OrchestratorProgress | None:
    return _progress_store.get(job_id)


# ── Phase 1: Strategist ──

async def _strategist_phase(
    body: AiDeckGenerateRequest,
    variables: dict,
    theme_colors: dict | None = None,
) -> dict:
    """规划演示结构，返回 {title, theme, pages: [{page_num, template_type, title, ...}]}"""
    # 注入主题色变量到模板
    tc = theme_colors or _THEME_COLORS["zjy-minimal"]
    variables = {
        **variables,
        "theme_style_hint": tc.get("style_hint", "简约商务"),
        "primary": tc["primary"],
        "text_color": tc["text"],
        "bg_color": tc["bg"],
    }
    messages = render_template("orchestrate_strategist.yaml", variables)
    t0 = time.perf_counter()
    raw, channel, model, usage = await chat_completion_with_usage(
        messages,
        channel=body.channel,
        tier=body.tier or "free",
        model=(body.model or "").strip() or None,
    )
    data = extract_json(raw)

    title = str(data.get("title") or "AI 演示").strip()[:120]
    theme = str(data.get("theme") or "").strip()[:64]
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        raise LlmError("Strategist 未返回有效的 pages 数组")

    # 确保恰好 page_count 页
    if len(pages) > body.page_count:
        pages = pages[:body.page_count]
    while len(pages) < body.page_count:
        pages.append({
            "page_num": len(pages) + 1,
            "template_type": "points",
            "title": f"第 {len(pages) + 1} 页",
            "key_points": ["内容要点"],
        })

    duration_ms = int((time.perf_counter() - t0) * 1000)
    result = {
        "title": title,
        "theme": theme,
        "pages": pages,
        "meta": {
            "duration_ms": duration_ms,
            "channel": channel,
            "model": model,
            "tokens": usage,
        },
    }
    logger.info(
        "orchestrator strategist done title=%r pages=%s duration_ms=%s tokens=%s",
        title[:80], len(pages), duration_ms, usage.get("total_tokens", 0),
    )
    return result


# ── Phase 2: 结构化归一化 ──

def _pages_plan_to_slides_seed(pages_plan: list[dict]) -> list[dict]:
    """将 Strategist 的 pages 规划转换为结构化 slides_seed。

    复用严格模板归一化 _extract_structured_slide 产出 structured（而非 SVG 背景图），
    坐标/配色交给前端 compilePptTemplateSlide + designThemes 计算。
    Strategist 用 key_points 承载要点/卡片，严格模板归一化读取 points/cards，这里做字段映射。
    """
    slides_seed = []
    for i, page in enumerate(pages_plan):
        template_type = str(page.get("template_type") or "points").strip()
        raw = dict(page)

        key_points = raw.get("key_points") or []
        if isinstance(key_points, str):
            key_points = [key_points]

        if template_type == "cards":
            raw["cards"] = key_points[:4]
        else:
            raw["points"] = key_points[:5]

        structured = _extract_structured_slide(raw, i, len(pages_plan))

        slides_seed.append({
            "layout": template_type[:32],
            "title": structured.get("title") or page.get("title") or "",
            "subtitle": structured.get("subtitle") or page.get("subtitle") or "",
            "bullets": [],
            "structured": structured,
        })
    return slides_seed


# ── 主编排入口 ──

async def orchestrate_deck_generation(
    db: AsyncSession,
    user: User,
    body: AiDeckGenerateRequest,
    *,
    job_id: str = "",
) -> Project:
    """多步编排生成演示文稿：Strategist 规划 + 严格模板结构化输出。"""
    tier = body.tier or user.tier or "free"
    try:
        await check_and_consume(db, user.id, tier)
    except QuotaExceeded as exc:
        raise QuotaLlmError(str(exc)) from exc

    progress = _progress_store.get(job_id) if job_id else None
    if progress:
        progress.stage = "strategist"
        progress.phase = "规划中"
        progress.message = "正在分析主题，规划PPT结构…"

    # ── 准备变量 ──
    content_mode = body.content_mode or "free"
    page_contents = list(body.page_contents or [])
    if content_mode == "per_page":
        while len(page_contents) < body.page_count:
            page_contents.append("")
        page_contents = page_contents[:body.page_count]
    else:
        page_contents = []

    variables = {
        "page_count": body.page_count,
        "topic": _build_topic(body) if content_mode == "free" else body.topic.strip(),
        "audience": (body.audience or "通用受众").strip(),
        "style": _build_style(body),
        "language": body.language or "简体中文",
        "text_density": body.text_density or "精炼",
        "extra_instructions": (body.extra_instructions or "").strip() or "无",
        "content_mode": content_mode,
        "page_contents": page_contents,
    }

    t_total_start = time.perf_counter()
    phases_meta = {}

    try:
        # ── 解析主题色 ──
        theme_colors = _resolve_theme_colors(body)

        # ── Phase 1: Strategist ──
        logger.info("orchestrator phase1 strategist start theme=%s",
                    body.theme_id or "zjy-minimal")
        strategist_result = await _strategist_phase(body, variables, theme_colors)
        phases_meta["strategist"] = strategist_result.get("meta", {})
        pages_plan = strategist_result["pages"]
        deck_title = strategist_result["title"]

        # ── Phase 2: 结构化归一化（不再生成 SVG）──
        if progress:
            progress.total_pages = len(pages_plan)
            progress.stage = "importing"
            progress.phase = "保存中"
            progress.progress_pct = 60
            progress.message = f"规划完成，共 {len(pages_plan)} 页，正在生成结构化内容…"

        preset = (body.background_preset or "").strip()
        theme_id = (body.theme_id or "zjy-minimal").strip()
        if theme_id not in VALID_THEME_IDS:
            theme_id = "zjy-minimal"
        if preset and preset in BACKGROUND_COLORS:
            bg = BACKGROUND_COLORS[preset]
        else:
            bg = THEME_DEFAULT_GRADIENTS.get(theme_id, THEME_DEFAULT_GRADIENTS["zjy-minimal"])

        viewport_id = VIEWPORT_MAP.get(body.viewport_mode, VIEWPORT_MAP["auto"])
        slides_seed = _pages_plan_to_slides_seed(pages_plan)
        struct_warnings = _validate_slide_structure(slides_seed)

        t_total_ms = int((time.perf_counter() - t_total_start) * 1000)

        template_settings = {
            "viewportId": viewport_id,
            "scrollEffect": "vertical",
            "themeId": theme_id,
            "showScrollHint": False,
            "slideBackgrounds": {},
            "bgm": {"enabled": False, "trackId": "", "url": "", "loop": True, "volume": 0.35},
            "defaultChatTapToContinue": True,
            "aiLanguage": body.language or "简体中文",
            "generationMeta": {
                "model": "orchestrated",
                "channel": "orchestrator",
                "duration_ms": t_total_ms,
                "background_preset": preset,
                "orchestrator_phases": phases_meta,
            },
        }

        pid = new_public_id()
        project = Project(
            title=deck_title,
            theme=strategist_result.get("theme", ""),
            public_id=pid,
            share_slug=pid,
            user_id=user.id,
            settings_json=json.dumps(template_settings, ensure_ascii=False),
        )
        db.add(project)
        await db.flush()
        await seed_project_slides(db, project, slides_seed, template_settings)

        # 为每个 slide 设置背景
        slide_rows = await db.execute(
            select(Slide).where(Slide.project_id == project.id).order_by(Slide.sort_order)
        )
        sorted_slides = list(slide_rows.scalars().all())
        bg_map = {str(s.id): bg for s in sorted_slides}
        if bg_map:
            merged = {**template_settings, "slideBackgrounds": bg_map}
            project.settings_json = json.dumps(merged, ensure_ascii=False)

        # ── 聚合 token 消耗（仅 Strategist）──
        st_tokens = phases_meta.get("strategist", {}).get("tokens", {})
        total_prompt = st_tokens.get("prompt_tokens", 0)
        total_completion = st_tokens.get("completion_tokens", 0)

        log_msg = f"编排生成成功 · {len(slides_seed)} 页 · structured"
        if struct_warnings:
            log_msg += f" · 结构提示: {', '.join(struct_warnings[:5])}"

        db.add(
            GenerationLog(
                project_id=project.id,
                template_id="orchestrated_deck",
                channel="orchestrator",
                model="multi-step",
                duration_ms=t_total_ms,
                prompt_tokens=total_prompt,
                completion_tokens=total_completion,
                success=1,
                message=log_msg,
            )
        )
        await db.commit()

        if progress:
            progress.stage = "completed"
            progress.progress_pct = 100
            progress.project_public_id = pid
            progress.message = "PPT 已生成，正在跳转…"

        logger.info(
            "orchestrator complete project=%s slides=%s total_ms=%s",
            pid, len(slides_seed), t_total_ms,
        )
        return await reload_project(db, project.id)

    except Exception as exc:
        logger.error("orchestrator failed: %s", exc)
        if progress:
            progress.stage = "failed"
            progress.error = str(exc)
        raise
