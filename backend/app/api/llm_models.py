"""公开的 LLM 模型列表（供前端生成页「模型」下拉框使用，不泄露密钥）。"""
from fastapi import APIRouter

from app.config import get_llm_providers

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])


@router.get("/models", summary="获取可用的 LLM 模型列表（公开）")
def list_llm_models():
    """返回 [{id, name, tier, model}]，不包含 base_url / api_key 等敏感字段。"""
    items = []
    for p in get_llm_providers():
        if not p["model"]:
            continue
        items.append({
            "id": p["id"],
            "name": p["name"],
            "tier": p["tier"],
            "model": p["model"],
        })
    return {"items": items}