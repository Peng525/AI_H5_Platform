"""AI 生图提示词模板服务。"""
import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ImagePromptTemplate

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
DEFAULT_FIELD_LABELS = ["主体", "环境", "光线", "风格"]

BUILTIN_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "cat-window-rain",
        "title": "橘猫窗台 · 雨天",
        "description": "温馨室内与雨景街景",
        "fields": [
            {"label": "主体", "value": "一只橘色的短毛猫，坐在木质窗台上"},
            {"label": "环境", "value": "窗外是下雨的街道"},
            {"label": "光线", "value": "柔和的自然光从侧面照入"},
            {"label": "风格", "value": "水彩插画风格，细腻笔触"},
        ],
        "sort_order": 10,
    },
    {
        "id": "business-data-screen",
        "title": "企业数据大屏",
        "description": "科技感汇报封面",
        "fields": [
            {"label": "主体", "value": "2024 企业财报数据可视化大屏标题区"},
            {"label": "环境", "value": "深色科技背景，隐约可见图表与数据流光"},
            {"label": "光线", "value": "屏幕自发光，蓝紫色霓虹点缀"},
            {"label": "风格", "value": "3D 质感，商务专业，简洁大气"},
        ],
        "sort_order": 20,
    },
    {
        "id": "fork-road-choice",
        "title": "路口分岔",
        "description": "决策类 H5 配图",
        "fields": [
            {"label": "主体", "value": "站在路口中央的人物剪影，面前左右两条分岔路"},
            {"label": "环境", "value": "开阔城市道路，远处城市天际线"},
            {"label": "光线", "value": "黄昏暖色侧光，路面有轻微反光"},
            {"label": "风格", "value": "扁平插画，留白充足，适合叠加标题"},
        ],
        "sort_order": 30,
    },
]


class ImagePromptTemplateError(Exception):
    pass


def _parse_fields(raw: str) -> list[dict[str, str]]:
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise ImagePromptTemplateError("fields JSON 格式无效") from exc
    if not isinstance(data, list) or not data:
        raise ImagePromptTemplateError("至少填写一项提示词要素")
    out: list[dict[str, str]] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ImagePromptTemplateError(f"fields[{idx}] 必须是对象")
        label = str(item.get("label") or "").strip()
        value = str(item.get("value") or "").strip()
        if not label or not value:
            raise ImagePromptTemplateError(f"fields[{idx}] 的 label 与 value 不能为空")
        out.append({"label": label, "value": value})
    return out


def _to_dict(row: ImagePromptTemplate) -> dict[str, Any]:
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description or "",
        "fields": _parse_fields(row.fields_json),
        "sort_order": row.sort_order,
        "enabled": bool(row.enabled),
        "source": row.source or "admin",
    }


def _public_item(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": data["id"],
        "title": data["title"],
        "description": data.get("description", ""),
        "fields": data["fields"],
    }


async def list_for_editor(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(ImagePromptTemplate)
        .where(ImagePromptTemplate.enabled == 1)
        .order_by(ImagePromptTemplate.sort_order, ImagePromptTemplate.id)
    )
    return [_public_item(_to_dict(r)) for r in result.scalars().all()]


async def admin_list(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(ImagePromptTemplate).order_by(ImagePromptTemplate.sort_order, ImagePromptTemplate.id)
    )
    return [_to_dict(r) for r in result.scalars().all()]


async def get_template(db: AsyncSession, template_id: str) -> dict | None:
    row = await db.get(ImagePromptTemplate, template_id)
    return _to_dict(row) if row else None


async def create_template(db: AsyncSession, data: dict[str, Any]) -> dict:
    tid = data["id"].strip()
    if not ID_PATTERN.match(tid):
        raise ImagePromptTemplateError("模板 ID 仅支持小写字母、数字与连字符，且以字母或数字开头")
    if await db.get(ImagePromptTemplate, tid):
        raise ImagePromptTemplateError("模板 ID 已存在")
    title = (data.get("title") or "").strip()
    if not title:
        raise ImagePromptTemplateError("标题不能为空")
    fields = data.get("fields") or []
    _parse_fields(json.dumps(fields, ensure_ascii=False))
    row = ImagePromptTemplate(
        id=tid,
        title=title,
        description=(data.get("description") or "").strip(),
        fields_json=json.dumps(fields, ensure_ascii=False),
        sort_order=int(data.get("sort_order") or 100),
        enabled=1 if data.get("enabled", True) else 0,
        source="admin",
    )
    db.add(row)
    await db.flush()
    return _to_dict(row)


async def update_template(db: AsyncSession, template_id: str, data: dict[str, Any]) -> dict:
    row = await db.get(ImagePromptTemplate, template_id)
    if not row:
        raise ImagePromptTemplateError("模板不存在")
    if data.get("title") is not None:
        title = str(data["title"]).strip()
        if not title:
            raise ImagePromptTemplateError("标题不能为空")
        row.title = title
    if data.get("description") is not None:
        row.description = str(data["description"]).strip()
    if data.get("fields") is not None:
        fields = _parse_fields(json.dumps(data["fields"], ensure_ascii=False))
        row.fields_json = json.dumps(fields, ensure_ascii=False)
    if data.get("sort_order") is not None:
        row.sort_order = int(data["sort_order"])
    if data.get("enabled") is not None:
        row.enabled = 1 if data["enabled"] else 0
    await db.flush()
    return _to_dict(row)


async def delete_template(db: AsyncSession, template_id: str) -> None:
    row = await db.get(ImagePromptTemplate, template_id)
    if not row:
        raise ImagePromptTemplateError("模板不存在")
    if row.source == "builtin":
        raise ImagePromptTemplateError("内置模板不可删除")
    await db.delete(row)


async def seed_builtin_templates(db: AsyncSession) -> None:
    result = await db.execute(select(ImagePromptTemplate).limit(1))
    if result.scalar_one_or_none():
        return
    for item in BUILTIN_TEMPLATES:
        db.add(
            ImagePromptTemplate(
                id=item["id"],
                title=item["title"],
                description=item.get("description", ""),
                fields_json=json.dumps(item["fields"], ensure_ascii=False),
                sort_order=item.get("sort_order", 100),
                enabled=1,
                source="builtin",
            )
        )
