"""大模型设置 API。"""
from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.schemas import LlmSettingsOut, LlmTestResult
from app.services.llm.model_tier import resolve_text_model
from app.services.llm.provider import LlmError, _official_ready, _relay_ready, chat_completion
from app.services.template_engine import list_templates

router = APIRouter(prefix="/api/v1/设置", tags=["设置"])


@router.get("/大模型", response_model=LlmSettingsOut, summary="获取大模型配置状态")
async def get_llm_settings():
    return LlmSettingsOut(
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
    )


@router.post("/大模型/测试", response_model=LlmTestResult, summary="测试大模型连通性")
async def test_llm(
    channel: str | None = Query(None, description="relay | official | 留空为 auto"),
    tier: str = Query("free", description="free 免费 gemini-3.1-flash | pro 升级 gemini-3-pro"),
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
async def get_model_tiers():
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
async def settings_templates():
    return {"items": list_templates()}
