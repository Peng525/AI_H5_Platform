"""
多步LLM编排器 — 模仿PPT-Master工作流 (Strategist→Executor→Designer)

在现有FastAPI内实现三阶段编排，不依赖外部Agent工具：
  Phase 1: Strategist — 规划页面结构
  Phase 2: Executor  — 逐页生成SVG（支持串行/批量对比）
  Phase 3: Designer  — 统一配色和视觉风格
  Phase 4: SVG → slides_seed（与现有seed_project_slides兼容）
"""
from __future__ import annotations

import base64
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog, Project, Slide, User
from app.schemas import AiDeckGenerateRequest
from app.services.deck_generation_service import (
    BACKGROUND_COLORS,
    THEME_DEFAULT_GRADIENTS,
    VALID_THEME_IDS,
    VIEWPORT_MAP,
    VIEWPORT_SIZES,
    TEXT_DENSITY_STYLE,
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

DEFAULT_CANVAS_W = 1280
DEFAULT_CANVAS_H = 720

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


def _resolve_canvas(body: AiDeckGenerateRequest) -> tuple[int, int]:
    """根据用户选择的 viewport_mode 解析画布尺寸，默认 1280×720（16:9）。"""
    viewport_id = VIEWPORT_MAP.get(body.viewport_mode, VIEWPORT_MAP["auto"])
    w, h = VIEWPORT_SIZES.get(viewport_id, VIEWPORT_SIZES.get("web-1280", (DEFAULT_CANVAS_W, DEFAULT_CANVAS_H)))
    return w, h

# ── 数据结构 ──

@dataclass
class OrchestratorProgress:
    """编排进度（供API轮询）"""
    stage: str = "queued"  # queued | strategist | executing | designing | importing | completed | failed
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


# ── Phase 2: Executor ──

def _build_executor_vars(page: dict, deck_title: str, total_pages: int, style: str, canvas_w: int = DEFAULT_CANVAS_W, canvas_h: int = DEFAULT_CANVAS_H, theme_colors: dict | None = None) -> dict:
    key_points = page.get("key_points") or []
    if isinstance(key_points, str):
        key_points = [key_points]
    tc = theme_colors or _THEME_COLORS["zjy-minimal"]
    return {
        "page_num": page.get("page_num", 1),
        "total_pages": total_pages,
        "template_type": page.get("template_type", "points"),
        "page_title": page.get("title", ""),
        "subtitle": page.get("subtitle", ""),
        "author": page.get("author", ""),
        "date": page.get("date", ""),
        "key_points": key_points[:6],
        "image_topic": page.get("image_topic", ""),
        "deck_title": deck_title,
        "style": style,
        "canvas_w": canvas_w,
        "canvas_h": canvas_h,
        # 主题色（来自用户选择的PPT模板）
        "primary": tc["primary"],
        "text_color": tc["text"],
        "text_muted": tc["text_muted"],
        "bg_color": tc["bg"],
        "accent2": tc["accent2"],
    }


_SVG_RE = re.compile(r"```(?:svg|xml)?\s*\n?(.*?)```", re.DOTALL | re.IGNORECASE)
_SVG_TAG_RE = re.compile(r"<svg[\s\S]*?</svg>", re.IGNORECASE)


def _extract_svg(raw: str) -> str:
    """从LLM输出中提取SVG代码"""
    # 优先提取代码块
    m = _SVG_RE.search(raw)
    if m:
        return m.group(1).strip()
    # 否则提取 <svg>...</svg> 标签
    m = _SVG_TAG_RE.search(raw)
    if m:
        return m.group(0).strip()
    # 兜底：返回去markdown的原始内容
    cleaned = raw.replace("```svg", "").replace("```xml", "").replace("```", "").strip()
    if cleaned.startswith("<svg"):
        return cleaned
    raise LlmError("Executor 未返回有效的 SVG 代码")


async def _executor_phase_serial(
    pages: list[dict],
    deck_title: str,
    style: str,
    body: AiDeckGenerateRequest,
    canvas_w: int = DEFAULT_CANVAS_W,
    canvas_h: int = DEFAULT_CANVAS_H,
    theme_colors: dict | None = None,
    progress: OrchestratorProgress | None = None,
) -> list[dict]:
    """逐页串行生成SVG（方案A：每页一次LLM调用）"""
    svgs = []
    per_page_ms = []
    tier = body.tier or "free"
    model_override = (body.model or "").strip() or None

    for page in pages:
        page_num = page.get("page_num", 1)
        # 每页开始前更新进度
        if progress:
            progress.current_page = page_num
            progress.progress_pct = int(15 + (page_num / len(pages)) * 65)
            progress.message = f"正在生成第 {page_num} / {len(pages)} 页…"

        vars_ = _build_executor_vars(page, deck_title, len(pages), style, canvas_w, canvas_h, theme_colors)
        messages = render_template("orchestrate_executor.yaml", vars_)

        t0 = time.perf_counter()
        raw, channel, model, usage = await chat_completion_with_usage(
            messages,
            channel=body.channel,
            tier=tier,
            model=model_override,
        )
        svg_code = _extract_svg(raw)
        duration_ms = int((time.perf_counter() - t0) * 1000)
        per_page_ms.append(duration_ms)

        svgs.append({
            "page_num": page_num,
            "template_type": page.get("template_type", "points"),
            "svg": svg_code,
            "generation_time_ms": duration_ms,
            "channel": channel,
            "model": model,
            "tokens": usage,
        })
        logger.info(
            "orchestrator executor page=%s/%s duration_ms=%s svg_len=%s",
            page_num, len(pages), duration_ms, len(svg_code),
        )

    return {"svgs": svgs, "mode": "serial", "per_page_ms": per_page_ms}


async def _executor_phase_batch(
    pages: list[dict],
    deck_title: str,
    style: str,
    body: AiDeckGenerateRequest,
) -> list[dict]:
    """一次调用生成所有页的SVG（方案B：对比用）"""
    # 构建批量Prompt：要求LLM一次性返回所有页的SVG
    all_pages_text = ""
    for p in pages:
        all_pages_text += f"\n--- 第{p.get('page_num',1)}页 ({p.get('template_type','points')}) ---\n"
        all_pages_text += f"标题：{p.get('title','')}\n"
        kps = p.get("key_points") or []
        all_pages_text += f"要点：{'；'.join(kps[:5])}\n"

    vars_ = {
        "page_num": 1,
        "total_pages": len(pages),
        "template_type": "batch",
        "page_title": deck_title,
        "subtitle": "",
        "author": "",
        "date": "",
        "key_points": [],
        "image_topic": "",
        "deck_title": deck_title,
        "style": style,
        "all_pages_summary": all_pages_text,
    }
    # 复用 executor 模板，但通过 extra hint 告知批量模式
    messages = render_template("orchestrate_executor.yaml", vars_)
    # 在 system 消息末尾追加批量模式说明
    messages[0]["content"] += (
        f"\n\n【批量模式】你需要一次性生成全部 {len(pages)} 页的SVG。"
        "每页SVG用 ---PAGE_N--- 分隔，其中N为页码。\n"
        + all_pages_text
    )

    t0 = time.perf_counter()
    raw, channel, model = await chat_completion(
        messages,
        channel=body.channel,
        tier=body.tier or "free",
        model=(body.model or "").strip() or None,
    )
    duration_ms = int((time.perf_counter() - t0) * 1000)

    # 按分隔符拆分
    parts = re.split(r"---PAGE_\d+---", raw)
    svgs = []
    per_page_ms = [duration_ms // max(len(pages), 1)] * len(pages)

    for i, page in enumerate(pages):
        svg_code = ""
        if i < len(parts):
            svg_code = _extract_svg(parts[i])
        if not svg_code and i > 0 and i - 1 < len(parts):
            svg_code = _extract_svg(parts[i - 1])  # fallback
        svgs.append({
            "page_num": page.get("page_num", i + 1),
            "template_type": page.get("template_type", "points"),
            "svg": svg_code,
            "generation_time_ms": per_page_ms[i],
            "channel": channel,
            "model": model,
        })

    return {"svgs": svgs, "mode": "batch", "per_page_ms": per_page_ms, "total_ms": duration_ms}


async def _executor_phase(
    pages: list[dict],
    deck_title: str,
    style: str,
    body: AiDeckGenerateRequest,
    progress: OrchestratorProgress | None = None,
    executor_mode: str = "serial",
    canvas_w: int = DEFAULT_CANVAS_W,
    canvas_h: int = DEFAULT_CANVAS_H,
    theme_colors: dict | None = None,
) -> dict:
    """Executor入口，支持串行/批量两种模式"""
    progress and setattr(progress, "total_pages", len(pages))

    if executor_mode == "batch":
        result = await _executor_phase_batch(pages, deck_title, style, body)
    else:
        result = await _executor_phase_serial(pages, deck_title, style, body, canvas_w, canvas_h, theme_colors, progress)

    return result


# ── Phase 3: Designer ──

def _svg_style_summary(svg_code: str) -> str:
    """从 SVG 中提取风格摘要（只取配色和排版特征，不传完整 SVG）。
    避免把 5000+ 字符的 SVG 代码塞进 LLM 上下文。"""
    import re as _re
    summary_parts = []

    # 提取 fill/stroke 颜色
    fills = _re.findall(r'\bfill\s*=\s*"([^"]*)"', svg_code)
    strokes = _re.findall(r'\bstroke\s*=\s*"([^"]*)"', svg_code)
    colors = set(f for f in fills + strokes if f.startswith("#") and len(f) == 7)
    if colors:
        summary_parts.append(f"配色: {', '.join(sorted(colors)[:8])}")

    # 提取字号范围
    font_sizes = _re.findall(r'font-size\s*=\s*"(\d+)"', svg_code)
    if font_sizes:
        sizes = sorted(set(int(s) for s in font_sizes))
        summary_parts.append(f"字号范围: {sizes[0]}-{sizes[-1]}px (共{len(sizes)}种)")

    # 提取圆角
    rx_vals = _re.findall(r'\brx\s*=\s*"(\d+)"', svg_code)
    if rx_vals:
        summary_parts.append(f"圆角: rx={max(set(rx_vals), key=rx_vals.count)}")

    # 提取文本内容前 80 字
    texts = _re.findall(r'<text[^>]*>(.*?)</text>', svg_code)
    text_content = " ".join(t.strip() for t in texts[:4] if t.strip())
    if text_content:
        summary_parts.append(f"内容摘要: {text_content[:80]}")

    return "；".join(summary_parts) if summary_parts else "(无风格信息)"


async def _designer_phase(
    svgs: list[dict],
    body: AiDeckGenerateRequest,
) -> dict:
    """提取统一配色方案（只传 SVG 风格摘要，不传完整 SVG）。"""
    slides_summaries = [
        {
            "page_num": s["page_num"],
            "template_type": s.get("template_type", "points"),
            "summary": _svg_style_summary(s["svg"]),
        }
        for s in svgs
    ]
    vars_ = {
        "slide_count": len(slides_summaries),
        "slides": slides_summaries,
    }
    messages = render_template("orchestrate_designer.yaml", vars_)
    t0 = time.perf_counter()
    raw, channel, model, usage = await chat_completion_with_usage(
        messages,
        channel=body.channel,
        tier=body.tier or "free",
        model=(body.model or "").strip() or None,
    )
    data = extract_json(raw)

    palette = data.get("palette") or {}
    style_notes = str(data.get("style_notes") or "").strip()

    duration_ms = int((time.perf_counter() - t0) * 1000)
    result = {
        "palette": palette,
        "style_notes": style_notes,
        "svgs": svgs,  # 原始 SVG 不变，只附加 palette
        "meta": {
            "duration_ms": duration_ms,
            "channel": channel,
            "model": model,
            "tokens": usage,
        },
    }
    logger.info("orchestrator designer done duration_ms=%s tokens=%s",
                duration_ms, usage.get("total_tokens", 0))
    return result


# ── Phase 4: SVG → slides_seed ──

def _svg_to_data_url(svg_code: str) -> str:
    """SVG代码 → Base64 Data URL"""
    encoded = base64.b64encode(svg_code.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _extract_text_elements(svg_code: str) -> list[dict]:
    """从SVG中提取<text>元素，返回canvas_elements text叠加层"""
    text_pattern = re.compile(
        r'<text\s[^>]*?(?:>|\s+fill="([^"]*)"[^>]*>)\s*(.*?)\s*</text>',
        re.DOTALL | re.IGNORECASE,
    )
    # 更稳健的解析：找所有 <text> 标签
    text_tag = re.compile(r'<text\b([^>]*)>(.*?)</text>', re.DOTALL | re.IGNORECASE)
    x_pattern = re.compile(r'\bx\s*=\s*"([^"]*)"')
    y_pattern = re.compile(r'\by\s*=\s*"([^"]*)"')
    font_size_pattern = re.compile(r'font-size\s*=\s*"([^"]*)"')
    fill_pattern = re.compile(r'\bfill\s*=\s*"([^"]*)"')
    font_weight_pattern = re.compile(r'font-weight\s*=\s*"([^"]*)"')
    text_anchor_pattern = re.compile(r'text-anchor\s*=\s*"([^"]*)"')

    elements = []
    for i, m in enumerate(text_tag.finditer(svg_code)):
        attrs = m.group(1)
        content = m.group(2).strip()

        # 跳过空白/纯数字页码
        if not content or content in {"|", "·", "•"}:
            continue

        # 解析属性
        x_str = x_pattern.search(attrs)
        y_str = y_pattern.search(attrs)
        x = float(x_str.group(1)) if x_str else 80.0
        y = float(y_str.group(1)) if y_str else 60.0

        font_size_str = font_size_pattern.search(attrs)
        font_size = float(font_size_str.group(1)) if font_size_str else 18.0

        fill = fill_pattern.search(attrs)
        color = fill.group(1) if fill else "#1f2937"

        fw = font_weight_pattern.search(attrs)
        fontWeight = fw.group(1) if fw else "normal"

        ta = text_anchor_pattern.search(attrs)
        text_align = "left"
        if ta:
            anchor = ta.group(1)
            if anchor == "middle":
                text_align = "center"
            elif anchor == "end":
                text_align = "right"

        # 跳过纯装饰的微小文字
        if font_size < 8:
            continue

        # 估算 text 元素宽高
        est_width = len(content) * font_size * 0.6
        est_height = font_size * 1.5

        elements.append({
            "id": f"orch_text_{i}",
            "type": "text",
            "x": x,
            "y": y - font_size * 0.2,  # 微调让文字对齐SVG baseline
            "width": est_width,
            "height": est_height,
            "zIndex": 100 + i,  # 在背景图之上
            "content": content,
            "style": {
                "background": "transparent",
                "color": color,
                "fontSize": font_size,
                "fontWeight": fontWeight,
                "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif",
                "textAlign": text_align,
                "lineHeight": 1.3,
            },
        })

    return elements


def _svg_slides_to_seed(
    designer_result: dict,
    pages_plan: list[dict],
    bg: str,
    deck_title: str = "",
    canvas_w: int = DEFAULT_CANVAS_W,
    canvas_h: int = DEFAULT_CANVAS_H,
) -> list[dict]:
    """将 Designer 输出转为 slides_seed（兼容现有 seed_project_slides）"""
    unified_svgs = designer_result.get("svgs") or []
    slides_seed = []

    for i, svg_item in enumerate(unified_svgs):
        svg_code = svg_item.get("svg", "")
        page_num = svg_item.get("page_num", i + 1)

        # 找对应规划
        plan = next((p for p in pages_plan if p.get("page_num") == page_num), None) or {}
        template_type = plan.get("template_type") or "points"
        page_title = plan.get("title") or svg_item.get("title") or f"第 {page_num} 页"

        # 策略A: SVG作为背景图 + 提取文字为叠加层
        data_url = _svg_to_data_url(svg_code) if svg_code else ""
        text_overlays = _extract_text_elements(svg_code) if svg_code else []

        # 背景图元素
        canvas_elements = []
        if data_url:
            canvas_elements.append({
                "id": f"orch_bg_{page_num}",
                "type": "image",
                "x": 0,
                "y": 0,
                "width": canvas_w,
                "height": canvas_h,
                "zIndex": 1,
                "content": data_url,
                "style": {"background": "transparent", "objectFit": "fill"},
            })
        # 文字叠加层
        canvas_elements.extend(text_overlays)

        # 不设置 structured — canvas_elements 已有完整渲染数据，
        # 否则前端 ensureSlideCompiled 会检测到 structured.template_type
        # 并重新编译覆盖掉编排器生成的 SVG 背景 + 文字叠加层

        slides_seed.append({
            "layout": template_type[:32],
            "title": page_title,
            "subtitle": plan.get("subtitle", ""),
            "bullets": [],
            "canvas_elements": canvas_elements,  # SVG背景+文字叠加，不设 structured 避免前端编译器覆盖
            "structured": {},
        })

    return slides_seed


# ── 主编排入口 ──

async def orchestrate_deck_generation(
    db: AsyncSession,
    user: User,
    body: AiDeckGenerateRequest,
    *,
    job_id: str = "",
    executor_mode: str = "serial",
) -> Project:
    """
    多步编排生成演示文稿。

    参数:
        executor_mode: "serial"（逐页串行，质量更高）或 "batch"（一次全量，对比用）
    """
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
        # ── 解析主题色和画布尺寸 ──
        theme_colors = _resolve_theme_colors(body)
        canvas_w, canvas_h = _resolve_canvas(body)

        # ── Phase 1: Strategist ──
        logger.info("orchestrator phase1 strategist start theme=%s canvas=%sx%s",
                    body.theme_id or "zjy-minimal", canvas_w, canvas_h)
        strategist_result = await _strategist_phase(body, variables, theme_colors)
        phases_meta["strategist"] = strategist_result.get("meta", {})
        pages_plan = strategist_result["pages"]
        deck_title = strategist_result["title"]
        if progress:
            progress.stage = "executing"
            progress.phase = "生成中"
            progress.progress_pct = 15
            progress.message = f"规划完成，共 {len(pages_plan)} 页，正在逐页生成…"

        # ── Phase 2: Executor ──
        logger.info("orchestrator phase2 executor start mode=%s canvas=%sx%s", executor_mode, canvas_w, canvas_h)
        executor_result = await _executor_phase(
            pages_plan, deck_title, variables["style"], body,
            progress=progress, executor_mode=executor_mode,
            canvas_w=canvas_w, canvas_h=canvas_h, theme_colors=theme_colors,
        )
        phases_meta["executor"] = {
            "mode": executor_result.get("mode", executor_mode),
            "per_page_ms": executor_result.get("per_page_ms", []),
            "total_ms": executor_result.get("total_ms", 0),
            "svg_count": len(executor_result.get("svgs", [])),
        }
        if progress:
            progress.stage = "designing"
            progress.phase = "最终校验"
            progress.progress_pct = 75
            progress.message = "页面生成完成，正在统一配色与视觉风格…"

        # ── Phase 3: Designer ──
        logger.info("orchestrator phase3 designer start")
        designer_result = await _designer_phase(executor_result["svgs"], body)
        phases_meta["designer"] = designer_result.get("meta", {})
        if progress:
            progress.stage = "importing"
            progress.phase = "导入中"
            progress.progress_pct = 90
            progress.message = "校验完成，正在保存到项目…"

        # ── Phase 4: 转换为 slides_seed 并入库 ──
        preset = (body.background_preset or "").strip()
        theme_id = (body.theme_id or "zjy-minimal").strip()
        if theme_id not in VALID_THEME_IDS:
            theme_id = "zjy-minimal"
        if preset and preset in BACKGROUND_COLORS:
            bg = BACKGROUND_COLORS[preset]
        else:
            bg = THEME_DEFAULT_GRADIENTS.get(theme_id, THEME_DEFAULT_GRADIENTS["zjy-minimal"])

        viewport_id = VIEWPORT_MAP.get(body.viewport_mode, VIEWPORT_MAP["auto"])
        slides_seed = _svg_slides_to_seed(designer_result, pages_plan, bg, deck_title, canvas_w, canvas_h)
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

        # ── 聚合 token 消耗 ──
        st_tokens = phases_meta.get("strategist", {}).get("tokens", {})
        ex_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        for svg_item in executor_result.get("svgs", []):
            t = svg_item.get("tokens", {})
            for k in ex_tokens:
                ex_tokens[k] += t.get(k, 0)
        de_tokens = phases_meta.get("designer", {}).get("tokens", {})
        total_prompt = st_tokens.get("prompt_tokens", 0) + ex_tokens["prompt_tokens"] + de_tokens.get("prompt_tokens", 0)
        total_completion = st_tokens.get("completion_tokens", 0) + ex_tokens["completion_tokens"] + de_tokens.get("completion_tokens", 0)

        log_msg = f"编排生成成功 · {len(slides_seed)} 页 · executor={executor_mode}"
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
            "orchestrator complete project=%s slides=%s total_ms=%s executor_mode=%s",
            pid, len(slides_seed), t_total_ms, executor_mode,
        )
        return await reload_project(db, project.id)

    except Exception as exc:
        logger.error("orchestrator failed: %s", exc)
        if progress:
            progress.stage = "failed"
            progress.error = str(exc)
        raise
