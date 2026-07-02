"""Compile structured resume data into visual_document for WYSIWYG templates."""
from __future__ import annotations

import copy
import re
from typing import Any

TEMPLATE_CLASSIC_BLUE = "classic-blue"


def _default_structured() -> dict[str, Any]:
    return {
        "basics": {
            "name": "",
            "email": "",
            "phone": "",
            "summary": "",
            "gender": "",
            "age": "",
            "native_place": "",
            "education": "",
            "motto": "踏实肯干，责任心强，期待在贵公司实现价值。",
        },
        "job_intention": {
            "position": "",
            "city": "",
            "salary": "",
            "availability": "随时到岗",
        },
        "experience": [],
        "education": [],
        "skills": [],
        "skill_bars": [
            {"name": "计算机", "level": 85, "label": "精通"},
            {"name": "英语", "level": 70, "label": "良好"},
        ],
        "honors": [],
        "self_evaluation": "",
    }


def normalize_structured(data: dict[str, Any] | None) -> dict[str, Any]:
    base = _default_structured()
    if not isinstance(data, dict):
        return base
    out = copy.deepcopy(base)
    basics = data.get("basics")
    if isinstance(basics, dict):
        out["basics"].update({k: v for k, v in basics.items() if v is not None})
    ji = data.get("job_intention")
    if isinstance(ji, dict):
        out["job_intention"].update({k: v for k, v in ji.items() if v is not None})
    for key in ("experience", "education", "skills", "honors"):
        val = data.get(key)
        if isinstance(val, list):
            out[key] = val
    sb = data.get("skill_bars")
    if isinstance(sb, list) and sb:
        out["skill_bars"] = sb
    elif isinstance(data.get("skills"), list) and data["skills"] and not sb:
        out["skill_bars"] = [
            {"name": str(s), "level": 75, "label": "良好"} for s in data["skills"][:4]
        ]
    if data.get("self_evaluation"):
        out["self_evaluation"] = data["self_evaluation"]
    elif out["basics"].get("summary"):
        out["self_evaluation"] = out["basics"]["summary"]
    return out


def compile_visual_document(
    structured: dict[str, Any],
    existing: dict[str, Any] | None = None,
    *,
    template_id: str = TEMPLATE_CLASSIC_BLUE,
) -> dict[str, Any]:
    prev = existing if isinstance(existing, dict) else {}
    styles = prev.get("styles") if isinstance(prev.get("styles"), dict) else {}
    return {
        "template_id": template_id,
        "photo_file_id": prev.get("photo_file_id"),
        "styles": copy.deepcopy(styles),
    }


def get_bind_value(structured: dict[str, Any], bind: str) -> str:
    if not bind:
        return ""
    m0 = re.match(r"^(\w+)\[(\d+)\]$", bind)
    if m0:
        arr = structured.get(m0.group(1))
        if isinstance(arr, list):
            idx = int(m0.group(2))
            if 0 <= idx < len(arr):
                return str(arr[idx] or "")
        return ""
    m = re.match(r"^(\w+)\[(\d+)\]\.(\w+)$", bind)
    if m:
        arr_key, idx, field = m.group(1), int(m.group(2)), m.group(3)
        arr = structured.get(arr_key)
        if isinstance(arr, list) and 0 <= idx < len(arr):
            item = arr[idx]
            if isinstance(item, dict):
                val = item.get(field)
                if isinstance(val, list):
                    return "\n".join(str(x) for x in val)
                return str(val or "")
        return ""
    m2 = re.match(r"^(\w+)\[(\d+)\]\.(\w+)\[(\d+)\]$", bind)
    if m2:
        arr_key, idx, field, bidx = m2.group(1), int(m2.group(2)), m2.group(3), int(m2.group(4))
        arr = structured.get(arr_key)
        if isinstance(arr, list) and 0 <= idx < len(arr):
            item = arr[idx]
            if isinstance(item, dict):
                bullets = item.get(field)
                if isinstance(bullets, list) and 0 <= bidx < len(bullets):
                    return str(bullets[bidx] or "")
        return ""
    parts = bind.split(".")
    cur: Any = structured
    for p in parts:
        if not isinstance(cur, dict):
            return ""
        cur = cur.get(p)
    if isinstance(cur, list):
        return ", ".join(str(x) for x in cur)
    return str(cur or "") if cur is not None else ""


def set_bind_value(structured: dict[str, Any], bind: str, value: str) -> None:
    m0 = re.match(r"^(\w+)\[(\d+)\]$", bind)
    if m0:
        key, idx = m0.group(1), int(m0.group(2))
        arr = structured.setdefault(key, [])
        if not isinstance(arr, list):
            arr = []
            structured[key] = arr
        while len(arr) <= idx:
            arr.append("")
        arr[idx] = value
        return
    m = re.match(r"^(\w+)\[(\d+)\]\.(\w+)\[(\d+)\]$", bind)
    if m:
        arr_key, idx, field, bidx = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
        arr = structured.setdefault(arr_key, [])
        while len(arr) <= idx:
            arr.append({})
        if not isinstance(arr[idx], dict):
            arr[idx] = {}
        bullets = arr[idx].setdefault(field, [])
        if not isinstance(bullets, list):
            bullets = []
            arr[idx][field] = bullets
        while len(bullets) <= bidx:
            bullets.append("")
        bullets[bidx] = value
        return
    m2 = re.match(r"^(\w+)\[(\d+)\]\.(\w+)$", bind)
    if m2:
        arr_key, idx, field = m2.group(1), int(m2.group(2)), m2.group(3)
        arr = structured.setdefault(arr_key, [])
        while len(arr) <= idx:
            arr.append({})
        if not isinstance(arr[idx], dict):
            arr[idx] = {}
        if field == "bullets":
            arr[idx][field] = [line for line in value.split("\n") if line.strip()]
        else:
            arr[idx][field] = value
        return
    parts = bind.split(".")
    if len(parts) == 2:
        structured.setdefault(parts[0], {})[parts[1]] = value
    elif len(parts) == 1:
        structured[parts[0]] = value
