"""大模型适配层：relay / official / auto。"""
import json
import re
from typing import Any

import httpx

from app.config import settings


class LlmError(Exception):
    pass


def _relay_ready() -> bool:
    return bool(settings.llm_relay_base_url and settings.llm_relay_api_key)


def _official_ready() -> bool:
    return bool(settings.llm_official_api_key)


async def _chat_openai_compatible(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
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


async def chat_relay(messages: list[dict[str, str]]) -> str:
    if not _relay_ready():
        raise LlmError("中转 API 未配置，请设置 LLM_RELAY_BASE_URL 与 LLM_RELAY_API_KEY")
    return await _chat_openai_compatible(
        settings.llm_relay_base_url,
        settings.llm_relay_api_key,
        settings.llm_relay_model,
        messages,
    )


async def chat_official(messages: list[dict[str, str]]) -> str:
    if not _official_ready():
        raise LlmError("官方 API 未配置，请设置 LLM_OFFICIAL_API_KEY")
    return await _chat_openai_compatible(
        settings.llm_official_base_url,
        settings.llm_official_api_key,
        settings.llm_official_model,
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


async def chat_auto(messages: list[dict[str, str]]) -> tuple[str, str]:
    channels = _resolve_auto_order()
    if not channels:
        raise LlmError("auto 模式无可用通道，请至少配置中转或官方 API 之一")
    errors: list[str] = []
    for ch in channels:
        try:
            if ch == "official":
                return await chat_official(messages), "official"
            return await chat_relay(messages), "relay"
        except LlmError as exc:
            errors.append(f"{ch}: {exc}")
    raise LlmError("auto 模式全部通道失败 — " + "；".join(errors))


async def chat_completion(
    messages: list[dict[str, str]],
    channel: str | None = None,
) -> tuple[str, str]:
    ch = (channel or settings.llm_default_channel).lower()
    if ch == "auto":
        return await chat_auto(messages)
    if ch == "relay":
        return await chat_relay(messages), "relay"
    if ch == "official":
        return await chat_official(messages), "official"
    raise LlmError(f"未知通道: {channel}")


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise LlmError("无法解析大模型返回的 JSON") from None
