"""提示词模板引擎。"""
from pathlib import Path

import yaml
from jinja2 import Template

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"


def list_templates() -> list[dict[str, str]]:
    items = []
    for path in sorted(TEMPLATES_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        items.append(
            {
                "id": data.get("id", path.stem),
                "name": data.get("name", path.stem),
                "description": data.get("description", ""),
                "file": path.name,
            }
        )
    return items


def render_template(filename: str, variables: dict) -> list[dict[str, str]]:
    path = TEMPLATES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"模板不存在: {filename}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    system_tpl = Template(data["system"])
    user_tpl = Template(data.get("user", ""))
    return [
        {"role": "system", "content": system_tpl.render(**variables)},
        {"role": "user", "content": user_tpl.render(**variables)},
    ]
