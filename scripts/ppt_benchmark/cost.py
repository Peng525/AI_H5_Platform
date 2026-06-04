"""DeepSeek-only token usage aggregation and USD cost estimates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as yaml:  # type: ignore
    yaml = None

from .config import RESULTS_DIR

DEEPSEEK_PROFILE = "deepseek-v4-pro"
DEEPSEEK_USAGE_URL = "https://platform.deepseek.com/usage"

PRICING_PATH = Path(__file__).resolve().parent / "pricing.yaml"
COSTS_DIR = RESULTS_DIR / "costs"

_EMPTY_USAGE = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 0,
}


def is_cost_tracked(profile: str) -> bool:
    return profile == DEEPSEEK_PROFILE


def load_pricing() -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    data = yaml.safe_load(PRICING_PATH.read_text(encoding="utf-8"))
    return data or {}


def normalize_usage(usage: dict | None) -> dict[str, int]:
    """Normalize API usage dict; infer cache_miss when cache fields absent."""
    if not usage:
        return dict(_EMPTY_USAGE)
    prompt = int(usage.get("prompt_tokens") or 0)
    completion = int(usage.get("completion_tokens") or 0)
    total = int(usage.get("total_tokens") or prompt + completion)
    cache_hit = int(usage.get("prompt_cache_hit_tokens") or 0)
    cache_miss = int(usage.get("prompt_cache_miss_tokens") or 0)
    if prompt > 0 and cache_hit == 0 and cache_miss == 0:
        cache_miss = prompt
    elif cache_hit + cache_miss > prompt and prompt > 0:
        cache_miss = max(0, prompt - cache_hit)
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
        "prompt_cache_hit_tokens": cache_hit,
        "prompt_cache_miss_tokens": cache_miss,
    }


def add_usage(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {k: a.get(k, 0) + b.get(k, 0) for k in _EMPTY_USAGE}


def estimate_usd(profile: str, totals: dict[str, int], *, pricing: dict | None = None) -> dict[str, Any] | None:
    """Return DeepSeek cost breakdown; None for non-tracked profiles."""
    if not is_cost_tracked(profile):
        return None

    pricing = pricing or load_pricing()
    model_pricing = pricing.get(DEEPSEEK_PROFILE) or {}

    cache_hit = totals.get("prompt_cache_hit_tokens", 0)
    cache_miss = totals.get("prompt_cache_miss_tokens", 0)
    completion = totals.get("completion_tokens", 0)

    hit_rate = model_pricing.get("input_per_1m_cache_hit", 0)
    miss_rate = model_pricing.get("input_per_1m_cache_miss", 0)
    usd_input = (cache_hit / 1_000_000) * hit_rate + (cache_miss / 1_000_000) * miss_rate

    out_rate = model_pricing.get("output_per_1m", 0)
    usd_output = (completion / 1_000_000) * out_rate
    usd_total = usd_input + usd_output

    return {
        "pricing_source": model_pricing.get("source", "official"),
        "estimated_usd_input": round(usd_input, 6),
        "estimated_usd_output": round(usd_output, 6),
        "estimated_usd_total": round(usd_total, 6),
    }


def build_cost_record(
    *,
    date_str: str,
    profile: str,
    bench_type: str,
    model: str,
    page_records: list[dict],
    totals: dict[str, int],
) -> dict[str, Any]:
    cost = estimate_usd(profile, totals) or {}
    return {
        "date": date_str,
        "profile": profile,
        "type": bench_type,
        "model": model,
        "compare_with": DEEPSEEK_USAGE_URL,
        "pages": page_records,
        "totals": {**totals, **cost},
    }


def write_cost_json(record: dict[str, Any]) -> Path:
    COSTS_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{record['date']}-{record['profile']}-{record['type']}.json"
    path = COSTS_DIR / name
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_cost_json(date_str: str, profile: str, bench_type: str) -> dict | None:
    if not is_cost_tracked(profile):
        return None
    path = COSTS_DIR / f"{date_str}-{profile}-{bench_type}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def cost_from_result(result: dict) -> float | None:
    """Extract total USD from a run result dict (DeepSeek only)."""
    profile = result.get("profile", "")
    if not is_cost_tracked(profile):
        return None
    cost = result.get("cost")
    if isinstance(cost, dict) and "estimated_usd_total" in cost:
        return float(cost["estimated_usd_total"])
    if "est_usd" in result and result.get("cost") is not None:
        return float(result["est_usd"])
    totals = result.get("cost_record", {}).get("totals")
    if isinstance(totals, dict) and "estimated_usd_total" in totals:
        return float(totals["estimated_usd_total"])
    return None
