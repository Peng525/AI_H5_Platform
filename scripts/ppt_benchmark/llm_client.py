"""OpenAI-compatible chat for benchmark profiles."""
from __future__ import annotations

import httpx

from .config import profile_credentials


class BenchmarkLlmError(Exception):
    pass


def normalize_base_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1") or base.endswith("/v1beta"):
        return base
    return base + "/v1"


def chat_completion(
    profile_key: str,
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.4,
    timeout: float = 180.0,
) -> tuple[str, dict]:
    cred = profile_credentials(profile_key)
    if not cred["base_url"] or not cred["api_key"] or not cred["model"]:
        raise BenchmarkLlmError(f"Profile {profile_key} missing base_url/api_key/model in .env")

    url = normalize_base_url(cred["base_url"]) + "/chat/completions"
    headers = {"Authorization": f"Bearer {cred['api_key']}", "Content-Type": "application/json"}
    payload = {
        "model": cred["model"],
        "messages": messages,
        "temperature": temperature,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise BenchmarkLlmError(f"{profile_key} HTTP {resp.status_code}: {resp.text[:800]}")
        data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise BenchmarkLlmError(f"{profile_key} bad response shape") from exc
    usage = data.get("usage") or {}
    return content, usage


def test_profile(profile_key: str) -> str:
    text, _ = chat_completion(
        profile_key,
        [{"role": "user", "content": "Reply with exactly: OK"}],
        temperature=0,
        timeout=60,
    )
    return text.strip()[:200]
