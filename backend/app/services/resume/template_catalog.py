"""Resume visual + industry prompt template catalog."""
from __future__ import annotations

from typing import Any

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

_WRITING_RULES = (
    "工作经历分点使用「加粗概括：详细描述」格式；尽量量化成就；"
    "对齐目标岗位 JD 关键词；5 年以内工作经历优先控制在一页。"
)

RESUME_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "general",
        "industry_id": "general",
        "title": "通用求职",
        "description": "适合大多数社招岗位",
        "prompt_hint": "目标岗位：\n优化方向：突出项目成果与量化数据",
        "system_snippet": f"通用求职简历。{_WRITING_RULES} 技能侧重：沟通协作、项目管理、业务结果。",
    },
    {
        "id": "backend",
        "industry_id": "tech",
        "title": "后端工程师",
        "description": "编程语言、框架、数据库与分布式",
        "prompt_hint": "目标岗位：后端工程师\n优化方向：突出高并发、系统设计与性能优化数据",
        "system_snippet": "后端工程师。技能维度：编程语言 / 框架与中间件 / 数据库 / 分布式与高并发 / DevOps。",
    },
    {
        "id": "ai-pm",
        "industry_id": "product",
        "title": "AI 产品经理",
        "description": "LLM 能力、产品方法论与数据能力",
        "prompt_hint": "目标岗位：AI 产品经理\n优化方向：突出 LLM 落地、需求分析与数据结果",
        "system_snippet": "AI 产品经理。技能维度：AI/LLM 能力 / 产品方法论 / 数据能力 / 行业认知 / 工具协作。",
    },
    {
        "id": "product",
        "industry_id": "product",
        "title": "产品经理",
        "description": "STAR 法则与跨部门协作",
        "prompt_hint": "目标岗位：产品经理\n优化方向：STAR 法则描述需求落地与数据结果",
        "system_snippet": "产品经理。技能维度：需求分析 / 用户研究 / 数据驱动 / 跨部门协作 / 项目管理。",
    },
    {
        "id": "ops-growth",
        "industry_id": "ops",
        "title": "C 端运营",
        "description": "增长、内容与数据分析",
        "prompt_hint": "目标岗位：用户运营\n优化方向：突出增长实验、内容策划与转化数据",
        "system_snippet": "C 端运营。技能维度：用户增长 / 内容策划 / 数据分析 / 平台规则 / 工具栈。",
    },
    {
        "id": "design",
        "industry_id": "design",
        "title": "视觉设计师",
        "description": "设计能力与作品集",
        "prompt_hint": "目标岗位：视觉设计师\n优化方向：突出品牌、UI 项目与作品集链接",
        "system_snippet": "视觉设计师。技能维度：品牌/插画/动效 / Figma·Sketch / 设计方法论 / 作品集。",
    },
    {
        "id": "marketing",
        "industry_id": "marketing",
        "title": "市场营销",
        "description": "品牌、投放与数据归因",
        "prompt_hint": "目标岗位：市场营销\n优化方向：突出品牌战役、投放 ROI 与转化",
        "system_snippet": "市场营销。技能维度：品牌策略 / 内容营销 / 投放渠道 / 数据归因。",
    },
    {
        "id": "finance",
        "industry_id": "finance",
        "title": "财务分析师",
        "description": "建模、估值与 BI 工具",
        "prompt_hint": "目标岗位：财务分析\n优化方向：突出建模、审计与业务洞察",
        "system_snippet": "财务分析师。技能维度：财务专业 / 建模与估值 / Excel·SQL·BI / 行业理解。",
    },
    {
        "id": "hr",
        "industry_id": "hr",
        "title": "HRBP",
        "description": "招聘、组织发展与绩效",
        "prompt_hint": "目标岗位：HRBP\n优化方向：突出组织变革、招聘与人才发展",
        "system_snippet": "HRBP。技能维度：招聘/OD/绩效/薪酬 / 业务理解 / 数据敏感度。",
    },
    {
        "id": "sales",
        "industry_id": "sales",
        "title": "销售/BD",
        "description": "成单规模与客户资源",
        "prompt_hint": "目标岗位：销售/BD\n优化方向：突出成单金额、客户开发与续约率",
        "system_snippet": "销售/BD。技能维度：销售方法论 / 客户类型 / 最大成单规模 / 行业资源。",
    },
    {
        "id": "data-analyst",
        "industry_id": "data",
        "title": "数据分析师",
        "description": "SQL、Python 与可视化",
        "prompt_hint": "目标岗位：数据分析师\n优化方向：突出分析项目、指标体系建设",
        "system_snippet": "数据分析师。技能维度：SQL/Python / BI 工具 / 统计分析 / 业务理解 / 可视化。",
    },
    {
        "id": "campus",
        "industry_id": "campus",
        "title": "校招应届",
        "description": "实习与校园经历为主",
        "prompt_hint": "目标岗位：\n优化方向：突出实习、竞赛与学习能力",
        "system_snippet": f"校招应届。{_WRITING_RULES} 突出实习、项目、竞赛与学习能力。",
    },
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
        return _WRITING_RULES
    row = RESUME_TEMPLATE_BY_ID.get(prompt_template_id)
    if not row:
        return _WRITING_RULES
    return str(row.get("system_snippet") or _WRITING_RULES)
