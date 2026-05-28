"""从 JSON 文件加载 H5 模板。"""
import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "h5_templates"

# 兼容旧名：仍导出 FLAGSHIP_IDS 供外部引用
FLAGSHIP_IDS = frozenset({"story-wechat-mobile", "story-wechat-mobile-v2"})


def list_template_files() -> list[Path]:
    if not DATA_DIR.is_dir():
        return []
    return sorted(DATA_DIR.glob("*.json"))


def load_template_file(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not data.get("id"):
        raise ValueError(f"无效模板文件: {path.name}")
    return data


def load_all_file_templates() -> list[dict[str, Any]]:
    """加载 data/h5_templates 下全部 JSON 模板。"""
    items: list[dict[str, Any]] = []
    for path in list_template_files():
        try:
            items.append(load_template_file(path))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return items


def load_all_flagship_templates() -> list[dict[str, Any]]:
    """兼容旧接口：等同于 load_all_file_templates。"""
    return load_all_file_templates()
