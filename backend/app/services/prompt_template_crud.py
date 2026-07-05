"""生图 / 演示文稿 DB 提示词模板共用 CRUD 逻辑。"""
import json
import re
from typing import Any, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def parse_fields(raw: str, error_cls: type[Exception]) -> list[dict[str, str]]:
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise error_cls("fields JSON 格式无效") from exc
    if not isinstance(data, list) or not data:
        raise error_cls("至少填写一项提示词要素")
    out: list[dict[str, str]] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise error_cls(f"fields[{idx}] 必须是对象")
        label = str(item.get("label") or "").strip()
        value = str(item.get("value") or "").strip()
        if not label or not value:
            raise error_cls(f"fields[{idx}] 的 label 与 value 不能为空")
        out.append({"label": label, "value": value})
    return out


def row_to_dict(row: Any, error_cls: type[Exception]) -> dict[str, Any]:
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description or "",
        "fields": parse_fields(row.fields_json, error_cls),
        "preview_url": getattr(row, "preview_url", None) or "",
        "sort_order": row.sort_order,
        "enabled": bool(row.enabled),
        "source": row.source or "admin",
    }


def public_item(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": data["id"],
        "title": data["title"],
        "description": data.get("description", ""),
        "fields": data["fields"],
        "preview_url": data.get("preview_url", ""),
    }


async def list_enabled(db: AsyncSession, model: Type, error_cls: type[Exception]) -> list[dict]:
    result = await db.execute(
        select(model)
        .where(model.enabled == 1)
        .order_by(model.sort_order, model.id)
    )
    return [public_item(row_to_dict(r, error_cls)) for r in result.scalars().all()]


async def admin_list_all(db: AsyncSession, model: Type, error_cls: type[Exception]) -> list[dict]:
    result = await db.execute(select(model).order_by(model.sort_order, model.id))
    return [row_to_dict(r, error_cls) for r in result.scalars().all()]


async def get_by_id(db: AsyncSession, model: Type, template_id: str, error_cls: type[Exception]) -> dict | None:
    row = await db.get(model, template_id)
    return row_to_dict(row, error_cls) if row else None


async def create_row(
    db: AsyncSession,
    model: Type,
    data: dict[str, Any],
    error_cls: type[Exception],
) -> dict:
    tid = data["id"].strip()
    if not ID_PATTERN.match(tid):
        raise error_cls("模板 ID 仅支持小写字母、数字与连字符，且以字母或数字开头")
    if await db.get(model, tid):
        raise error_cls("模板 ID 已存在")
    title = (data.get("title") or "").strip()
    if not title:
        raise error_cls("标题不能为空")
    fields = data.get("fields") or []
    parse_fields(json.dumps(fields, ensure_ascii=False), error_cls)
    row = model(
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
    return row_to_dict(row, error_cls)


async def update_row(
    db: AsyncSession,
    model: Type,
    template_id: str,
    data: dict[str, Any],
    error_cls: type[Exception],
) -> dict:
    row = await db.get(model, template_id)
    if not row:
        raise error_cls("模板不存在")
    if data.get("title") is not None:
        title = str(data["title"]).strip()
        if not title:
            raise error_cls("标题不能为空")
        row.title = title
    if data.get("description") is not None:
        row.description = str(data["description"]).strip()
    if data.get("fields") is not None:
        fields = parse_fields(json.dumps(data["fields"], ensure_ascii=False), error_cls)
        row.fields_json = json.dumps(fields, ensure_ascii=False)
    if data.get("preview_url") is not None:
        row.preview_url = str(data["preview_url"]).strip()
    if data.get("sort_order") is not None:
        row.sort_order = int(data["sort_order"])
    if data.get("enabled") is not None:
        row.enabled = 1 if data["enabled"] else 0
    await db.flush()
    return row_to_dict(row, error_cls)


async def delete_row(db: AsyncSession, model: Type, template_id: str, error_cls: type[Exception]) -> None:
    row = await db.get(model, template_id)
    if not row:
        raise error_cls("模板不存在")
    if row.source == "builtin":
        raise error_cls("内置模板不可删除")
    await db.delete(row)


async def seed_builtins(db: AsyncSession, model: Type, builtins: list[dict[str, Any]]) -> None:
    result = await db.execute(select(model).limit(1))
    if result.scalar_one_or_none():
        return
    for item in builtins:
        db.add(
            model(
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
