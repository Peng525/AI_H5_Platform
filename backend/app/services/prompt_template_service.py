"""提示词 YAML 模板管理。"""
import re
from pathlib import Path
from typing import Any

import yaml

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
BUILTIN_IDS = {"full_deck", "single_page"}
SAFE_ID = re.compile(r"^[a-zA-Z0-9_\-]+$")


class PromptTemplateError(Exception):
    pass


def _file_for_id(template_id: str) -> Path:
    if not SAFE_ID.match(template_id):
        raise PromptTemplateError("模板 ID 仅允许字母、数字、下划线与连字符")
    matches = list(TEMPLATES_DIR.glob("*.yaml"))
    for path in matches:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if data.get("id", path.stem) == template_id:
            return path
    legacy = {
        "full_deck": "全量生成.yaml",
        "single_page": "单页改写.yaml",
    }
    if template_id in legacy:
        return TEMPLATES_DIR / legacy[template_id]
    return TEMPLATES_DIR / f"{template_id}.yaml"


def list_templates() -> list[dict[str, str]]:
    items = []
    if not TEMPLATES_DIR.exists():
        return items
    for path in sorted(TEMPLATES_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise PromptTemplateError(f"模板 {path.name} YAML 解析失败：{exc}") from exc
        tid = data.get("id", path.stem)
        items.append(
            {
                "id": tid,
                "name": data.get("name", path.stem),
                "description": data.get("description", ""),
                "file": path.name,
                "builtin": tid in BUILTIN_IDS or path.stem in ("全量生成", "单页改写"),
            }
        )
    return items


def get_template(template_id: str) -> dict[str, Any]:
    path = _file_for_id(template_id)
    if not path.exists():
        raise PromptTemplateError("模板不存在")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise PromptTemplateError(f"YAML 解析失败：{exc}") from exc
    tid = data.get("id", path.stem)
    return {
        "id": tid,
        "name": data.get("name", path.stem),
        "description": data.get("description", ""),
        "file": path.name,
        "system": data.get("system", ""),
        "user": data.get("user", ""),
        "builtin": tid in BUILTIN_IDS or path.stem in ("全量生成", "单页改写"),
    }


def _validate_body(body: dict[str, Any]) -> dict[str, str]:
    name = (body.get("name") or "").strip()
    if not name:
        raise PromptTemplateError("模板名称不能为空")
    system = body.get("system")
    if system is None or not str(system).strip():
        raise PromptTemplateError("system 提示词不能为空")
    user = body.get("user", "")
    return {
        "id": body.get("id", "").strip(),
        "name": name,
        "description": (body.get("description") or "").strip(),
        "system": str(system),
        "user": str(user),
    }


def save_template(template_id: str | None, body: dict[str, Any]) -> dict[str, Any]:
    validated = _validate_body(body)
    tid = template_id or validated["id"]
    if not tid:
        raise PromptTemplateError("模板 ID 不能为空")
    if not SAFE_ID.match(tid):
        raise PromptTemplateError("模板 ID 仅允许字母、数字、下划线与连字符")

    path = _file_for_id(tid) if template_id else TEMPLATES_DIR / f"{tid}.yaml"
    if not template_id and path.exists():
        raise PromptTemplateError("模板 ID 已存在")

    payload = {
        "id": tid,
        "name": validated["name"],
        "description": validated["description"],
        "system": validated["system"],
        "user": validated["user"],
    }
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    except OSError as exc:
        raise PromptTemplateError(f"写入模板文件失败：{exc}") from exc
    return get_template(tid)


def delete_template(template_id: str) -> None:
    detail = get_template(template_id)
    if detail.get("builtin"):
        raise PromptTemplateError("内置模板不可删除")
    path = _file_for_id(template_id)
    if path.exists():
        path.unlink()


def render_template(filename: str, variables: dict) -> list[dict[str, str]]:
    from jinja2 import Template

    path = TEMPLATES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"模板不存在: {filename}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise PromptTemplateError(f"YAML 解析失败：{exc}") from exc
    system_tpl = Template(data.get("system", ""))
    user_tpl = Template(data.get("user", ""))
    return [
        {"role": "system", "content": system_tpl.render(**variables)},
        {"role": "user", "content": user_tpl.render(**variables)},
    ]
