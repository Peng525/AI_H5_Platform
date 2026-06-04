"""Print Cursor model settings for active profile (secrets masked)."""
from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
PROFILES_PATH = ROOT / "docs" / "ppt-master-benchmark" / "model-profiles.yaml"


def parse_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def mask(value: str) -> str:
    v = (value or "").strip()
    if len(v) <= 8:
        return "***" if v else "(empty)"
    return f"{v[:4]}...{v[-4:]}"


def load_profiles() -> dict:
    if yaml is None:
        raise SystemExit("Install PyYAML: python -m pip install pyyaml")
    data = yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Invalid model-profiles.yaml")
    return data


def resolve_profile(data: dict) -> tuple[str, dict]:
    active = data.get("active_profile", "deepseek-v4-pro")
    profiles = data.get("profiles") or {}
    if active not in profiles:
        raise SystemExit(f"Unknown active_profile: {active}")
    return active, profiles[active]


def env_value(env: dict[str, str], profile: dict, key: str) -> str:
    env_key = profile.get(key)
    if not env_key:
        return ""
    return env.get(str(env_key), "")


def main() -> None:
    env = parse_env(ENV_PATH.read_text(encoding="utf-8"))
    data = load_profiles()
    active, profile = resolve_profile(data)

    base_url = env_value(env, profile, "base_url_env")
    api_key = env_value(env, profile, "api_key_env")
    model = env_value(env, profile, "model_id_env") or str(profile.get("model_id", ""))

    print(f"active_profile: {active}")
    print(f"benchmark_phase: {data.get('benchmark_phase', 1)}")
    print()
    print("Cursor Settings -> Models:")
    print(f"  Override OpenAI Base URL: ON")
    print(f"  Base URL: {base_url or '(empty)'}")
    print(f"  OpenAI API Key: {mask(api_key)}")
    print(f"  Model name: {model or '(empty)'}")
    print()
    if profile.get("notes"):
        print(f"Note: {profile['notes']}")
    if not base_url or not api_key or not model:
        print()
        print("WARN: Missing values. Fill develop/.env then re-run this script.")


if __name__ == "__main__":
    main()
