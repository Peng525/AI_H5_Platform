"""Resume visual + industry prompt template catalog."""
from __future__ import annotations

from typing import Any

from app.services.resume.industry_prompts import (
    GLOBAL_WRITING_RULES,
    build_prompt_full,
    build_system_snippet,
    prompt_fields,
)

# Industry chips (Polebrief-style primary filter)
INDUSTRIES: list[dict[str, str]] = [
    {"id": "all", "label": "全部"},
    {"id": "general", "label": "通用"},
    {"id": "tech", "label": "计算机/AI"},
    {"id": "product", "label": "产品"},
    {"id": "ops", "label": "运营"},
    {"id": "design", "label": "设计"},
    {"id": "marketing", "label": "市场"},
    {"id": "finance", "label": "财务"},
    {"id": "hr", "label": "人力"},
    {"id": "sales", "label": "销售"},
    {"id": "data", "label": "数据"},
    {"id": "campus", "label": "校招"},
]

def _resume_row(
    id: str,
    industry_id: str,
    title: str,
    description: str,
) -> dict[str, Any]:
    return {
        "id": id,
        "industry_id": industry_id,
        "title": title,
        "description": description,
        "prompt_hint": build_prompt_full(id, title),
        "prompt_full": build_prompt_full(id, title),
        "fields": prompt_fields(id),
        "system_snippet": build_system_snippet(id),
    }


RESUME_TEMPLATES: list[dict[str, Any]] = [
    _resume_row("general", "general", "通用求职", "适合大多数社招岗位"),
    _resume_row("backend", "tech", "后端工程师", "编程语言、框架、数据库与分布式"),
    _resume_row("ai-pm", "product", "AI 产品经理", "LLM 能力、产品方法论与数据能力"),
    _resume_row("product", "product", "产品经理", "STAR 法则与跨部门协作"),
    _resume_row("ops-growth", "ops", "C 端运营", "增长、内容与数据分析"),
    _resume_row("design", "design", "视觉设计师", "设计能力与作品集"),
    _resume_row("marketing", "marketing", "市场营销", "品牌、投放与数据归因"),
    _resume_row("finance", "finance", "财务分析师", "建模、估值与 BI 工具"),
    _resume_row("hr", "hr", "HRBP", "招聘、组织发展与绩效"),
    _resume_row("sales", "sales", "销售/BD", "成单规模与客户资源"),
    _resume_row("data-analyst", "data", "数据分析师", "SQL、Python 与可视化"),
    _resume_row("campus", "campus", "校招应届", "实习与校园经历为主"),
]

VISUAL_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "template1",
        "title": "经典双栏",
        "description": "双栏布局，信息密度较高",
        "preview_url": "/resume-templates/template1.png",
        "layout": "two-column",
        "industry_tags": ["general", "tech", "finance", "campus"],
    },
    {
        "id": "template2",
        "title": "简易一页",
        "description": "结构轻量，适合一页纸",
        "preview_url": "/resume-templates/template2.png",
        "layout": "single",
        "industry_tags": ["general", "campus"],
    },
    {
        "id": "template3",
        "title": "多页分区",
        "description": "分区展示，层次清晰",
        "preview_url": "/resume-templates/template3.png",
        "layout": "multi",
        "industry_tags": ["general", "product", "hr"],
    },
    {
        "id": "template4",
        "title": "现代简洁",
        "description": "留白充足，默认推荐",
        "preview_url": "/resume-templates/template4.png",
        "layout": "modern",
        "industry_tags": ["general", "product", "design", "data"],
    },
    {
        "id": "template5",
        "title": "商务侧栏",
        "description": "侧栏布局，更正式",
        "preview_url": "/resume-templates/template5.png",
        "layout": "sidebar",
        "industry_tags": ["finance", "sales", "hr", "marketing"],
    },
    {
        "id": "template6",
        "title": "杂志感",
        "description": "大标题网格，适合创意岗",
        "preview_url": "/resume-templates/template6.png",
        "layout": "magazine",
        "industry_tags": ["design", "marketing", "ops"],
    },
    {
        "id": "template7",
        "title": "技术极客",
        "description": "开发者档案风格",
        "preview_url": "/resume-templates/template7.png",
        "layout": "tech",
        "industry_tags": ["tech", "data"],
    },
]

# Legacy alias
TEMPLATE_ALIASES = {"classic-blue": "template1"}

RESUME_TEMPLATE_BY_ID = {t["id"]: t for t in RESUME_TEMPLATES}
ALLOWED_VISUAL_TEMPLATE_IDS = {t["id"] for t in VISUAL_TEMPLATES} | set(TEMPLATE_ALIASES.keys())


def normalize_template_id(template_id: str | None) -> str | None:
    if not template_id:
        return None
    tid = template_id.strip()
    return TEMPLATE_ALIASES.get(tid, tid)


def filter_resume_templates(industry: str | None = None) -> list[dict[str, Any]]:
    if not industry or industry == "all":
        return list(RESUME_TEMPLATES)
    return [t for t in RESUME_TEMPLATES if t.get("industry_id") == industry]


def filter_visual_templates(industry: str | None = None) -> list[dict[str, Any]]:
    if not industry or industry == "all":
        return list(VISUAL_TEMPLATES)
    return [t for t in VISUAL_TEMPLATES if industry in (t.get("industry_tags") or [])]


def get_industry_snippet(prompt_template_id: str | None) -> str:
    if not prompt_template_id:
        return GLOBAL_WRITING_RULES
    row = RESUME_TEMPLATE_BY_ID.get(prompt_template_id)
    if not row:
        return GLOBAL_WRITING_RULES
    return str(row.get("system_snippet") or GLOBAL_WRITING_RULES)
