"""H5 探索模板库服务。"""
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import H5Template

DEFAULT_CATALOG: list[dict[str, Any]] = [
    {
        "id": "fin-2024-mobile",
        "title": "2024 企业财报数据大屏",
        "description": "专业数据可视化，适合年度总结与经营分析汇报。",
        "category": "年度报告",
        "device": "mobile",
        "pages": 12,
        "premium": True,
        "cover_gradient": "from-blue-600 to-indigo-800",
        "default_viewport": "mobile-375",
    },
    {
        "id": "fin-2024-web",
        "title": "2024 企业财报数据大屏（网页版）",
        "description": "宽屏数据汇报，适合大屏展示与网页嵌入。",
        "category": "年度报告",
        "device": "web",
        "pages": 12,
        "premium": True,
        "cover_gradient": "from-blue-700 to-indigo-900",
        "default_viewport": "web-1920",
    },
    {
        "id": "tech-launch-mobile",
        "title": "极简科技产品发布",
        "description": "极简风格，突出产品核心卖点。",
        "category": "产品发布",
        "device": "mobile",
        "pages": 8,
        "premium": False,
        "cover_gradient": "from-slate-50 to-teal-100",
        "default_viewport": "mobile-375",
    },
    {
        "id": "tech-launch-web",
        "title": "极简科技产品发布（网页版）",
        "description": "1280 宽屏布局，适合官网与发布会投屏。",
        "category": "产品发布",
        "device": "web",
        "pages": 8,
        "premium": False,
        "cover_gradient": "from-slate-100 to-teal-200",
        "default_viewport": "web-1280",
    },
    {
        "id": "resume-creative-mobile",
        "title": "高端创意个人微简历",
        "description": "适合设计师与创意从业者，手机端浏览体验佳。",
        "category": "个人简历",
        "device": "mobile",
        "pages": 5,
        "premium": False,
        "cover_gradient": "from-rose-500 to-orange-400",
        "default_viewport": "mobile-390",
    },
    {
        "id": "resume-creative-web",
        "title": "高端创意个人微简历（网页版）",
        "description": "横向宽屏简历，适合作品集与招聘场景。",
        "category": "个人简历",
        "device": "web",
        "pages": 5,
        "premium": False,
        "cover_gradient": "from-rose-600 to-orange-500",
        "default_viewport": "web-1280",
    },
    {
        "id": "corp-intro-mobile",
        "title": "企业品牌介绍",
        "description": "展示企业文化、业务与团队。",
        "category": "企业介绍",
        "device": "mobile",
        "pages": 10,
        "premium": False,
        "cover_gradient": "from-emerald-600 to-teal-700",
        "default_viewport": "mobile-375",
    },
    {
        "id": "corp-intro-web",
        "title": "企业品牌介绍（网页版）",
        "description": "企业官网风格宽屏介绍，适合 B 端展示。",
        "category": "企业介绍",
        "device": "web",
        "pages": 10,
        "premium": False,
        "cover_gradient": "from-emerald-700 to-teal-800",
        "default_viewport": "web-1920",
    },
]

CATEGORIES = ["全部", "对话故事", "简约商务", "叙事公益", "年度报告", "产品发布", "个人简历", "企业介绍"]
DEVICES = [
    {"id": "全部", "label": "全部终端"},
    {"id": "mobile", "label": "移动端"},
    {"id": "web", "label": "网页版"},
]


class H5TemplateError(Exception):
    pass


def _to_dict(row: H5Template) -> dict[str, Any]:
    try:
        slides = json.loads(row.slides_json or "[]")
        if not isinstance(slides, list):
            slides = []
    except json.JSONDecodeError:
        slides = []
    try:
        settings = json.loads(getattr(row, "settings_json", None) or "{}")
        if not isinstance(settings, dict):
            settings = {}
    except json.JSONDecodeError:
        settings = {}
    featured = len(slides) > 0
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description,
        "category": row.category,
        "device": row.device,
        "pages": row.pages,
        "premium": bool(row.premium),
        "cover_gradient": row.cover_gradient,
        "default_viewport": row.default_viewport,
        "slides_json": slides,
        "settings_json": settings,
        "sort_order": row.sort_order,
        "enabled": bool(row.enabled),
        "featured": featured,
        "source": getattr(row, "source", None) or "file",
    }


def _enrich_from_file_template(data: dict[str, Any]) -> dict[str, Any]:
    """数据库 slides 为空时，用 data/h5_templates 下的 JSON 补全试看内容。"""
    if len(data.get("slides_json") or []) > 0:
        return data
    from app.services.template_loader import get_file_template_by_id

    file_data = get_file_template_by_id(data["id"])
    if not file_data:
        return data
    slides = file_data.get("slides_json") or []
    if not slides:
        return data
    enriched = {**data}
    enriched["slides_json"] = slides
    enriched["settings_json"] = file_data.get("settings_json") or data.get("settings_json") or {}
    enriched["featured"] = True
    if file_data.get("pages"):
        enriched["pages"] = int(file_data["pages"])
    return enriched


def _cover_slide_from_slides(slides: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not slides:
        return None
    first = slides[0]
    if not isinstance(first, dict):
        return None
    return {
        "id": "cover",
        "title": first.get("title", ""),
        "subtitle": first.get("subtitle", ""),
        "bullets": first.get("bullets") or [],
        "layout": first.get("layout", "cover"),
        "canvas_background": first.get("canvas_background"),
        "canvas_elements": first.get("canvas_elements") or [],
    }


def _public_template_item(data: dict[str, Any]) -> dict[str, Any]:
    slides = data.get("slides_json") or []
    item = {k: v for k, v in data.items() if k not in ("slides_json", "settings_json")}
    item["cover_slide"] = _cover_slide_from_slides(slides)
    return item


def _filter_items(items: list[dict], category: str, device: str, q: str) -> list[dict]:
    result = items
    if category and category != "全部":
        result = [t for t in result if t["category"] == category]
    if device and device != "全部":
        result = [t for t in result if t["device"] == device]
    if q.strip():
        kw = q.strip().lower()
        result = [
            t
            for t in result
            if kw in t["title"].lower()
            or kw in t["description"].lower()
            or kw in t["category"].lower()
            or ("移动" in kw and t["device"] == "mobile")
            or ("网页" in kw and t["device"] == "web")
            or ("手机" in kw and t["device"] == "mobile")
        ]
    return result


async def seed_default_templates(db: AsyncSession) -> None:
    result = await db.execute(select(H5Template).limit(1))
    if not result.scalar_one_or_none():
        for idx, item in enumerate(DEFAULT_CATALOG):
            db.add(
                H5Template(
                    id=item["id"],
                    title=item["title"],
                    description=item["description"],
                    category=item["category"],
                    device=item["device"],
                    pages=item["pages"],
                    premium=1 if item.get("premium") else 0,
                    cover_gradient=item.get("cover_gradient", ""),
                    default_viewport=item.get("default_viewport", "mobile-375"),
                    slides_json="[]",
                    settings_json="{}",
                    sort_order=idx,
                    enabled=1,
                )
            )
        await db.flush()
    await sync_flagship_templates(db)


async def sync_flagship_templates(db: AsyncSession) -> None:
    from app.services.template_loader import clear_file_template_cache, load_all_file_templates

    clear_file_template_cache()
    base_order = -100
    for offset, data in enumerate(load_all_file_templates()):
        tid = data["id"]
        slides = data.get("slides_json") or []
        settings = data.get("settings_json") or {}
        row = await db.get(H5Template, tid)
        payload = {
            "title": data["title"],
            "description": data.get("description", ""),
            "category": data.get("category", "对话故事"),
            "device": data.get("device", "mobile"),
            "pages": int(data.get("pages", len(slides) or 1)),
            "premium": 1 if data.get("premium") else 0,
            "cover_gradient": data.get("cover_gradient", "from-primary to-primary-container"),
            "default_viewport": data.get("default_viewport", "mobile-375"),
            "slides_json": json.dumps(slides, ensure_ascii=False),
            "settings_json": json.dumps(settings, ensure_ascii=False),
            "sort_order": base_order + offset,
            "enabled": 1,
        }
        if row:
            if getattr(row, "source", "file") == "admin":
                continue
            for key, val in payload.items():
                setattr(row, key, val)
            row.source = "file"
        else:
            db.add(H5Template(id=tid, source="file", **payload))
    await db.flush()


async def list_for_user(
    db: AsyncSession,
    category: str = "全部",
    device: str = "全部",
    q: str = "",
) -> list[dict]:
    result = await db.execute(
        select(H5Template).where(H5Template.enabled == 1).order_by(H5Template.sort_order, H5Template.id)
    )
    items = [_enrich_from_file_template(_to_dict(r)) for r in result.scalars().all()]
    public = [_public_template_item(t) for t in items]
    return _filter_items(public, category, device, q)


async def admin_list(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(H5Template).order_by(H5Template.sort_order, H5Template.id))
    return [_to_dict(r) for r in result.scalars().all()]


async def get_template(db: AsyncSession, template_id: str) -> dict | None:
    row = await db.get(H5Template, template_id)
    if row:
        return _enrich_from_file_template(_to_dict(row))
    from app.services.template_loader import get_file_template_by_id

    file_data = get_file_template_by_id(template_id)
    if not file_data:
        return None
    slides = file_data.get("slides_json") or []
    return {
        "id": file_data["id"],
        "title": file_data.get("title", template_id),
        "description": file_data.get("description", ""),
        "category": file_data.get("category", ""),
        "device": file_data.get("device", "mobile"),
        "pages": int(file_data.get("pages", len(slides) or 1)),
        "premium": bool(file_data.get("premium")),
        "cover_gradient": file_data.get("cover_gradient", ""),
        "default_viewport": file_data.get("default_viewport", "mobile-375"),
        "slides_json": slides,
        "settings_json": file_data.get("settings_json") or {},
        "sort_order": 0,
        "enabled": True,
        "featured": len(slides) > 0,
    }


async def create_template(db: AsyncSession, data: dict[str, Any]) -> dict:
    tid = data["id"].strip()
    exists = await db.get(H5Template, tid)
    if exists:
        raise H5TemplateError("模板 ID 已存在")
    slides_json = data.get("slides_json", [])
    page_count = int(data.get("pages", len(slides_json) or 1))
    row = H5Template(
        id=tid,
        title=data["title"],
        description=data.get("description", ""),
        category=data.get("category", ""),
        device=data.get("device", "mobile"),
        pages=page_count,
        premium=1 if data.get("premium") else 0,
        cover_gradient=data.get("cover_gradient", "from-primary to-primary-container"),
        default_viewport=data.get("default_viewport", "mobile-375"),
        slides_json=json.dumps(slides_json, ensure_ascii=False),
        settings_json=json.dumps(data.get("settings_json") or {}, ensure_ascii=False),
        sort_order=int(data.get("sort_order", 0)),
        enabled=1 if data.get("enabled", True) else 0,
        source="admin",
    )
    db.add(row)
    await db.flush()
    return _to_dict(row)


async def update_template(db: AsyncSession, template_id: str, data: dict[str, Any]) -> dict:
    row = await db.get(H5Template, template_id)
    if not row:
        raise H5TemplateError("模板不存在")
    for field in ("title", "description", "category", "device", "cover_gradient", "default_viewport"):
        if field in data and data[field] is not None:
            setattr(row, field, data[field])
    if "pages" in data and data["pages"] is not None:
        row.pages = int(data["pages"])
    if "premium" in data and data["premium"] is not None:
        row.premium = 1 if data["premium"] else 0
    if "enabled" in data and data["enabled"] is not None:
        row.enabled = 1 if data["enabled"] else 0
    if "sort_order" in data and data["sort_order"] is not None:
        row.sort_order = int(data["sort_order"])
    if "settings_json" in data and data["settings_json"] is not None:
        row.settings_json = json.dumps(data["settings_json"], ensure_ascii=False)
    if "slides_json" in data and data["slides_json"] is not None:
        row.slides_json = json.dumps(data["slides_json"], ensure_ascii=False)
        if "pages" not in data or data["pages"] is None:
            row.pages = len(data["slides_json"]) or 1
    row.source = "admin"
    await db.flush()
    return _to_dict(row)


async def delete_template(db: AsyncSession, template_id: str) -> None:
    row = await db.get(H5Template, template_id)
    if not row:
        raise H5TemplateError("模板不存在")
    await db.delete(row)
    await db.flush()
