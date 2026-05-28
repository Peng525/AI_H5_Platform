"""大模型设置 API。"""
from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.schemas import LlmSettingsOut, LlmTestResult
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
        relay_model=settings.llm_relay_model,
        official_model=settings.llm_official_model,
    )


@router.post("/大模型/测试", response_model=LlmTestResult, summary="测试大模型连通性")
async def test_llm(channel: str | None = Query(None, description="relay | official | 留空为 auto")):
    messages = [
        {"role": "system", "content": "你是助手，请用一句简体中文回复。"},
        {"role": "user", "content": "连通性测试"},
    ]
    try:
        _, used = await chat_completion(messages, channel)
        return LlmTestResult(success=True, channel=used, message="连接成功")
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/模板列表", summary="提示词模板（设置页）")
async def settings_templates():
    return {"items": list_templates()}
