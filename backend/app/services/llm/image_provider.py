"""AI 配图：读取 .env 中的通道、API Key 与 LLM_IMAGE_MODEL_*。"""
import base64
import re
from typing import Any

import httpx

from app.config import settings
from app.services.llm.model_tier import normalize_tier, resolve_image_model
from app.services.llm.provider import LlmError, _normalize_openai_base_url, _official_ready, _relay_ready


def _strip_secret(value: str) -> str:
    return (value or "").strip()


def _resolve_auto_order() -> list[str]:
    order: list[str] = []
    for part in settings.llm_auto_order.split(","):
        ch = part.strip().lower()
        if ch in ("relay", "official"):
            order.append(ch)
    if not order:
        order = ["official", "relay"]
    ready: list[str] = []
    for ch in order:
        if ch == "official" and _official_ready():
            ready.append(ch)
        if ch == "relay" and _relay_ready():
            ready.append(ch)
    return ready


def _channel_credentials(channel: str) -> tuple[str, str]:
    if channel == "relay":
        if not _relay_ready():
            raise LlmError("中转 API 未配置，请设置 LLM_RELAY_BASE_URL 与 LLM_RELAY_API_KEY")
        return settings.llm_relay_base_url, _strip_secret(settings.llm_relay_api_key)
    if channel == "official":
        if not _official_ready():
            raise LlmError("官方 API 未配置，请设置 LLM_OFFICIAL_API_KEY")
        return settings.llm_official_base_url, _strip_secret(settings.llm_official_api_key)
    raise LlmError(f"未知通道: {channel}")


def _build_prompt(prompt: str, style: str | None = None) -> str:
    text = prompt.strip()
    if style and style.strip():
        text = f"{text}\n\n画面风格：{style.strip()}"
    return text


def _as_data_url(raw: str, mime: str = "image/png") -> str:
    if raw.startswith("data:image"):
        return raw
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    return f"data:{mime};base64,{raw}"


def _extract_from_content(content: Any) -> str | None:
    if content is None:
        return None
    if isinstance(content, str):
        text = content.strip()
        if text.startswith("data:image"):
            return text
        if text.startswith("http://") or text.startswith("https://"):
            return text
        md = re.search(r"!\[[^\]]*\]\((data:image/[^)]+)\)", text)
        if md:
            return md.group(1)
        md_url = re.search(r"!\[[^\]]*\]\((https?://[^)]+)\)", text)
        if md_url:
            return md_url.group(1)
        b64 = re.search(r"(data:image/[^;]+;base64,[A-Za-z0-9+/=\s]+)", text)
        if b64:
            return b64.group(1).replace("\n", "").replace(" ", "")
        return None
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            ptype = part.get("type")
            if ptype == "image_url":
                url = part.get("image_url", {}).get("url")
                if url:
                    return _as_data_url(url)
            if ptype == "image":
                data = part.get("data") or part.get("image", {}).get("data")
                if data:
                    mime = part.get("mime_type") or part.get("image", {}).get("mime_type") or "image/png"
                    return _as_data_url(data, mime)
            nested = _extract_from_content(part.get("content") or part.get("text"))
            if nested:
                return nested
    return None


def _extract_image_from_response(data: dict[str, Any]) -> str | None:
    if not isinstance(data, dict):
        return None

    for key in ("image", "images", "output", "result"):
        val = data.get(key)
        if isinstance(val, str) and val:
            return _as_data_url(val)
        if isinstance(val, list) and val:
            first = val[0]
            if isinstance(first, str):
                return _as_data_url(first)
            if isinstance(first, dict):
                for k in ("url", "b64_json", "image", "data"):
                    if first.get(k):
                        return _as_data_url(first[k])

    items = data.get("data")
    if isinstance(items, list) and items:
        item = items[0]
        if isinstance(item, dict):
            if item.get("url"):
                return item["url"]
            if item.get("b64_json"):
                return _as_data_url(item["b64_json"])

    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message") or choices[0].get("delta") or {}
        for field in ("content", "images", "image"):
            found = _extract_from_content(msg.get(field))
            if found:
                return found
        for field in ("image", "images"):
            val = msg.get(field)
            if isinstance(val, str):
                return _as_data_url(val)

    return None


async def _post_json(url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise LlmError(f"生图请求失败 ({resp.status_code}): {resp.text[:500]}")
        return resp.json()


async def _try_images_generations(base_url: str, api_key: str, model: str, prompt: str) -> str:
    url = _normalize_openai_base_url(base_url) + "/images/generations"
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json",
    }
    data = await _post_json(url, api_key, payload)
    image = _extract_image_from_response(data)
    if not image:
        raise LlmError("images/generations 响应中未找到图片数据")
    return image


async def _try_chat_image(base_url: str, api_key: str, model: str, prompt: str) -> str:
    url = _normalize_openai_base_url(base_url) + "/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "image_config": {"aspect_ratio": "9:16", "image_size": "1K"},
    }
    data = await _post_json(url, api_key, payload)
    image = _extract_image_from_response(data)
    if not image:
        raise LlmError("chat/completions 响应中未找到图片数据")
    return image


async def _generate_on_channel(channel: str, model: str, prompt: str) -> str:
    base_url, api_key = _channel_credentials(channel)
    errors: list[str] = []
    for attempt in (_try_images_generations, _try_chat_image):
        try:
            return await attempt(base_url, api_key, model, prompt)
        except LlmError as exc:
            errors.append(str(exc))
    raise LlmError("；".join(errors))


async def generate_image(
    prompt: str,
    channel: str | None = None,
    tier: str | None = "free",
    style: str | None = None,
) -> tuple[str, str, str, int, int]:
    """返回 (图片 URL 或 data URL, 通道, 模型, 宽, 高)。"""
    full_prompt = _build_prompt(prompt, style)
    if not full_prompt:
        raise LlmError("请输入画面描述")
    model = resolve_image_model(tier)
    tier_norm = normalize_tier(tier)
    ch = (channel or settings.llm_default_channel).lower()
    display_channel = ch

    if tier_norm == "pro":
        actual_channel = "relay"
        display_channel = "official"
    elif ch == "auto":
        channels = _resolve_auto_order()
        if not channels:
            raise LlmError("auto 模式无可用通道，请配置 LLM_RELAY_* 或 LLM_OFFICIAL_API_KEY")
        errors: list[str] = []
        for used in channels:
            try:
                image = await _generate_on_channel(used, model, full_prompt)
                return image, used, model, 1024, 1024
            except LlmError as exc:
                errors.append(f"{used}: {exc}")
        raise LlmError("auto 模式全部通道失败 — " + "；".join(errors))
    else:
        if ch not in ("relay", "official"):
            raise LlmError(f"未知通道: {channel}")
        actual_channel = ch
        display_channel = ch

    image = await _generate_on_channel(actual_channel, model, full_prompt)
    return image, display_channel, model, 1024, 1024
