"""Load benchmark profiles and .env for PPT Phase 1 runs."""
from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError as yaml:  # type: ignore
    yaml = None

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
PROFILES_PATH = ROOT / "docs" / "ppt-master-benchmark" / "model-profiles.yaml"
PPT_MASTER = ROOT / "ppt-master-main"
RESULTS_DIR = ROOT / "docs" / "ppt-master-benchmark" / "results"
PROMPTS_DIR = ROOT / "docs" / "ppt-master-benchmark"

BENCHMARK_TYPES = ("调研", "报告", "学术")


def parse_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load_env() -> dict[str, str]:
    return parse_env(ENV_PATH.read_text(encoding="utf-8"))


def load_profiles_config() -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    return yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))


def profile_credentials(profile_key: str, env: dict[str, str] | None = None) -> dict[str, str]:
    env = env or load_env()
    cfg = load_profiles_config()
    p = cfg["profiles"][profile_key]
    base_key = p["base_url_env"]
    key_key = p["api_key_env"]
    model = env.get(p.get("model_id_env", ""), "") or p.get("model_id", "")
    return {
        "base_url": env.get(base_key, ""),
        "api_key": env.get(key_key, ""),
        "model": model,
        "label": p.get("label", profile_key),
    }
