"""大模型适配层：relay / official / auto。"""
import json
import re
from typing import Any

import httpx

from app.config import settings
from app.services.llm.model_tier import resolve_text_model


class LlmError(Exception):
    pass


def _relay_ready() -> bool:
    return bool(settings.llm_relay_base_url and settings.llm_relay_api_key.strip())


def _official_ready() -> bool:
    return bool(settings.llm_official_api_key.strip())


def _normalize_openai_base_url(base_url: str) -> str:
    """OpenAI 兼容接口需以 /v1 结尾（如 https://us.novaiapi.com/v1）。"""
    base = base_url.rstrip("/")
    if base.endswith("/v1") or base.endswith("/v1beta"):
        return base
    return base + "/v1"


async def _chat_openai_compatible(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> str:
    url = _normalize_openai_base_url(base_url) + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": 0.7}
    async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise LlmError(f"大模型请求失败 ({resp.status_code}): {resp.text[:500]}")
        data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LlmError("大模型响应格式异常") from exc


async def chat_relay(
    messages: list[dict[str, str]],
    tier: str | None = "free",
    model: str | None = None,
) -> str:
    if not _relay_ready():
        raise LlmError("中转 API 未配置，请设置 LLM_RELAY_BASE_URL 与 LLM_RELAY_API_KEY")
    resolved = model or resolve_text_model(tier)
    return await _chat_openai_compatible(
        settings.llm_relay_base_url,
        settings.llm_relay_api_key.strip(),
        resolved,
        messages,
    )


async def chat_official(
    messages: list[dict[str, str]],
    tier: str | None = "free",
    model: str | None = None,
) -> str:
    if not _official_ready():
        raise LlmError("官方 API 未配置，请设置 LLM_OFFICIAL_API_KEY")
    resolved = model or resolve_text_model(tier)
    return await _chat_openai_compatible(
        settings.llm_official_base_url,
        settings.llm_official_api_key.strip(),
        resolved,
        messages,
    )


def _resolve_auto_order() -> list[str]:
    order = []
    for part in settings.llm_auto_order.split(","):
        ch = part.strip().lower()
        if ch in ("relay", "official"):
            order.append(ch)
    if not order:
        order = ["official", "relay"]
    ready = []
    for ch in order:
        if ch == "official" and _official_ready():
            ready.append(ch)
        if ch == "relay" and _relay_ready():
            ready.append(ch)
    return ready


async def chat_auto(
    messages: list[dict[str, str]],
    tier: str | None = "free",
    model: str | None = None,
) -> tuple[str, str]:
    channels = _resolve_auto_order()
    if not channels:
        raise LlmError("auto 模式无可用通道，请至少配置中转或官方 API 之一")
    errors: list[str] = []
    for ch in channels:
        try:
            if ch == "official":
                return await chat_official(messages, tier, model), "official"
            return await chat_relay(messages, tier, model), "relay"
        except LlmError as exc:
            errors.append(f"{ch}: {exc}")
    raise LlmError("auto 模式全部通道失败 — " + "；".join(errors))


async def chat_completion(
    messages: list[dict[str, str]],
    channel: str | None = None,
    tier: str | None = "free",
    model: str | None = None,
) -> tuple[str, str, str]:
    """返回 (回复文本, 通道, 实际使用的模型名)。"""
    resolved = model or resolve_text_model(tier)
    ch = (channel or settings.llm_default_channel).lower()
    if ch == "auto":
        text, used = await chat_auto(messages, tier, model)
        return text, used, resolved
    if ch == "relay":
        return await chat_relay(messages, tier, model), "relay", resolved
    if ch == "official":
        return await chat_official(messages, tier, model), "official", resolved
    raise LlmError(f"未知通道: {channel}")


def _loads_json_relaxed(payload: str) -> dict[str, Any]:
    """解析 JSON；strict=False 允许模型返回字符串中的控制字符。"""
    return json.loads(payload, strict=False)


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
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
