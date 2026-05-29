"""编辑器素材版式块服务。"""
import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LayoutBlock

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
GROUPS = {"business", "story", "custom"}
PLACEMENTS = {"primary", "more"}


class LayoutBlockError(Exception):
    pass


def _parse_elements(raw: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise LayoutBlockError("elements JSON 格式无效") from exc
    if not isinstance(data, list):
        raise LayoutBlockError("elements 必须是数组")
    return data


def _validate_elements(elements: list[dict[str, Any]], field_name: str) -> None:
    for idx, el in enumerate(elements):
        if not isinstance(el, dict):
            raise LayoutBlockError(f"{field_name}[{idx}] 必须是对象")
        if not el.get("type"):
            raise LayoutBlockError(f"{field_name}[{idx}] 缺少 type 字段")


def _to_dict(row: LayoutBlock) -> dict[str, Any]:
    elements = _parse_elements(row.elements_json)
    try:
        elements_web = json.loads(row.elements_web_json or "[]")
        if not isinstance(elements_web, list):
            elements_web = []
    except json.JSONDecodeError:
        elements_web = []
    return {
        "id": row.id,
        "label": row.label,
        "icon": row.icon,
        "group": row.group,
        "placement": row.placement,
        "elements": elements,
        "elements_web": elements_web,
        "canvas_background": row.canvas_background or "",
        "sort_order": row.sort_order,
        "enabled": bool(row.enabled),
        "source": row.source or "admin",
    }


def _public_item(data: dict[str, Any]) -> dict[str, Any]:
    return {k: data[k] for k in data if k != "source"}


async def list_for_editor(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(LayoutBlock)
        .where(LayoutBlock.enabled == 1)
        .order_by(LayoutBlock.sort_order, LayoutBlock.id)
    )
    return [_public_item(_to_dict(r)) for r in result.scalars().all()]


async def admin_list(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(LayoutBlock).order_by(LayoutBlock.sort_order, LayoutBlock.id))
    return [_to_dict(r) for r in result.scalars().all()]


async def get_block(db: AsyncSession, block_id: str) -> dict | None:
    row = await db.get(LayoutBlock, block_id)
    return _to_dict(row) if row else None


async def create_block(db: AsyncSession, data: dict[str, Any]) -> dict:
    bid = data["id"].strip()
    if not ID_PATTERN.match(bid):
        raise LayoutBlockError("版式 ID 仅支持小写字母、数字与连字符，且以字母或数字开头")
    if await db.get(LayoutBlock, bid):
        raise LayoutBlockError("版式 ID 已存在")
    group = data.get("group", "custom")
    placement = data.get("placement", "more")
    if group not in GROUPS:
        raise LayoutBlockError("分组无效")
    if placement not in PLACEMENTS:
        raise LayoutBlockError("展示位置无效")
    elements = data.get("elements") or []
    elements_web = data.get("elements_web") or []
    _validate_elements(elements, "elements")
    _validate_elements(elements_web, "elements_web")
    if not elements and not elements_web:
        raise LayoutBlockError("至少填写手机端或网页端画布元素 JSON")
    row = LayoutBlock(
        id=bid,
        label=data["label"].strip(),
        icon=(data.get("icon") or "dashboard").strip(),
        group=group,
        placement=placement,
        elements_json=json.dumps(elements, ensure_ascii=False),
        elements_web_json=json.dumps(elements_web, ensure_ascii=False),
        canvas_background=data.get("canvas_background") or "",
        sort_order=int(data.get("sort_order", 100)),
        enabled=1 if data.get("enabled", True) else 0,
        source="admin",
    )
    db.add(row)
    await db.flush()
    return _to_dict(row)


async def update_block(db: AsyncSession, block_id: str, data: dict[str, Any]) -> dict:
    row = await db.get(LayoutBlock, block_id)
    if not row:
        raise LayoutBlockError("版式不存在")
    if "label" in data and data["label"] is not None:
        row.label = data["label"].strip()
    if "icon" in data and data["icon"] is not None:
        row.icon = data["icon"].strip()
    if "group" in data and data["group"] is not None:
        if data["group"] not in GROUPS:
            raise LayoutBlockError("分组无效")
        row.group = data["group"]
    if "placement" in data and data["placement"] is not None:
        if data["placement"] not in PLACEMENTS:
            raise LayoutBlockError("展示位置无效")
        row.placement = data["placement"]
    if "elements" in data and data["elements"] is not None:
        _validate_elements(data["elements"], "elements")
        row.elements_json = json.dumps(data["elements"], ensure_ascii=False)
    if "elements_web" in data and data["elements_web"] is not None:
        _validate_elements(data["elements_web"], "elements_web")
        row.elements_web_json = json.dumps(data["elements_web"], ensure_ascii=False)
    if "canvas_background" in data and data["canvas_background"] is not None:
        row.canvas_background = data["canvas_background"]
    if "sort_order" in data and data["sort_order"] is not None:
        row.sort_order = int(data["sort_order"])
    if "enabled" in data and data["enabled"] is not None:
        row.enabled = 1 if data["enabled"] else 0
    parsed_mobile = _parse_elements(row.elements_json)
    try:
        parsed_web = json.loads(row.elements_web_json or "[]")
        if not isinstance(parsed_web, list):
            parsed_web = []
    except json.JSONDecodeError:
        parsed_web = []
    if not parsed_mobile and not parsed_web:
        raise LayoutBlockError("至少保留手机端或网页端画布元素")
    row.source = "admin"
    await db.flush()
    return _to_dict(row)


async def delete_block(db: AsyncSession, block_id: str) -> None:
    row = await db.get(LayoutBlock, block_id)
    if not row:
        raise LayoutBlockError("版式不存在")
    await db.delete(row)
