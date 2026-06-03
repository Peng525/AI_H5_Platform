"""AI 演示文稿提示词模板服务。"""
import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DeckPromptTemplate

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
DEFAULT_FIELD_LABELS = ["主题", "受众", "结构", "风格"]

BUILTIN_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "coral-reef-edu",
        "title": "珊瑚礁生态保护",
        "description": "面向本科生的科普演示",
        "fields": [
            {"label": "主题", "value": "珊瑚礁生态保护与海洋生物多样性"},
            {"label": "受众", "value": "本科生与环境科学入门读者"},
            {"label": "结构", "value": "问题引入、生态价值、威胁因素、保护行动、结语"},
            {"label": "风格", "value": "科普友好、图文并重、数据可视化点缀"},
        ],
        "sort_order": 10,
    },
    {
        "id": "coffee-brew-guide",
        "title": "完美手冲咖啡",
        "description": "生活技巧类短演示",
        "fields": [
            {"label": "主题", "value": "如何冲泡一杯完美的特浓咖啡"},
            {"label": "受众", "value": "咖啡爱好者与居家入门者"},
            {"label": "结构", "value": "选豆、研磨、水温、萃取步骤、拉花技巧"},
            {"label": "风格", "value": "步骤清晰、温暖生活感、配图说明"},
        ],
        "sort_order": 20,
    },
    {
        "id": "product-roadshow",
        "title": "智能 H5 平台路演",
        "description": "新产品功能介绍",
        "fields": [
            {"label": "主题", "value": "智能 H5 演示平台功能与价值介绍"},
            {"label": "受众", "value": "潜在用户、合作伙伴与投资人"},
            {"label": "结构", "value": "痛点、产品亮点、核心功能、案例、行动号召"},
            {"label": "风格", "value": "商务专业、简洁大气、数据支撑"},
        ],
        "sort_order": 30,
    },
    {
        "id": "digital-transform-report",
        "title": "数字化转型复盘",
        "description": "企业季度汇报",
        "fields": [
            {"label": "主题", "value": "2025 企业数字化转型季度复盘"},
            {"label": "受众", "value": "管理层与业务负责人"},
            {"label": "结构", "value": "目标回顾、关键指标、项目进展、问题与下一步"},
            {"label": "风格", "value": "数据驱动、图表为主、结论先行"},
        ],
        "sort_order": 40,
    },
    {
        "id": "decision-psychology",
        "title": "决策心理学研讨",
        "description": "团队培训工作坊",
        "fields": [
            {"label": "主题", "value": "决策心理学：认知偏差与团队决策"},
            {"label": "受众", "value": "产品经理与团队负责人"},
            {"label": "结构", "value": "常见偏差、案例讨论、改进框架、练习"},
            {"label": "风格", "value": "互动研讨、案例故事、要点提炼"},
        ],
        "sort_order": 50,
    },
    {
        "id": "campus-recruitment",
        "title": "校园社团招新",
        "description": "活动宣传方案",
        "fields": [
            {"label": "主题", "value": "校园社团招新宣传与全年活动规划"},
            {"label": "受众", "value": "在校新生与社团成员"},
            {"label": "结构", "value": "社团介绍、亮点活动、加入方式、时间线"},
            {"label": "风格", "value": "年轻活力、色彩明快、信息清晰"},
        ],
        "sort_order": 60,
    },
]


class DeckPromptTemplateError(Exception):
    pass


def _parse_fields(raw: str) -> list[dict[str, str]]:
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise DeckPromptTemplateError("fields JSON 格式无效") from exc
    if not isinstance(data, list) or not data:
        raise DeckPromptTemplateError("至少填写一项提示词要素")
    out: list[dict[str, str]] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise DeckPromptTemplateError(f"fields[{idx}] 必须是对象")
        label = str(item.get("label") or "").strip()
        value = str(item.get("value") or "").strip()
        if not label or not value:
            raise DeckPromptTemplateError(f"fields[{idx}] 的 label 与 value 不能为空")
        out.append({"label": label, "value": value})
    return out


def _to_dict(row: DeckPromptTemplate) -> dict[str, Any]:
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description or "",
        "fields": _parse_fields(row.fields_json),
        "preview_url": row.preview_url or "",
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
        "preview_url": data.get("preview_url", ""),
    }


async def list_for_editor(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(DeckPromptTemplate)
        .where(DeckPromptTemplate.enabled == 1)
        .order_by(DeckPromptTemplate.sort_order, DeckPromptTemplate.id)
    )
    return [_public_item(_to_dict(r)) for r in result.scalars().all()]


async def admin_list(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(DeckPromptTemplate).order_by(DeckPromptTemplate.sort_order, DeckPromptTemplate.id)
    )
    return [_to_dict(r) for r in result.scalars().all()]


async def get_template(db: AsyncSession, template_id: str) -> dict | None:
    row = await db.get(DeckPromptTemplate, template_id)
    return _to_dict(row) if row else None


async def create_template(db: AsyncSession, data: dict[str, Any]) -> dict:
    tid = data["id"].strip()
    if not ID_PATTERN.match(tid):
        raise DeckPromptTemplateError("模板 ID 仅支持小写字母、数字与连字符，且以字母或数字开头")
    if await db.get(DeckPromptTemplate, tid):
        raise DeckPromptTemplateError("模板 ID 已存在")
    title = (data.get("title") or "").strip()
    if not title:
        raise DeckPromptTemplateError("标题不能为空")
    fields = data.get("fields") or []
    _parse_fields(json.dumps(fields, ensure_ascii=False))
    row = DeckPromptTemplate(
        id=tid,
        title=title,
        description=(data.get("description") or "").strip(),
        fields_json=json.dumps(fields, ensure_ascii=False),
        preview_url=(data.get("preview_url") or "").strip(),
        sort_order=int(data.get("sort_order") or 100),
        enabled=1 if data.get("enabled", True) else 0,
        source="admin",
    )
    db.add(row)
    await db.flush()
    return _to_dict(row)


async def update_template(db: AsyncSession, template_id: str, data: dict[str, Any]) -> dict:
    row = await db.get(DeckPromptTemplate, template_id)
    if not row:
        raise DeckPromptTemplateError("模板不存在")
    if data.get("title") is not None:
        title = str(data["title"]).strip()
        if not title:
            raise DeckPromptTemplateError("标题不能为空")
        row.title = title
    if data.get("description") is not None:
        row.description = str(data["description"]).strip()
    if data.get("fields") is not None:
        fields = _parse_fields(json.dumps(data["fields"], ensure_ascii=False))
        row.fields_json = json.dumps(fields, ensure_ascii=False)
    if data.get("preview_url") is not None:
        row.preview_url = str(data["preview_url"]).strip()
    if data.get("sort_order") is not None:
        row.sort_order = int(data["sort_order"])
    if data.get("enabled") is not None:
        row.enabled = 1 if data["enabled"] else 0
    await db.flush()
    return _to_dict(row)


async def delete_template(db: AsyncSession, template_id: str) -> None:
    row = await db.get(DeckPromptTemplate, template_id)
    if not row:
        raise DeckPromptTemplateError("模板不存在")
    if row.source == "builtin":
        raise DeckPromptTemplateError("内置模板不可删除")
    await db.delete(row)


async def seed_builtin_templates(db: AsyncSession) -> None:
    result = await db.execute(select(DeckPromptTemplate).limit(1))
    if result.scalar_one_or_none():
        return
    for item in BUILTIN_TEMPLATES:
        db.add(
            DeckPromptTemplate(
                id=item["id"],
                title=item["title"],
                description=item.get("description", ""),
                fields_json=json.dumps(item["fields"], ensure_ascii=False),
                preview_url=item.get("preview_url", ""),
                sort_order=item.get("sort_order", 100),
                enabled=1,
                source="builtin",
            )
        )
