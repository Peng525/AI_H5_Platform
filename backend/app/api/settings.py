"""大模型设置 API（管理员）。"""
import json

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import get_llm_providers, provider_tier, settings
from app.deps.auth import require_admin
from app.models import User
from app.schemas import (
    LlmProviderOut,
    LlmSettingsAdminOut,
    LlmSettingsUpdate,
    LlmTestResult,
    PromptTemplateCreate,
    PromptTemplateOut,
    PromptTemplateUpdate,
)
from app.services.env_store import apply_settings_patch, mask_secret
from app.services.llm.image_provider import generate_image
from app.services.llm.model_tier import resolve_image_model
from app.services.llm.provider import LlmError
from app.services.prompt_template_service import (
    PromptTemplateError,
    delete_template as delete_prompt_template,
    get_template as get_prompt_template,
    list_templates,
    save_template,
)

router = APIRouter(prefix="/api/v1/设置", tags=["设置"])


def _admin_settings_out() -> LlmSettingsAdminOut:
    providers = [
        LlmProviderOut(
            id=p["id"],
            name=p["name"],
            tier=p["tier"],
            base_url=p["base_url"],
            api_key_masked=mask_secret(p["api_key"]),
            model=p["model"],
            configured=bool(p["base_url"] and p["api_key"]),
        )
        for p in get_llm_providers()
    ]
    return LlmSettingsAdminOut(
        default_channel=settings.llm_default_channel,
        auto_order=settings.llm_auto_order,
        providers=providers,
        model_free=settings.llm_model_free,
        model_pro=settings.llm_model_pro,
        image_model_free=settings.llm_image_model_free,
        image_model_pro=settings.llm_image_model_pro,
        timeout=settings.llm_timeout,
        free_quota_per_user=settings.free_quota_per_user,
    )


@router.get("/大模型", response_model=LlmSettingsAdminOut, summary="获取大模型配置（管理员）")
async def get_llm_settings(_admin: User = Depends(require_admin)):
    return _admin_settings_out()


@router.put("/大模型", response_model=LlmSettingsAdminOut, summary="保存大模型配置到 .env")
async def update_llm_settings(body: LlmSettingsUpdate, _admin: User = Depends(require_admin)):
    patch: dict[str, str | int | float] = {}

    scalar_map = {
        "default_channel": "llm_default_channel",
        "auto_order": "llm_auto_order",
        "timeout": "llm_timeout",
        "free_quota_per_user": "free_quota_per_user",
        "model_free": "llm_model_free",
        "model_pro": "llm_model_pro",
        "image_model_free": "llm_image_model_free",
        "image_model_pro": "llm_image_model_pro",
    }
    for field, attr in scalar_map.items():
        val = getattr(body, field, None)
        if val is not None:
            patch[attr] = val

    if body.providers is not None:
        existing = {p["id"]: p for p in get_llm_providers()}
        merged: list[dict] = []
        for item in body.providers:
            pid = str(item.get("id") or "").strip().lower()
            if not pid:
                continue
            api_key = str(item.get("api_key") or "").strip()
            if (not api_key or api_key.startswith("****")) and pid in existing:
                api_key = existing[pid]["api_key"]
            merged.append({
                "id": pid,
                "name": str(item.get("name") or pid)[:32],
                "tier": provider_tier(item.get("tier")),
                "base_url": str(item.get("base_url") or "").strip(),
                "api_key": api_key,
                "model": str(item.get("model") or "").strip(),
            })
        patch["llm_providers_json"] = json.dumps(merged, ensure_ascii=False)

    if not patch:
        return _admin_settings_out()

    try:
        apply_settings_patch(patch)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"写入 .env 失败：{exc}") from exc

    return _admin_settings_out()


@router.post("/大模型/测试", response_model=LlmTestResult, summary="测试 AI 生图连通性")
async def test_llm(
    channel: str | None = Query(None, description="relay | official | 留空为 auto"),
    tier: str = Query("free", description="free 免费 | pro 升级"),
    _admin: User = Depends(require_admin),
):
    model = resolve_image_model(tier)
    try:
        _, used, used_model, _, _ = await generate_image(
            "连通性测试：简洁蓝色圆形图标，白底",
            channel,
            tier,
        )
        return LlmTestResult(
            success=True,
            channel=used,
            model=used_model or model,
            message=f"生图连接成功（{'免费档' if tier == 'free' else '升级档'}）",
        )
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/大模型/档位", summary="查看免费/升级生图模型")
async def get_model_tiers(_admin: User = Depends(require_admin)):
    return {
        "免费档": {
            "生图模型": settings.llm_image_model_free,
            "说明": "编辑器 AI 面板「AI 生图」",
        },
        "升级档": {
            "生图模型": settings.llm_image_model_pro,
            "说明": "会员高清生图通道",
        },
    }


@router.get("/模板列表", summary="提示词模板列表")
async def settings_templates(_admin: User = Depends(require_admin)):
    return {"items": list_templates()}


@router.get("/提示词模板/{template_id}", response_model=PromptTemplateOut, summary="提示词模板详情")
async def get_prompt_template_detail(template_id: str, _admin: User = Depends(require_admin)):
    try:
        row = get_prompt_template(template_id)
    except PromptTemplateError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return PromptTemplateOut(**row)


@router.post("/提示词模板", response_model=PromptTemplateOut, summary="新建提示词模板")
async def create_prompt_template(body: PromptTemplateCreate, _admin: User = Depends(require_admin)):
    try:
        row = save_template(None, body.model_dump())
    except PromptTemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PromptTemplateOut(**row)


@router.put("/提示词模板/{template_id}", response_model=PromptTemplateOut, summary="更新提示词模板")
async def update_prompt_template(
    template_id: str,
    body: PromptTemplateUpdate,
    _admin: User = Depends(require_admin),
):
    payload = body.model_dump(exclude_unset=True)
    existing = get_prompt_template(template_id)
    merged = {**existing, **payload}
    try:
        row = save_template(template_id, merged)
    except PromptTemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PromptTemplateOut(**row)


@router.delete("/提示词模板/{template_id}", summary="删除提示词模板")
async def remove_prompt_template(template_id: str, _admin: User = Depends(require_admin)):
    try:
        delete_prompt_template(template_id)
    except PromptTemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "已删除"}
