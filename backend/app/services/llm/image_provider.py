"""AI 配图：读取 .env 中的通道、API Key 与 LLM_IMAGE_MODEL_*。"""
import base64
import re
from typing import Any

import httpx

from app.config import get_llm_provider, providers_ready_for_tier, settings
from app.services.llm.model_tier import resolve_image_model
from app.services.llm.provider import LlmError, _normalize_openai_base_url


def _strip_secret(value: str) -> str:
    return (value or "").strip()


def _channel_credentials(channel: str) -> tuple[str, str]:
    p = get_llm_provider(channel)
    if not p:
        raise LlmError(f"未知通道: {channel}")
    if not p["base_url"] or not p["api_key"]:
        raise LlmError(f"通道「{p['name']}」未配置 base_url / api_key")
    return p["base_url"], _strip_secret(p["api_key"])


def _build_prompt(prompt: str, style: str | None = None) -> str:
    text = prompt.strip()
    if style and style.strip():
        text = f"{text}\n\n画面风格：{style.strip()}"
    return text


def _aspect_for_viewport(w: int | None, h: int | None) -> tuple[str, int, int]:
    """映射到 API 支持的宽高比，返回 (aspect_ratio, width, height)。"""
    if not w or not h or w <= 0 or h <= 0:
        return "1:1", 1024, 1024
    ratio = w / h
    if ratio < 0.85:
        return "9:16", 1024, 1792
    if ratio > 1.15:
        return "16:9", 1792, 1024
    return "1:1", 1024, 1024


def _fullscreen_prompt_suffix(aspect: str) -> str:
    if aspect == "9:16":
        return "\n\n竖屏全屏海报构图，主体居中，四边留安全边距。"
    if aspect == "16:9":
        return "\n\n横屏全屏背景构图，主体居中，四边留安全边距。"
    return ""


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
    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                raise LlmError(f"生图请求失败 ({resp.status_code}): {resp.text[:500]}")
            return resp.json()
    except httpx.ConnectError as exc:
        raise LlmError("无法连接生图服务，请检查 LLM 配置与服务器出网") from exc


async def _try_images_generations(
    base_url: str, api_key: str, model: str, prompt: str, size: str = "1024x1024"
) -> str:
    url = _normalize_openai_base_url(base_url) + "/images/generations"
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }
    data = await _post_json(url, api_key, payload)
    image = _extract_image_from_response(data)
    if not image:
        raise LlmError("images/generations 响应中未找到图片数据")
    return image


async def _try_chat_image(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    aspect_ratio: str = "9:16",
    reference_image_url: str | None = None,
) -> str:
    url = _normalize_openai_base_url(base_url) + "/chat/completions"
    if reference_image_url:
        user_content: str | list[dict[str, Any]] = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": reference_image_url}},
        ]
    else:
        user_content = prompt
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": user_content}],
        "modalities": ["image", "text"],
        "image_config": {"aspect_ratio": aspect_ratio, "image_size": "1K"},
    }
    data = await _post_json(url, api_key, payload)
    image = _extract_image_from_response(data)
    if not image:
        raise LlmError("chat/completions 响应中未找到图片数据")
    return image


async def _generate_on_channel(
    channel: str,
    model: str,
    prompt: str,
    aspect_ratio: str,
    size: str,
    reference_image_url: str | None = None,
) -> str:
    base_url, api_key = _channel_credentials(channel)
    errors: list[str] = []
    if reference_image_url:
        try:
            return await _try_chat_image(
                base_url, api_key, model, prompt, aspect_ratio, reference_image_url
            )
        except LlmError as exc:
            raise LlmError(f"参考图生图失败，请检查 LLM 是否支持多模态生图 — {exc}") from exc
    for attempt in (
        lambda: _try_images_generations(base_url, api_key, model, prompt, size),
        lambda: _try_chat_image(base_url, api_key, model, prompt, aspect_ratio),
    ):
        try:
            return await attempt()
        except LlmError as exc:
            errors.append(str(exc))
    raise LlmError("；".join(errors))


async def generate_image(
    prompt: str,
    channel: str | None = None,
    tier: str | None = "free",
    style: str | None = None,
    fit_mode: str | None = None,
    viewport_width: int | None = None,
    viewport_height: int | None = None,
    viewport_preset_id: str | None = None,
    use_reference_image: bool = False,
    reference_image_url: str | None = None,
) -> tuple[str, str, str, int, int]:
    """返回 (图片 URL 或 data URL, 通道, 模型, 宽, 高)。"""
    del viewport_preset_id  # 预留日志字段，调用方可写入 GenerationLog
    full_prompt = _build_prompt(prompt, style)
    if not full_prompt:
        raise LlmError("请输入画面描述")

    ref_url: str | None = None
    if use_reference_image and reference_image_url and reference_image_url.strip():
        ref_url = reference_image_url.strip()
        full_prompt += "\n\n在参考图基础上按描述重新生成，保持构图相似度适中。"

    if viewport_width and viewport_height:
        aspect_ratio, out_w, out_h = _aspect_for_viewport(viewport_width, viewport_height)
        if fit_mode == "fill" or aspect_ratio in ("9:16", "16:9"):
            full_prompt += _fullscreen_prompt_suffix(aspect_ratio)
    else:
        aspect_ratio, out_w, out_h = "1:1", 1024, 1024

    size = f"{out_w}x{out_h}"
    ch = (channel or "").strip().lower()

    if ch and ch != "auto" and get_llm_provider(ch):
        p = get_llm_provider(ch)
        model = p["model"] or resolve_image_model(tier)
        image = await _generate_on_channel(
            ch, model, full_prompt, aspect_ratio, size, ref_url
        )
        return image, ch, model, out_w, out_h

    providers = providers_ready_for_tier(tier)
    if not providers:
        raise LlmError(f"{tier} 档无可用供应商，请在该档位配置至少一个 API（base_url + api_key）")
    errors: list[str] = []
    for p in providers:
        try:
            model = p["model"] or resolve_image_model(tier)
            image = await _generate_on_channel(
                p["id"], model, full_prompt, aspect_ratio, size, ref_url
            )
            return image, p["id"], model, out_w, out_h
        except LlmError as exc:
            errors.append(f"{p['name']}: {exc}")
    raise LlmError(f"{tier} 档全部供应商失败 — " + "；".join(errors))
