"""Verify PPT benchmark env vars without printing secrets."""
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
REQUIRED = [
    "LLM_RELAY_BASE_URL",
    "LLM_RELAY_API_KEY",
    "base_url",
    "api_key",
    "model",
]
PLACEHOLDER_PREFIXES = ("你的", "请", "https://你的")


def parse_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def main() -> int:
    if not ENV_PATH.is_file():
        print(f"MISSING: {ENV_PATH}")
        return 1

    env = parse_env(ENV_PATH.read_text(encoding="utf-8"))
    ok = True
    for key in REQUIRED:
        val = env.get(key, "")
        if not val or any(val.startswith(p) for p in PLACEHOLDER_PREFIXES):
            print(f"{key}: MISSING or placeholder")
            ok = False
        elif "KEY" in key.upper() or key == "api_key":
            print(f"{key}: set ({len(val)} chars)")
        else:
            print(f"{key}: {val}")
            if key in ("LLM_RELAY_BASE_URL", "base_url") and not val.rstrip("/").endswith("/v1"):
                print("  WARN: should end with /v1")
                ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
