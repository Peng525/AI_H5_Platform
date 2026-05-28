"""大模型设置 API（管理员）。"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import settings
from app.deps.auth import require_admin
from app.models import User
from app.schemas import LlmSettingsAdminOut, LlmSettingsUpdate, LlmTestResult
from app.services.env_store import apply_settings_patch, mask_secret
from app.services.llm.model_tier import resolve_text_model
from app.services.llm.provider import LlmError, _official_ready, _relay_ready, chat_completion
from app.services.template_engine import list_templates

router = APIRouter(prefix="/api/v1/设置", tags=["设置"])


def _admin_settings_out() -> LlmSettingsAdminOut:
    return LlmSettingsAdminOut(
        default_channel=settings.llm_default_channel,
        auto_order=settings.llm_auto_order,
        relay_configured=_relay_ready(),
        official_configured=_official_ready(),
        model_free=settings.llm_model_free,
        model_pro=settings.llm_model_pro,
        image_model_free=settings.llm_image_model_free,
        image_model_pro=settings.llm_image_model_pro,
        relay_model=settings.llm_relay_model,
        official_model=settings.llm_official_model,
        timeout=settings.llm_timeout,
        free_quota_per_user=settings.free_quota_per_user,
        relay_base_url=settings.llm_relay_base_url,
        relay_api_key_masked=mask_secret(settings.llm_relay_api_key),
        official_base_url=settings.llm_official_base_url,
        official_api_key_masked=mask_secret(settings.llm_official_api_key),
    )


def _should_skip_secret(value: str | None) -> bool:
    if value is None:
        return True
    v = value.strip()
    return not v or v.startswith("****")


@router.get("/大模型", response_model=LlmSettingsAdminOut, summary="获取大模型配置（管理员）")
async def get_llm_settings(_admin: User = Depends(require_admin)):
    return _admin_settings_out()


@router.put("/大模型", response_model=LlmSettingsAdminOut, summary="保存大模型配置到 .env")
async def update_llm_settings(body: LlmSettingsUpdate, _admin: User = Depends(require_admin)):
    field_map = {
        "default_channel": "llm_default_channel",
        "auto_order": "llm_auto_order",
        "timeout": "llm_timeout",
        "free_quota_per_user": "free_quota_per_user",
        "relay_base_url": "llm_relay_base_url",
        "relay_model": "llm_relay_model",
        "official_base_url": "llm_official_base_url",
        "official_model": "llm_official_model",
        "model_free": "llm_model_free",
        "model_pro": "llm_model_pro",
        "image_model_free": "llm_image_model_free",
        "image_model_pro": "llm_image_model_pro",
    }
    patch: dict[str, str | int | float] = {}

    for field, attr in field_map.items():
        val = getattr(body, field, None)
        if val is not None:
            patch[attr] = val

    if not _should_skip_secret(body.relay_api_key):
        patch["llm_relay_api_key"] = body.relay_api_key.strip()
    if not _should_skip_secret(body.official_api_key):
        patch["llm_official_api_key"] = body.official_api_key.strip()

    if not patch:
        return _admin_settings_out()

    try:
        apply_settings_patch(patch)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"写入 .env 失败：{exc}") from exc

    return _admin_settings_out()


@router.post("/大模型/测试", response_model=LlmTestResult, summary="测试大模型连通性")
async def test_llm(
    channel: str | None = Query(None, description="relay | official | 留空为 auto"),
    tier: str = Query("free", description="free 免费 | pro 升级"),
    _admin: User = Depends(require_admin),
):
    messages = [
        {"role": "system", "content": "你是助手，请用一句简体中文回复。"},
        {"role": "user", "content": "连通性测试"},
    ]
    model = resolve_text_model(tier)
    try:
        _, used, _ = await chat_completion(messages, channel, tier)
        return LlmTestResult(
            success=True,
            channel=used,
            model=model,
            message=f"连接成功（{'免费档' if tier == 'free' else '升级档'}）",
        )
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/大模型/档位", summary="查看免费/升级模型与配图模型")
async def get_model_tiers(_admin: User = Depends(require_admin)):
    return {
        "免费档": {
            "文稿生成": settings.llm_model_free,
            "配图生成": settings.llm_image_model_free,
            "说明": "默认使用 Gemini 3.1 Flash（含免费配图）",
        },
        "升级档": {
            "文稿生成": settings.llm_model_pro,
            "配图生成": settings.llm_image_model_pro,
            "说明": "升级后使用 Gemini 3 Pro",
        },
    }


@router.get("/模板列表", summary="提示词模板（设置页）")
async def settings_templates(_admin: User = Depends(require_admin)):
    return {"items": list_templates()}
