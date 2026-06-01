"""AI 全量演示生成。"""
import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog, Project, User
from app.schemas import AiDeckGenerateRequest
from app.services.deck_generator import new_share_slug
from app.services.llm.provider import LlmError, chat_completion, extract_json
from app.services.project_seed_service import reload_project, seed_project_slides
from app.services.prompt_template_service import render_template
from app.services.quota import QuotaExceeded, check_and_consume

BACKGROUND_COLORS = {
    "classic_white": "#fafafa",
    "light_gray": "#f0f2f5",
}

VIEWPORT_MAP = {
    "auto": "mobile-375",
    "web": "web-1280",
    "mobile": "mobile-375",
}

TEXT_DENSITY_STYLE = {
    "简约": "简洁明了，每页要点极少",
    "精炼": "精炼专业，重点突出",
    "详细": "详细展开，信息充实",
    "繁琐": "详尽全面，覆盖细节",
}


def _build_topic(body: AiDeckGenerateRequest) -> str:
    parts = [body.topic.strip()]
    if body.extra_content and body.extra_content.strip():
        parts.append(body.extra_content.strip())
    return "\n\n".join(parts)


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


def _llm_slides_to_seed(slides: list[dict], bg: str) -> list[dict]:
    out: list[dict] = []
    for s in slides:
        out.append(
            {
                "layout": s.get("layout", "bullets"),
                "title": s.get("title", ""),
                "subtitle": s.get("subtitle", ""),
                "bullets": s.get("bullets") or [],
                "speakerNotes": s.get("speakerNotes", s.get("speaker_notes", "")),
                "animation": s.get("animation", "fade"),
                "canvas_background": bg,
                "canvas_elements": s.get("canvas_elements") or [],
            }
        )
    return out


def _normalize_deck_json(data: dict[str, Any], page_count: int) -> tuple[str, str, list[dict]]:
    title = str(data.get("title") or "AI 生成的演示").strip()[:120]
    theme = str(data.get("theme") or "ai-generated").strip()[:64]
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        raise LlmError("大模型未返回有效的 slides 数组")
    if len(slides) > page_count:
        slides = slides[:page_count]
    return title, theme, slides


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

    variables = {
        "page_count": body.page_count,
        "topic": _build_topic(body),
        "audience": (body.audience or "通用受众").strip(),
        "style": _build_style(body),
        "language": body.language or "简体中文",
        "text_density": body.text_density or "精炼",
        "extra_instructions": (body.extra_instructions or "").strip() or "无",
    }

    messages = render_template("全量生成.yaml", variables)
    try:
        raw, channel, model = await chat_completion(messages, channel=body.channel, tier=tier)
        data = extract_json(raw)
        title, theme, slides_raw = _normalize_deck_json(data, body.page_count)
    except LlmError:
        raise
    except Exception as exc:
        raise LlmError(f"生成失败：{exc}") from exc

    bg = BACKGROUND_COLORS.get(body.background_preset, BACKGROUND_COLORS["classic_white"])
    viewport_id = VIEWPORT_MAP.get(body.viewport_mode, VIEWPORT_MAP["auto"])
    template_settings = {
        "viewportId": viewport_id,
        "scrollEffect": "vertical",
        "themeId": "zjy-minimal",
        "showScrollHint": False,
        "slideBackgrounds": {},
        "bgm": {"enabled": False, "trackId": "", "url": "", "loop": True, "volume": 0.35},
        "defaultChatTapToContinue": True,
        "aiLanguage": body.language or "简体中文",
    }
    slides_seed = _llm_slides_to_seed(slides_raw, bg)

    project = Project(
        title=title,
        theme=theme,
        share_slug=new_share_slug(),
        user_id=user.id,
        settings_json=json.dumps(template_settings, ensure_ascii=False),
    )
    db.add(project)
    await db.flush()
    await seed_project_slides(db, project, slides_seed, template_settings)

    # 统一背景到所有页
    sorted_slides = sorted(project.slides, key=lambda x: x.sort_order)
    bg_map = {str(s.id): bg for s in sorted_slides}
    if bg_map:
        merged = {**template_settings, "slideBackgrounds": bg_map}
        project.settings_json = json.dumps(merged, ensure_ascii=False)

    db.add(
        GenerationLog(
            project_id=project.id,
            template_id="full_deck",
            channel=channel,
            success=1,
            message=f"AI 全量生成成功 · {len(slides_seed)} 页",
        )
    )
    await db.commit()
    return await reload_project(db, project.id)
