"""AI 全量演示生成。"""
import json
import logging
import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog, Project, Slide, User
from app.schemas import AiDeckGenerateRequest
from app.services.deck_generator import new_public_id
from app.services.llm.provider import LlmError, chat_completion, extract_json
from app.services.project_seed_service import reload_project, seed_project_slides
from app.services.prompt_template_service import render_template
from app.services.quota import QuotaExceeded, check_and_consume

logger = logging.getLogger(__name__)

BACKGROUND_COLORS = {
    "classic_white": "#fafafa",
    "light_gray": "#f0f2f5",
}

VALID_THEME_IDS = frozenset({
    "zjy-minimal",
    "eqxiu-story",
    "tech-blue",
    "dark-pro",
    "fresh-green",
    "coral-vivid",
    "lavender-soft",
    "ocean-calm",
    "sunset-warm",
    "minimal-gray",
    "elegant-gold",
    "berry-bold",
})

THEME_DEFAULT_GRADIENTS = {
    "zjy-minimal": "linear-gradient(180deg, #FFFFFF 0%, #E8E8E8 100%)",
    "eqxiu-story": "linear-gradient(180deg, #FFF8F3 0%, #FFE8D6 100%)",
    "tech-blue": "linear-gradient(180deg, #0A1628 0%, #152238 100%)",
    "dark-pro": "linear-gradient(180deg, #1A1A1A 0%, #2D2D2D 100%)",
    "fresh-green": "linear-gradient(180deg, #F7FBF8 0%, #E8F5EC 100%)",
    "coral-vivid": "linear-gradient(180deg, #FFF5F2 0%, #FFE4DC 100%)",
    "lavender-soft": "linear-gradient(180deg, #FAF5FF 0%, #EDE9FE 100%)",
    "ocean-calm": "linear-gradient(180deg, #F0F9FF 0%, #E0F2FE 100%)",
    "sunset-warm": "linear-gradient(180deg, #FFFBEB 0%, #FEF3C7 100%)",
    "minimal-gray": "linear-gradient(180deg, #FAFAFA 0%, #F0F0F0 100%)",
    "elegant-gold": "linear-gradient(180deg, #FBF8F3 0%, #F5EDE0 100%)",
    "berry-bold": "linear-gradient(180deg, #FFF1F2 0%, #FFE4E6 100%)",
}

VIEWPORT_MAP = {
    "auto": "web-wide-1024",
    "web": "web-wide-1024",
    "mobile": "mobile-375",
}

TEXT_DENSITY_STYLE = {
    "简约": "简洁明了，每页要点极少",
    "精炼": "精炼专业，重点突出",
    "详细": "详细展开，信息充实",
    "繁琐": "详尽全面，覆盖细节",
}

VALID_TEMPLATES = frozenset({
    "cover", "section", "split_lr", "grid_2x2", "cards_row",
    "stat_hero", "steps", "quote", "closing",
})

TEMPLATE_MODULE_RULES = {
    "cover": (0, 0),
    "section": (0, 1),
    "split_lr": (2, 2),
    "grid_2x2": (4, 4),
    "cards_row": (3, 4),
    "stat_hero": (1, 1),
    "steps": (3, 3),
    "quote": (0, 0),
    "closing": (0, 0),
}


def _normalize_modules(raw: Any) -> list[dict]:
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for m in raw:
        if not isinstance(m, dict):
            continue
        mod = {
            "icon": str(m.get("icon") or "circle").strip()[:32],
            "title": str(m.get("title") or "").strip()[:120],
            "body": str(m.get("body") or "").strip()[:800],
            "emphasis": str(m.get("emphasis") or "").strip()[:120],
            "stat": str(m.get("stat") or "").strip()[:32],
            "desc": str(m.get("desc") or "").strip()[:200],
            "quote": str(m.get("quote") or "").strip()[:500],
            "author": str(m.get("author") or "").strip()[:120],
            "contact": str(m.get("contact") or "").strip()[:200],
            "role": str(m.get("role") or "").strip()[:32],
        }
        out.append({k: v for k, v in mod.items() if v})
    return out


def _extract_structured_slide(s: dict) -> dict:
    template = str(s.get("template") or s.get("layout") or "section").strip()
    if template == "bullets":
        template = "cards_row"
    if template not in VALID_TEMPLATES:
        template = "section"
    modules = _normalize_modules(s.get("modules"))
    structured = {
        "template": template,
        "title": str(s.get("title") or "")[:255],
        "subtitle": str(s.get("subtitle") or "")[:512],
        "headline": str(s.get("headline") or "")[:255],
        "modules": modules,
    }
    if s.get("quote"):
        structured["quote"] = str(s.get("quote"))[:500]
    if s.get("author"):
        structured["author"] = str(s.get("author"))[:120]
    if s.get("contact"):
        structured["contact"] = str(s.get("contact"))[:200]
    return structured


def _validate_slide_structure(slides: list[dict]) -> list[str]:
    warnings: list[str] = []
    for i, s in enumerate(slides):
        st = s.get("structured") if isinstance(s.get("structured"), dict) else {}
        template = st.get("template") or "section"
        if template == "bullets":
            warnings.append(f"slide_{i + 1}:bullets_template_rejected")
            st["template"] = "cards_row"
            s["structured"] = st
        modules = st.get("modules") or []
        min_m, max_m = TEMPLATE_MODULE_RULES.get(template, (0, 99))
        if template in ("grid_2x2", "cards_row", "split_lr", "steps", "stat_hero"):
            if len(modules) < min_m:
                warnings.append(f"slide_{i + 1}:modules_underflow")
        for mod in modules:
            body = mod.get("body") or ""
            if len(body) > 120:
                warnings.append(f"slide_{i + 1}:text_overflow_risk")
        if template not in ("cover", "section", "closing", "quote") and not modules and not st.get("headline"):
            warnings.append(f"slide_{i + 1}:missing_modules_or_headline")
    return warnings


def _llm_slides_to_seed(slides: list[dict], bg: str) -> list[dict]:
    out: list[dict] = []
    for s in slides:
        structured = _extract_structured_slide(s)
        template = structured["template"]
        out.append(
            {
                "layout": template[:32],
                "title": structured["title"],
                "subtitle": structured["subtitle"],
                "bullets": [],
                "speakerNotes": str(s.get("speakerNotes", s.get("speaker_notes", "")))[:8000],
                "animation": str(s.get("animation", "fade"))[:32],
                "canvas_background": bg,
                "canvas_elements": s.get("canvas_elements") if isinstance(s.get("canvas_elements"), list) else [],
                "structured": structured,
            }
        )
    return out


def _build_topic(body: AiDeckGenerateRequest) -> str:
    parts = [body.topic.strip()]
    if body.extra_content and body.extra_content.strip():
        parts.append(body.extra_content.strip())
    return "\n\n".join(parts)


def _normalize_deck_json(data: dict[str, Any], page_count: int) -> tuple[str, str, list[dict]]:
    title = str(data.get("title") or "AI 生成的演示").strip()[:120]
    theme = str(data.get("theme") or "ai-generated").strip()[:64]
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        raise LlmError("大模型未返回有效的 slides 数组")
    if len(slides) > page_count:
        slides = slides[:page_count]
    return title, theme, slides


def _build_style(body: AiDeckGenerateRequest) -> str:
    density = TEXT_DENSITY_STYLE.get(body.text_density, body.text_density)
    tone = (body.tone or "").strip()
    style = (body.style or "").strip()
    bits = [density]
    if tone:
        bits.append(f"语气：{tone}")
    if style:
        bits.append(style)
    return "；".join(bits)


async def generate_deck_from_ai(
    db: AsyncSession,
    user: User,
    body: AiDeckGenerateRequest,
) -> Project:
    tier = body.tier or user.tier or "free"
    try:
        await check_and_consume(db, user.id, tier)
    except QuotaExceeded as exc:
        raise LlmError(str(exc)) from exc

    content_mode = body.content_mode or "free"
    page_contents = list(body.page_contents or [])
    if content_mode == "per_page":
        while len(page_contents) < body.page_count:
            page_contents.append("")
        page_contents = page_contents[: body.page_count]
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

    messages = render_template("全量生成.yaml", variables)
    model_override = (body.model or "").strip() or None
    logger.info(
        "deck_generate start user_id=%s pages=%s mode=%s model=%s",
        user.id,
        body.page_count,
        content_mode,
        model_override or "(default)",
    )
    t0 = time.perf_counter()
    raw = ""
    channel = ""
    model = ""
    try:
        raw, channel, model = await chat_completion(
            messages,
            channel=body.channel,
            tier=tier,
            model=model_override,
        )
        logger.info(
            "deck_generate llm_done user_id=%s channel=%s model=%s raw_len=%s",
            user.id,
            channel,
            model,
            len(raw),
        )
        data = extract_json(raw)
        title, theme, slides_raw = _normalize_deck_json(data, body.page_count)
        logger.info(
            "deck_generate parsed user_id=%s title=%r slides=%s",
            user.id,
            title[:80],
            len(slides_raw),
        )
    except LlmError:
        raise
    except Exception as exc:
        raise LlmError(f"生成失败：{exc}") from exc
    duration_ms = int((time.perf_counter() - t0) * 1000)

    try:
        preset = (body.background_preset or "").strip()
        theme_id = (body.theme_id or "zjy-minimal").strip()
        if theme_id not in VALID_THEME_IDS:
            theme_id = "zjy-minimal"
        if preset and preset in BACKGROUND_COLORS:
            bg = BACKGROUND_COLORS[preset]
        else:
            bg = THEME_DEFAULT_GRADIENTS.get(theme_id, THEME_DEFAULT_GRADIENTS["zjy-minimal"])
        viewport_id = VIEWPORT_MAP.get(body.viewport_mode, VIEWPORT_MAP["auto"])
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
                "model": model,
                "channel": channel,
                "duration_ms": duration_ms,
                "background_preset": preset,
            },
        }
        slides_seed = _llm_slides_to_seed(slides_raw, bg)
        struct_warnings = _validate_slide_structure(slides_seed)
        log_msg = f"AI 全量生成成功 · {len(slides_seed)} 页"
        if struct_warnings:
            log_msg += f" · 结构提示: {', '.join(struct_warnings[:5])}"

        pid = new_public_id()
        project = Project(
            title=title,
            theme=theme,
            public_id=pid,
            share_slug=pid,
            user_id=user.id,
            settings_json=json.dumps(template_settings, ensure_ascii=False),
        )
        db.add(project)
        await db.flush()
        logger.info("deck_generate project_flushed user_id=%s project_id=%s", user.id, project.id)
        await seed_project_slides(db, project, slides_seed, template_settings)
        logger.info(
            "deck_generate slides_seeded user_id=%s project_id=%s count=%s",
            user.id,
            project.id,
            len(slides_seed),
        )

        slide_rows = await db.execute(
            select(Slide).where(Slide.project_id == project.id).order_by(Slide.sort_order)
        )
        sorted_slides = list(slide_rows.scalars().all())
        bg_map = {str(s.id): bg for s in sorted_slides}
        if bg_map:
            merged = {**template_settings, "slideBackgrounds": bg_map}
            project.settings_json = json.dumps(merged, ensure_ascii=False)

        db.add(
            GenerationLog(
                project_id=project.id,
                template_id="full_deck",
                channel=channel,
                model=model,
                duration_ms=duration_ms,
                success=1,
                message=log_msg,
            )
        )
        await db.commit()
        logger.info(
            "deck_generate committed user_id=%s project_id=%s duration_ms=%s",
            user.id,
            project.id,
            duration_ms,
        )
    except Exception as exc:
        logger.error(
            "deck_generate persist_failed user_id=%s err=%s raw_preview=%s",
            user.id,
            exc,
            (raw[:2048] if raw else ""),
        )
        raise

    return await reload_project(db, project.id)
