"""大模型适配层：支持任意多个 API 供应商（LLM_PROVIDERS_JSON）。"""
import json
import re
from typing import Any

import httpx

from app.config import get_llm_provider, providers_ready_for_tier, settings
from app.services.llm.model_tier import resolve_text_model


class LlmError(Exception):
    pass


class QuotaLlmError(LlmError):
    """配额不足；API 层应映射 HTTP 402。"""


def _provider_ready(channel: str) -> bool:
    p = get_llm_provider(channel)
    return bool(p and p["base_url"] and p["api_key"])


def _relay_ready() -> bool:
    return _provider_ready("relay")


def _official_ready() -> bool:
    return _provider_ready("official")


def _normalize_openai_base_url(base_url: str) -> str:
    """OpenAI 兼容接口需以 /v1 结尾（如 https://us.novaiapi.com/v1）。

    校验协议头：缺 http:// 或 https:// 时直接抛出清晰错误。
    """
    base = (base_url or "").strip().rstrip("/")
    if not base:
        raise LlmError("LLM base URL 未配置，请在设置页为对应供应商填写 base_url")
    if not (base.startswith("http://") or base.startswith("https://")):
        raise LlmError(
            f"LLM base URL 缺少协议头（http:// 或 https://），当前值: {base_url!r}，"
            "请在设置页为对应供应商填写完整 base_url，格式示例: https://your-relay.example.com/v1"
        )
    if base.endswith("/v1") or base.endswith("/v1beta"):
        return base
    return base + "/v1"


def _resolve_channel_text_model(
    channel: str,
    tier: str | None = "free",
    model: str | None = None,
) -> str:
    override = (model or "").strip()
    if override:
        return override
    p = get_llm_provider(channel)
    if p and p["model"]:
        return p["model"]
    return resolve_text_model(tier)


def _channel_credentials(channel: str) -> tuple[str, str]:
    p = get_llm_provider(channel)
    if not p:
        raise LlmError(f"未知通道: {channel}")
    if not p["base_url"] or not p["api_key"]:
        raise LlmError(f"通道「{p['name']}」未配置 base_url / api_key")
    return p["base_url"], p["api_key"]


async def _chat_openai_compatible(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> tuple[str, dict]:
    url = _normalize_openai_base_url(base_url) + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": 0.7}
    async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise LlmError(f"大模型请求失败 ({resp.status_code}): {resp.text[:500]}")
        data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LlmError("大模型响应格式异常") from exc
    usage = data.get("usage") or {}
    return text, {
        "prompt_tokens": usage.get("prompt_tokens") or 0,
        "completion_tokens": usage.get("completion_tokens") or 0,
        "total_tokens": usage.get("total_tokens") or 0,
    }


async def _chat_tier_with_usage(
    messages: list[dict[str, str]],
    tier: str | None = "free",
    model: str | None = None,
) -> tuple[str, str, str, dict]:
    providers = providers_ready_for_tier(tier)
    if not providers:
        raise LlmError(f"{tier} 档无可用供应商，请在设置页为该档位配置至少一个 API（base_url + api_key）")
    errors: list[str] = []
    for p in providers:
        try:
            resolved = (model or "").strip() or p["model"] or resolve_text_model(tier)
            text, usage = await _chat_openai_compatible(
                p["base_url"], p["api_key"], resolved, messages
            )
            return text, p["id"], resolved, usage
        except LlmError as exc:
            errors.append(f"{p['name']}: {exc}")
    raise LlmError(f"{tier} 档全部供应商失败 — " + "；".join(errors))


async def chat_completion(
    messages: list[dict[str, str]],
    channel: str | None = None,
    tier: str | None = "free",
    model: str | None = None,
) -> tuple[str, str, str]:
    """返回 (回复文本, 通道, 实际使用的模型名)。向后兼容，不返回 token 数据。"""
    text, used, model_name, _usage = await chat_completion_with_usage(messages, channel, tier, model)
    return text, used, model_name


async def chat_completion_with_usage(
    messages: list[dict[str, str]],
    channel: str | None = None,
    tier: str | None = "free",
    model: str | None = None,
) -> tuple[str, str, str, dict]:
    """返回 (回复文本, 通道, 实际使用的模型名, usage_dict)。

    路由规则：显式传入某个供应商 id 时用该供应商；否则按档位(free/pro)路由，
    同档位多个供应商出错时自动重试下一个。
    """
    ch = (channel or "").strip().lower()
    if ch and ch != "auto" and get_llm_provider(ch):
        p = get_llm_provider(ch)
        if not p["base_url"] or not p["api_key"]:
            raise LlmError(f"通道「{p['name']}」未配置 base_url / api_key")
        resolved = _resolve_channel_text_model(ch, tier, model)
        text, usage = await _chat_openai_compatible(p["base_url"], p["api_key"], resolved, messages)
        return text, ch, resolved, usage
    return await _chat_tier_with_usage(messages, tier, model)


def _loads_json_relaxed(payload: str) -> dict[str, Any]:
    """解析 JSON；strict=False 允许模型返回字符串中的控制字符。"""
    return json.loads(payload, strict=False)


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise LlmError("大模型返回为空，请检查当前文本模型配置或稍后重试")
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    candidates = [text]
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        candidates.append(text[start : end + 1])
    last_err: json.JSONDecodeError | None = None
    for candidate in candidates:
        try:
            return _loads_json_relaxed(candidate)
        except json.JSONDecodeError as exc:
            last_err = exc
    raise LlmError(f"无法解析大模型返回的 JSON：{last_err}") from last_err
