"""AI 全量演示生成。"""
import json
import logging
import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog, Project, Slide, User
from app.services.image_search_service import search_image
from app.schemas import AiDeckGenerateRequest, AiSlideGenerateRequest
from app.services.deck_generator import new_public_id
from app.services.llm.image_provider import generate_image
from app.services.llm.provider import LlmError, QuotaLlmError, chat_completion, extract_json
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
    "auto": "web-1280",
    "web": "web-1280",
    "mobile": "mobile-375",
}

VIEWPORT_SIZES = {
    "web-wide-1024": (1024, 401),
    "web-1280": (1280, 720),
    "web-1920": (1920, 1080),
    "web-1024": (1024, 768),
    "mobile-375": (375, 812),
    "mobile-390": (390, 844),
    "mobile-360": (360, 780),
}

TEXT_DENSITY_STYLE = {
    "简约": "简洁明了，每页要点极少",
    "精炼": "精炼专业，重点突出",
    "详细": "详细展开，信息充实",
    "完整": "详尽全面，覆盖细节",
}

VALID_TEMPLATES = frozenset({
    "cover", "section", "split_lr", "grid_2x2", "cards_row",
    "stat_hero", "steps", "quote", "closing",
})

FIXED_LAYOUT_IDS = frozenset({
    "cover_title",
    "toc",
    "chapter_divider",
    "roadmap_bottom",
    "scene_left",
    "chart_left",
    "key_points",
    "closing",
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

VISUAL_TO_LAYOUT = {
    "roadmap": "roadmap_bottom",
    "scene": "scene_left",
    "chart": "chart_left",
    "none": "key_points",
}

# ── 严格PPT模板约束模式 ──
STRICT_TEMPLATE_TYPES = frozenset({
    "title_page", "toc", "points", "cards",
    "image_text_left", "image_text_right",
})

STRICT_TEMPLATE_ICONS = [
    "target", "bolt", "trending_up", "bar_chart", "school",
    "database", "settings", "star", "lightbulb", "groups",
    "check_circle", "rocket_launch", "emoji_objects", "insights",
    "handshake", "shield", "cloud", "devices", "palette", "campaign",
]


def _clean_text(value: Any, limit: int = 255) -> str:
    return str(value or "").strip()[:limit]


def _normalize_points(raw: Any, limit: int = 4) -> list[dict]:
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for item in raw:
        if isinstance(item, str):
            title = item.strip()
            body = ""
            icon = "circle"
        elif isinstance(item, dict):
            title = _clean_text(item.get("title") or item.get("label") or item.get("name"), 48)
            body = _clean_text(item.get("body") or item.get("desc") or item.get("description"), 120)
            icon = _clean_text(item.get("icon") or "circle", 32)
        else:
            continue
        if title or body:
            out.append({"icon": icon or "circle", "title": title, "body": body})
        if len(out) >= limit:
            break
    return out


def _fallback_points_from_text(*values: Any, limit: int = 4) -> list[dict]:
    chunks: list[str] = []
    for value in values:
        text = _clean_text(value, 600)
        if not text:
            continue
        for sep in ("。", "；", ";", "\n", "."):
            text = text.replace(sep, "|")
        chunks.extend(part.strip() for part in text.split("|") if part.strip())
    out: list[dict] = []
    for i, chunk in enumerate(chunks[:limit]):
        out.append({
            "icon": ["target", "bolt", "trending_up", "database"][i % 4],
            "title": chunk[:48],
            "body": "",
        })
    return out


def _normalize_chart(raw: Any) -> dict:
    if not isinstance(raw, dict):
        return {}
    labels = raw.get("labels") if isinstance(raw.get("labels"), list) else []
    values = raw.get("values") if isinstance(raw.get("values"), list) else []
    pairs: list[tuple[str, float]] = []
    for i in range(min(len(labels), len(values), 6)):
        try:
            value = float(values[i])
        except (TypeError, ValueError):
            value = 0
        pairs.append((_clean_text(labels[i], 16), value))
    if not pairs:
        return {}
    return {
        "type": "pie" if raw.get("type") == "pie" or raw.get("chartType") == "pie" else "bar",
        "title": _clean_text(raw.get("title"), 80),
        "labels": [p[0] for p in pairs],
        "values": [p[1] for p in pairs],
    }


def _infer_visual_intent(slide: dict) -> str:
    visual = _clean_text(slide.get("visual_intent") or slide.get("visual"), 32)
    if visual in {"roadmap", "scene", "chart", "none"}:
        return visual
    if slide.get("chart"):
        return "chart"
    if slide.get("image_intent") == "roadmap":
        return "roadmap"
    if slide.get("image_intent") == "scene" or slide.get("image_prompt"):
        return "scene"
    return "none"


def _normalize_fixed_layout_slide(raw: dict, index: int, total: int) -> dict:
    visual = _infer_visual_intent(raw)
    layout_id = _clean_text(raw.get("layout_id") or raw.get("fixed_layout") or "", 32)
    if layout_id not in FIXED_LAYOUT_IDS:
        if raw.get("is_chapter") is True:
            layout_id = "chapter_divider"
        elif raw.get("chart"):
            layout_id = "chart_left"
        elif raw.get("image_prompt") or raw.get("image_url"):
            layout_id = "scene_left" if visual != "roadmap" else "roadmap_bottom"
        else:
            layout_id = VISUAL_TO_LAYOUT.get(visual, "key_points")

    points = _normalize_points(
        raw.get("points") or raw.get("steps") or raw.get("blocks") or raw.get("modules"),
        6 if layout_id == "toc" else 4,
    )
    if not points and layout_id in {"key_points", "roadmap_bottom", "toc"}:
        points = _fallback_points_from_text(
            raw.get("insight") or raw.get("summary"),
            raw.get("body") or raw.get("description"),
            raw.get("subtitle"),
            raw.get("title"),
            limit=6 if layout_id == "toc" else 4,
        )
    chart = _normalize_chart(raw.get("chart"))
    structured = {
        "layout_id": layout_id,
        "title": _clean_text(raw.get("title"), 255),
        "subtitle": _clean_text(raw.get("subtitle"), 512),
        "headline": _clean_text(raw.get("headline"), 255),
        "insight": _clean_text(raw.get("insight") or raw.get("summary"), 255),
        "body": _clean_text(raw.get("body") or raw.get("description"), 600),
        "visual_intent": visual,
        "points": points,
        "steps": points,
        "chart": chart,
        "image_prompt": _clean_text(raw.get("image_prompt"), 120),
        "image_url": _clean_text(raw.get("image_url"), 4096),
        "contact": _clean_text(raw.get("contact"), 200),
    }
    return {k: v for k, v in structured.items() if v not in ("", [], {})}


def _build_toc_points(slides: list[dict]) -> list[dict]:
    items: list[dict] = []
    for slide in slides[2:]:
        st = slide.get("structured") if isinstance(slide.get("structured"), dict) else {}
        title = _clean_text(st.get("title") or slide.get("title"), 48)
        if title and st.get("layout_id") != "closing":
            items.append({"icon": "circle", "title": title, "body": ""})
        if len(items) >= 6:
            break
    return items


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
            "body": str(m.get("body") or "").strip()[:120],
            "emphasis": str(m.get("emphasis") or "").strip()[:120],
            "stat": str(m.get("stat") or "").strip()[:32],
            "desc": str(m.get("desc") or "").strip()[:200],
            "quote": str(m.get("quote") or "").strip()[:500],
            "author": str(m.get("author") or "").strip()[:120],
            "contact": str(m.get("contact") or "").strip()[:200],
            "role": str(m.get("role") or "").strip()[:32],
            "image_intent": str(m.get("image_intent") or "").strip()[:32],
            "image_prompt": str(m.get("image_prompt") or "").strip()[:120],
        }
        if m.get("image_url"):
            mod["image_url"] = str(m.get("image_url")).strip()[:4096]
        out.append({k: v for k, v in mod.items() if v})
    return out


def _normalize_strict_slide(raw: dict, index: int = 0, total: int = 1) -> dict:
    """将严格模板AI输出规范化为structured dict。
    AI不输出icon/variant/image_query — 全部由后端/前端自动处理。"""
    template_type = str(raw.get("template_type") or "points").strip()
    if template_type not in STRICT_TEMPLATE_TYPES:
        template_type = "points"

    base = {
        "template_type": template_type,
        "title": _clean_text(raw.get("title"), 255),
        "subtitle": _clean_text(raw.get("subtitle"), 512),
    }

    if template_type == "title_page":
        base["author"] = _clean_text(raw.get("author"), 64)
        base["date"] = _clean_text(raw.get("date"), 32)

    elif template_type == "toc":
        items = raw.get("items") or raw.get("points") or []
        if isinstance(items, list):
            normalized = []
            for item in items:
                if isinstance(item, str):
                    normalized.append({"num": "", "title": _clean_text(item, 60)})
                elif isinstance(item, dict):
                    normalized.append({
                        "num": _clean_text(item.get("num") or "", 8),
                        "title": _clean_text(item.get("title") or item.get("body") or "", 60),
                    })
                if len(normalized) >= 8:
                    break
            base["items"] = normalized
        else:
            base["items"] = []

    elif template_type == "points":
        raw_points = raw.get("points") or []
        if not isinstance(raw_points, list):
            raw_points = []
        normalized = []
        for pt in raw_points[:5]:
            if isinstance(pt, str):
                normalized.append({"text": _clean_text(pt, 120)})
            elif isinstance(pt, dict):
                normalized.append({
                    "text": _clean_text(pt.get("text") or pt.get("title") or pt.get("body") or "", 120),
                })
        # 至少1个要点
        if not normalized:
            normalized.append({"text": "要点内容"})
        base["variant"] = len(normalized)  # 自动计算
        base["points"] = normalized

    elif template_type == "cards":
        raw_cards = raw.get("cards") or []
        if not isinstance(raw_cards, list):
            raw_cards = []
        normalized = []
        for card in raw_cards[:4]:
            if isinstance(card, str):
                normalized.append({"title": _clean_text(card, 48), "body": ""})
            elif isinstance(card, dict):
                normalized.append({
                    "title": _clean_text(card.get("title") or "", 48),
                    "body": _clean_text(card.get("body") or card.get("text") or "", 160),
                })
        if not normalized:
            normalized.append({"title": "卡片标题", "body": "内容待补充"})
        base["variant"] = len(normalized)  # 自动计算
        base["cards"] = normalized

    elif template_type in ("image_text_left", "image_text_right"):
        content_type = str(raw.get("content_type") or "points").strip()
        if content_type not in ("points", "cards"):
            content_type = "points"
        base["content_type"] = content_type
        # 图片搜索关键词（中文，3-5个词）
        base["image_topic"] = _clean_text(raw.get("image_topic") or "", 120)

        if content_type == "points":
            raw_points = raw.get("points") or []
            if not isinstance(raw_points, list):
                raw_points = []
            normalized = []
            for pt in raw_points[:4]:
                if isinstance(pt, str):
                    normalized.append({"text": _clean_text(pt, 120)})
                elif isinstance(pt, dict):
                    normalized.append({
                        "text": _clean_text(pt.get("text") or pt.get("title") or pt.get("body") or "", 120),
                    })
            if not normalized:
                normalized.append({"text": "要点内容"})
            base["variant"] = len(normalized)
            base["points"] = normalized
        else:
            raw_cards = raw.get("cards") or []
            if not isinstance(raw_cards, list):
                raw_cards = []
            normalized = []
            for card in raw_cards[:3]:
                if isinstance(card, str):
                    normalized.append({"title": _clean_text(card, 48), "body": ""})
                elif isinstance(card, dict):
                    normalized.append({
                        "title": _clean_text(card.get("title") or "", 48),
                        "body": _clean_text(card.get("body") or card.get("text") or "", 160),
                    })
            if not normalized:
                normalized.append({"title": "卡片标题", "body": "内容待补充"})
            base["variant"] = len(normalized)
            base["cards"] = normalized

    return {k: v for k, v in base.items() if v not in ("", [], {})}


def _extract_structured_slide(s: dict, index: int = 0, total: int = 1) -> dict:
    # 严格模板约束模式：检测 template_type 字段
    template_type = str(s.get("template_type") or "").strip()
    if template_type in STRICT_TEMPLATE_TYPES:
        return _normalize_strict_slide(s, index, total)

    if s.get("layout_id") or s.get("fixed_layout") or s.get("visual_intent") or s.get("chart"):
        return _normalize_fixed_layout_slide(s, index, total)

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
    if s.get("image_prompt"):
        structured["image_prompt"] = str(s.get("image_prompt"))[:120]
    if s.get("image_intent"):
        structured["image_intent"] = str(s.get("image_intent"))[:32]
    if s.get("image_url"):
        structured["image_url"] = str(s.get("image_url"))[:4096]
    return structured


def _validate_slide_structure(slides: list[dict]) -> list[str]:
    warnings: list[str] = []
    for i, s in enumerate(slides):
        st = s.get("structured") if isinstance(s.get("structured"), dict) else {}

        # 严格模板约束模式：验证 template_type
        ttype = st.get("template_type") or ""
        if ttype in STRICT_TEMPLATE_TYPES:
            if ttype in ("image_text_left", "image_text_right"):
                if not st.get("image_topic"):
                    warnings.append(f"slide_{i + 1}:image_topic_missing")
            continue

        if st.get("layout_id"):
            if st["layout_id"] not in FIXED_LAYOUT_IDS:
                warnings.append(f"slide_{i + 1}:fixed_layout_rejected")
                st["layout_id"] = "key_points"
            if st["layout_id"] == "chart_left" and not st.get("chart"):
                warnings.append(f"slide_{i + 1}:chart_missing")
            if st["layout_id"] in {"scene_left", "roadmap_bottom"} and not (st.get("image_prompt") or st.get("image_url")):
                warnings.append(f"slide_{i + 1}:image_prompt_missing")
            continue
        template = st.get("template") or "section"
        if template == "bullets":
            warnings.append(f"slide_{i + 1}:bullets_template_rejected")
            st["template"] = "cards_row"
            s["structured"] = st
        modules = st.get("modules") or []
        min_m, max_m = TEMPLATE_MODULE_RULES.get(template, (0, 99))
        if template == "grid_2x2":
            while len(modules) < 4:
                modules.append({
                    "icon": "circle",
                    "title": "模块",
                    "body": "内容",
                })
            st["modules"] = modules[:4]
            s["structured"] = st
        if template in ("grid_2x2", "cards_row", "split_lr", "steps", "stat_hero"):
            if len(modules) < min_m:
                warnings.append(f"slide_{i + 1}:modules_underflow")
        for mod in modules:
            body = mod.get("body") or ""
            if len(body) > 120:
                warnings.append(f"slide_{i + 1}:text_overflow_risk")
        if template not in ("cover", "section", "closing", "quote") and not modules and not st.get("headline"):
            warnings.append(f"slide_{i + 1}:missing_modules_or_headline")

    # ── 跨页检测：相邻页标题是否疑似同一节被拆分 ──
    for i in range(1, len(slides)):
        prev_st = slides[i - 1].get("structured") if isinstance(slides[i - 1].get("structured"), dict) else {}
        curr_st = slides[i].get("structured") if isinstance(slides[i].get("structured"), dict) else {}
        prev_title = str(prev_st.get("title") or "").strip()
        curr_title = str(curr_st.get("title") or "").strip()
        if not prev_title or not curr_title:
            continue
        # 完全相同 → 明确拆分问题
        if prev_title == curr_title:
            warnings.append(f"slide_{i + 1}:title_identical_to_prev(可能同一节被拆分)")
        # 前缀相同（如 "4.4 盈利策略" 和 "4.4 盈利策略（续）"）
        elif len(prev_title) >= 6 and len(curr_title) >= 6:
            short = min(len(prev_title), len(curr_title))
            common = 0
            for j in range(short):
                if prev_title[j] == curr_title[j]:
                    common += 1
                else:
                    break
            if common >= 6 and common >= short * 0.7:
                warnings.append(f"slide_{i + 1}:title_similar_to_prev(common_prefix={common}chars)")

    return warnings


def _llm_slides_to_seed(slides: list[dict], bg: str) -> list[dict]:
    out: list[dict] = []
    for idx, s in enumerate(slides):
        structured = _extract_structured_slide(s, idx, len(slides))
        template = structured.get("layout_id") or structured.get("template") or structured.get("template_type") or "key_points"
        out.append(
            {
                "layout": template[:32],
                "title": structured.get("title", ""),
                "subtitle": structured.get("subtitle", ""),
                "bullets": [],
                "speakerNotes": str(s.get("speakerNotes", s.get("speaker_notes", "")))[:8000],
                "animation": str(s.get("animation", "fade"))[:32],
                "canvas_background": bg,
                "canvas_elements": [],
                "structured": structured,
            }
        )
    if len(out) >= 4 and out[1].get("structured", {}).get("layout_id") == "toc":
        toc = out[1]["structured"]
        if not toc.get("points"):
            toc["points"] = _build_toc_points(out)
            toc["steps"] = toc["points"]
    return out


def _build_deck_image_prompt(
    prompt: str,
    *,
    slide_title: str = "",
    deck_title: str = "",
    slot: str = "scene",
) -> str:
    scene = str(prompt or "").strip()
    slide = str(slide_title or "").strip()
    topic = str(deck_title or "").strip()
    lines: list[str] = []
    if topic:
        lines.append(f"演示主题：{topic}")
    if slide and slide != scene:
        lines.append(f"本页标题：{slide}")
    lines.append(f"画面内容：{scene or slide or topic}")
    if slot == "cover":
        lines.append(
            "专业演示封面主视觉，写实摄影或高质量插画，与上述主题高度相关，"
            "现代商务/教育场景，无文字、无水印、无 Logo。"
        )
    elif slot == "roadmap":
        lines.append(
            "专业流程路线图/信息图插画，清晰展示步骤与流向，与上述主题高度相关，"
            "扁平或商务风格，无文字、无水印、无 Logo。"
        )
    else:
        lines.append(
            "专业商务/教育场景配图，写实摄影风格，与上述主题高度相关，"
            "如管理者查看数据大屏、教师在智慧教室使用平板等，无文字、无水印、无 Logo。"
        )
    return "\n".join(lines)


async def _generate_deck_image_with_retry(
    prompt: str,
    *,
    channel: str | None,
    tier: str,
    width: int,
    height: int,
    viewport_id: str,
) -> str:
    last_err: Exception | None = None
    for attempt in range(2):
        try:
            url, _, _, _, _ = await generate_image(
                prompt,
                channel=channel,
                tier=tier,
                viewport_width=width,
                viewport_height=height,
                viewport_preset_id=viewport_id,
            )
            if url and str(url).strip():
                return str(url).strip()
        except Exception as exc:
            last_err = exc
            if attempt == 0:
                logger.info("deck_image_enrich retry prompt=%s err=%s", prompt[:80], exc)
    if last_err:
        raise last_err
    raise RuntimeError("生图结果为空，请重试")


def _collect_image_jobs(slides_seed: list[dict]) -> list[tuple[int, str, str]]:
    """仅 image_intent 为 cover_bg / scene / roadmap 且含 image_prompt 的页入队生图；无 title 兜底。"""
    jobs: list[tuple[int, str, str]] = []
    for i, slide in enumerate(slides_seed):
        st = slide.get("structured") if isinstance(slide.get("structured"), dict) else {}
        layout_id = st.get("layout_id") or ""
        if layout_id == "scene_left":
            prompt = str(st.get("image_prompt") or "").strip()
            if prompt:
                jobs.append((i, "fixed_scene", prompt))
            continue
        if layout_id == "roadmap_bottom":
            prompt = str(st.get("image_prompt") or "").strip()
            if prompt:
                jobs.append((i, "fixed_roadmap", prompt))
            continue

        template = st.get("template") or ""
        if template == "cover":
            if str(st.get("image_intent") or "").strip() != "cover_bg":
                continue
            prompt = str(st.get("image_prompt") or "").strip()
            if prompt:
                jobs.append((i, "cover", prompt))
        elif template == "split_lr":
            modules = st.get("modules") or []
            if len(modules) < 2:
                continue
            right = modules[1]
            intent = str(right.get("image_intent") or "").strip()
            if intent != "scene":
                continue
            prompt = str(right.get("image_prompt") or "").strip()
            if prompt:
                jobs.append((i, "split_right", prompt))
        elif template == "steps":
            if str(st.get("image_intent") or "").strip() != "roadmap":
                continue
            prompt = str(st.get("image_prompt") or "").strip()
            if prompt:
                jobs.append((i, "roadmap", prompt))
    return jobs


async def _enrich_slide_images(
    slides_seed: list[dict],
    viewport_id: str,
    tier: str,
    channel: str | None,
    page_count: int,
    deck_title: str = "",
) -> int:
    vp_w, vp_h = VIEWPORT_SIZES.get(viewport_id, VIEWPORT_SIZES["web-wide-1024"])
    cover_img_w = max(200, round(vp_w * 0.38))
    cover_img_h = vp_h
    split_img_w = max(200, round(vp_w * 0.48))
    split_img_h = max(200, round(vp_h * 0.75))
    roadmap_img_w = vp_w
    roadmap_img_h = max(200, round(vp_h * 0.28))

    jobs = _collect_image_jobs(slides_seed)
    max_images = max(1, min(len(jobs), page_count // 2 + 1))
    jobs = jobs[:max_images]

    generated = 0
    for slide_idx, slot, prompt in jobs:
        st = slides_seed[slide_idx]["structured"]
        slide_title = str(st.get("title") or "").strip()
        slot_key = "roadmap" if slot == "fixed_roadmap" else slot if slot in ("cover", "roadmap") else "scene"
        full_prompt = _build_deck_image_prompt(
            prompt,
            slide_title=slide_title,
            deck_title=deck_title,
            slot=slot_key,
        )
        try:
            if slot == "cover":
                url = await _generate_deck_image_with_retry(
                    full_prompt,
                    channel=channel,
                    tier=tier,
                    width=cover_img_w,
                    height=cover_img_h,
                    viewport_id=viewport_id,
                )
                st["image_url"] = url
                st["image_intent"] = "cover_bg"
                generated += 1
            elif slot == "fixed_scene":
                url = await _generate_deck_image_with_retry(
                    full_prompt,
                    channel=channel,
                    tier=tier,
                    width=split_img_w,
                    height=split_img_h,
                    viewport_id=viewport_id,
                )
                st["image_url"] = url
                generated += 1
            elif slot == "split_right":
                url = await _generate_deck_image_with_retry(
                    full_prompt,
                    channel=channel,
                    tier=tier,
                    width=split_img_w,
                    height=split_img_h,
                    viewport_id=viewport_id,
                )
                modules = st.setdefault("modules", [])
                while len(modules) < 2:
                    modules.append({})
                modules[1]["image_url"] = url
                modules[1]["image_intent"] = "scene"
                if not modules[1].get("role"):
                    modules[1]["role"] = "scene_image"
                generated += 1
            elif slot == "fixed_roadmap":
                url = await _generate_deck_image_with_retry(
                    full_prompt,
                    channel=channel,
                    tier=tier,
                    width=roadmap_img_w,
                    height=roadmap_img_h,
                    viewport_id=viewport_id,
                )
                st["image_url"] = url
                generated += 1
            elif slot == "roadmap":
                url = await _generate_deck_image_with_retry(
                    full_prompt,
                    channel=channel,
                    tier=tier,
                    width=roadmap_img_w,
                    height=roadmap_img_h,
                    viewport_id=viewport_id,
                )
                st["image_url"] = url
                st["image_intent"] = "roadmap"
                generated += 1
        except Exception as exc:
            logger.warning(
                "deck_image_enrich failed slide=%s slot=%s err=%s",
                slide_idx,
                slot,
                exc,
            )
    return generated


async def _enrich_strict_images(slides_seed: list[dict]) -> int:
    """为严格模板 slides 搜索Unsplash/Pexels素材图片。
    仅处理含 image_topic 的 image_text_left/right 页，每页约0.5秒。"""
    generated = 0
    for i, slide in enumerate(slides_seed):
        st = slide.get("structured") if isinstance(slide.get("structured"), dict) else {}
        image_topic = str(st.get("image_topic") or "").strip()
        if not image_topic:
            continue
        try:
            url = await search_image(image_topic, orientation="landscape")
            if url:
                st["image_url"] = url
                slide["structured"] = st
                generated += 1
                logger.info("strict_image found for slide_%s topic=%r", i + 1, image_topic[:60])
            else:
                logger.info("strict_image not found for slide_%s topic=%r", i + 1, image_topic[:60])
        except Exception as exc:
            logger.warning("strict_image search error slide_%s: %s", i + 1, exc)
    return generated


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
        raise QuotaLlmError(str(exc)) from exc

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

    # 严格模板模式使用专用Prompt
    prompt_template = "严格模板生成.yaml" if body.strict_template_mode else "固定布局生成.yaml"
    messages = render_template(prompt_template, variables)
    model_override = (body.model or "").strip() or None
    logger.info(
        "deck_generate start user_id=%s pages=%s mode=%s strict=%s model=%s",
        user.id,
        body.page_count,
        content_mode,
        body.strict_template_mode,
        model_override or "(default)",
    )
    t0 = time.perf_counter()
    raw = ""
    channel = ""
    model = ""
    try:
        logger.info("deck_generate llm_call_start t=0.0s")
        raw, channel, model = await chat_completion(
            messages,
            channel=body.channel,
            tier=tier,
            model=model_override,
        )
        logger.info("deck_generate llm_call_done t=%.1fs", time.perf_counter() - t0)
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
        # 严格模板模式：用素材搜索替代AI生图（快30-60倍）
        t_img = time.perf_counter()
        if body.strict_template_mode:
            images_generated = await _enrich_strict_images(slides_seed)
            logger.info("deck_generate strict_images_done t=%.1fs count=%s", time.perf_counter() - t0, images_generated)
        else:
            images_generated = await _enrich_slide_images(
                slides_seed,
                viewport_id,
                tier,
                body.channel,
                body.page_count,
                deck_title=title,
            )
            logger.info("deck_generate ai_images_done t=%.1fs count=%s", time.perf_counter() - t0, images_generated)
        if images_generated:
            template_settings["generationMeta"]["images_generated"] = images_generated
        log_msg = f"AI 全量生成成功 · {len(slides_seed)} 页"
        if images_generated:
            log_msg += f" · 配图 {images_generated} 张"
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


TEMPLATE_HINT_INSTRUCTIONS = {
    "magic": "自动选择最合适的 template_type（6种严格模板：title_page/toc/points/cards/image_text_left/image_text_right）",
    "bullets": "必须输出要点式内容，优先 points 模板；提供 2-5 个 points，每个要点独立成段，纯文字无需配图",
    "paragraph": "必须输出段落式内容，优先 points 或 cards 模板；以一段完整说明为主，然后根据内容拆分为子要点",
    "cards": "必须输出卡片式内容，优先 cards 模板；拆分为 2-4 张独立卡片，每张有标题和正文",
    "image_text": "必须输出图片配文字结构，优先 image_text_left 模板；提供 image_topic（3-5个中文关键词）用于配图搜索，左侧图片右侧内容",
    "split": "使用 image_text_left 或 image_text_right 模板，左右分栏",
    "image": "使用 image_text_left 或 image_text_right 模板，必须提供 image_topic",
    "grid": "使用 cards 模板，多卡片并列展示",
    "text": "优先 points 或 cards 模板，以文字内容为主",
}


def compute_insert_sort_order(slides: list, after_slide_id: int | None) -> int:
    sorted_slides = sorted(slides, key=lambda s: s.sort_order)
    if after_slide_id is None:
        if not sorted_slides:
            return 0
        return sorted_slides[-1].sort_order + 1
    for s in sorted_slides:
        if s.id == after_slide_id:
            return s.sort_order + 1
    return len(sorted_slides)


def _neighbor_context(slides: list, after_slide_id: int | None) -> tuple[str, str, str]:
    sorted_slides = sorted(slides, key=lambda s: s.sort_order)
    idx = -1
    if after_slide_id is not None:
        for i, s in enumerate(sorted_slides):
            if s.id == after_slide_id:
                idx = i
                break
    prev_title = sorted_slides[idx].title if idx >= 0 else ""
    next_title = sorted_slides[idx + 1].title if 0 <= idx + 1 < len(sorted_slides) else ""
    style_summary = "；".join(s.title for s in sorted_slides[:8] if s.title)
    return prev_title, next_title, style_summary


def _deck_style_snapshot(slides: list) -> str:
    """从已有页面提取风格摘要：模板分布 + 内容语气采样。

    不做页码提示、不做位置标记——单页生成就是全量生成的简化版，
    只需让 LLM 知道已有页面用了什么模板、什么语气。
    """
    if not slides:
        return ""

    sorted_slides = sorted(slides, key=lambda s: s.sort_order)
    template_seq: list[str] = []
    content_samples: list[str] = []

    for s in sorted_slides:
        st = s.structured or {}
        ttype = st.get("template_type") or s.layout or ""
        template_seq.append(ttype)

        pts = st.get("points") or st.get("cards") or []
        if pts and isinstance(pts, list):
            for p in pts[:1]:
                txt = (p.get("text") or p.get("title") or "") if isinstance(p, dict) else str(p)
                if txt:
                    content_samples.append(txt[:50])
        if len(content_samples) >= 3:
            break

    from collections import Counter
    tc = Counter(template_seq)
    template_summary = "、".join(f"{t}({c}页)" for t, c in tc.most_common(6))

    parts = [f"已有模板分布：{template_summary}"]
    if content_samples:
        parts.append(f"内容语气参考：{'；'.join(content_samples[:3])}")

    return "；".join(parts)


async def shift_slide_sort_orders_from(
    db: AsyncSession,
    project_id: int,
    from_order: int,
) -> None:
    result = await db.execute(
        select(Slide).where(Slide.project_id == project_id, Slide.sort_order >= from_order)
    )
    for slide in result.scalars():
        slide.sort_order += 1


async def generate_single_slide_into_project(
    db: AsyncSession,
    user: User,
    project: Project,
    body: AiSlideGenerateRequest,
) -> Slide:
    tier = body.tier or user.tier or "free"
    try:
        await check_and_consume(db, user.id, tier)
    except QuotaExceeded as exc:
        raise QuotaLlmError(str(exc)) from exc

    replace_slide_id = body.replace_slide_id
    hint = TEMPLATE_HINT_INSTRUCTIONS.get(body.template_hint or "magic", TEMPLATE_HINT_INSTRUCTIONS["magic"])

    # 风格快照：从已有页面提取模板分布和内容语气，确保单页风格匹配
    style_snapshot = _deck_style_snapshot(project.slides)

    context_bits = [
        f"模板偏好：{hint}",
        f"演示整体标题：{project.title}",
    ]
    # 注入风格快照
    if style_snapshot:
        context_bits.append(style_snapshot)

    deck_body = AiDeckGenerateRequest(
        topic=body.prompt.strip(),
        page_count=1,
        language=body.language or "简体中文",
        text_density="精炼",
        extra_instructions="；".join(context_bits),
        channel=body.channel,
        tier=tier,
        model=body.model,
    )

    variables = {
        "page_count": 1,
        "topic": _build_topic(deck_body),
        "audience": "通用受众",
        "style": _build_style(deck_body),
        "language": deck_body.language or "简体中文",
        "text_density": deck_body.text_density or "精炼",
        "extra_instructions": deck_body.extra_instructions or "无",
        "content_mode": "free",
        "page_contents": [],
    }

    # 单页改写统一使用严格模板（与全量生成保持一致）
    messages = render_template("严格模板生成.yaml", variables)
    model_override = (body.model or "").strip() or None
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
        data = extract_json(raw)
        _, _, slides_raw = _normalize_deck_json(data, 1)
        if not slides_raw:
            raise LlmError("大模型未返回有效页面")
        slide_raw = slides_raw[0]
    except LlmError:
        raise
    except Exception as exc:
        raise LlmError(f"生成失败：{exc}") from exc

    duration_ms = int((time.perf_counter() - t0) * 1000)

    try:
        settings = json.loads(project.settings_json or "{}")
    except json.JSONDecodeError:
        settings = {}
    theme_id = str(settings.get("themeId") or "zjy-minimal").strip()
    if theme_id not in VALID_THEME_IDS:
        theme_id = "zjy-minimal"
    bg = THEME_DEFAULT_GRADIENTS.get(theme_id, THEME_DEFAULT_GRADIENTS["zjy-minimal"])

    slides_seed = _llm_slides_to_seed(slides_raw, bg)
    seed = slides_seed[0]
    structured = seed.get("structured") or {}

    if replace_slide_id is not None:
        existing = next((s for s in project.slides if s.id == replace_slide_id), None)
        if not existing:
            raise LlmError("要替换的页面不存在")
        new_order = existing.sort_order
    else:
        new_order = compute_insert_sort_order(list(project.slides), body.insert_after_slide_id)
        if body.insert_after_slide_id is not None:
            await shift_slide_sort_orders_from(db, project.id, new_order)

    slide = Slide(
        project_id=project.id,
        sort_order=new_order,
        layout=seed.get("layout", structured.get("template", "section"))[:32],
        title=seed.get("title", "")[:255],
        subtitle=seed.get("subtitle", "")[:512],
        bullets_json=json.dumps(seed.get("bullets", []), ensure_ascii=False),
        speaker_notes=str(seed.get("speakerNotes", ""))[:8000],
        animation=str(seed.get("animation", "fade"))[:32],
        canvas_json=json.dumps(seed.get("canvas_elements", []), ensure_ascii=False),
        chat_script_json=json.dumps(seed.get("chat_script") or {}, ensure_ascii=False),
        structured_json=json.dumps(structured, ensure_ascii=False),
    )
    db.add(slide)
    await db.flush()

    if replace_slide_id is not None:
        old_slide = await db.get(Slide, replace_slide_id)
        if old_slide and old_slide.project_id == project.id:
            await db.delete(old_slide)
            await db.flush()

    canvas_bg = seed.get("canvas_background")
    if canvas_bg:
        merged_bg = {**(settings.get("slideBackgrounds") or {}), str(slide.id): canvas_bg}
        settings["slideBackgrounds"] = merged_bg
        project.settings_json = json.dumps(settings, ensure_ascii=False)

    db.add(
        GenerationLog(
            project_id=project.id,
            template_id="single_slide",
            channel=channel,
            model=model,
            duration_ms=duration_ms,
            success=1,
            message=f"AI 单页生成成功 · {seed.get('title', '')[:40]}",
        )
    )
    await db.commit()
    await db.refresh(slide)
    await db.refresh(project)
    return slide

