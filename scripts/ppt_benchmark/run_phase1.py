#!/usr/bin/env python3
"""PPT Master Phase 1 benchmark runner.

Usage:
  python -m scripts.ppt_benchmark.run_phase1 --profile deepseek-v4-pro --type 调研
  python -m scripts.ppt_benchmark.run_phase1 --all
  python -m scripts.ppt_benchmark.run_phase1 --test-models
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# allow `python develop/scripts/ppt_benchmark/run_phase1.py`
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from datetime import date

from scripts.ppt_benchmark.config import BENCHMARK_TYPES, RESULTS_DIR, load_profiles_config
from scripts.ppt_benchmark.console import safe_print
from scripts.ppt_benchmark.generator import run_single, write_summary
from scripts.ppt_benchmark.llm_client import BenchmarkLlmError, test_profile
from scripts.ppt_benchmark.scorer import format_result_md


def _write_skip_result(profile: str, bench_type: str, reason: str) -> dict:
    date_str = date.today().strftime("%Y%m%d")
    score = {"page_count": 0, "scores": {}, "core_avg": 0}
    md = format_result_md(
        date_str=date_str,
        profile=profile,
        bench_type=bench_type,
        project_path=Path("-"),
        export_path=Path("-"),
        elapsed_min=0,
        est_usd=0,
        score=score,
        error=reason,
    )
    out_md = RESULTS_DIR / f"{date_str}-{profile}-{bench_type}-phase1-SKIP.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(md, encoding="utf-8")
    return {"profile": profile, "type": bench_type, "score": score, "skipped": True}


def main() -> int:
    parser = argparse.ArgumentParser(description="PPT Master Phase 1 benchmark")
    parser.add_argument("--profile", help="active_profile key")
    parser.add_argument("--type", choices=list(BENCHMARK_TYPES), help="调研|报告|学术")
    parser.add_argument("--all", action="store_true", help="Run full 5x3 matrix")
    parser.add_argument("--test-models", action="store_true", help="Test API connectivity only")
    args = parser.parse_args()

    cfg = load_profiles_config()
    order = cfg.get("benchmark_order") or list(cfg["profiles"].keys())

    if args.test_models:
        for p in order:
            try:
                msg = test_profile(p)
                safe_print(f"OK  {p}: {msg[:80]}")
            except BenchmarkLlmError as exc:
                safe_print(f"FAIL {p}: {exc}")
        return 0

    runs: list[tuple[str, str]] = []
    results: list[dict] = []
    if args.all:
        profiles = cfg.get("profiles") or {}
        for p in order:
            if profiles.get(p, {}).get("phase1_skip"):
                for t in BENCHMARK_TYPES:
                    reason = profiles[p].get("notes", "phase1_skip")
                    safe_print(f"SKIP {p}/{t}: {reason[:60]}")
                    results.append(_write_skip_result(p, t, reason))
                continue
            for t in BENCHMARK_TYPES:
                runs.append((p, t))
    elif args.profile and args.type:
        profiles = cfg.get("profiles") or {}
        if profiles.get(args.profile, {}).get("phase1_skip"):
            results.append(_write_skip_result(args.profile, args.type, "phase1_skip"))
        else:
            runs.append((args.profile, args.type))
    else:
        parser.error("Specify --profile and --type, or --all, or --test-models")

    for profile, bench_type in runs:
        safe_print(f"\n=== Run: {profile} / {bench_type} ===")
        try:
            r = run_single(profile, bench_type)
            results.append(r)
            core = r.get("score", {}).get("core_avg", "-")
            exp = r.get("export_path")
            safe_print(f"Done: core_avg={core} export={exp}")
        except Exception as exc:  # noqa: BLE001
            safe_print(f"FAILED {profile}/{bench_type}: {exc}")
            results.append({"profile": profile, "type": bench_type, "score": {"core_avg": 0}})

    if len(results) > 1:
        summary = write_summary(results)
        safe_print(f"\nSummary: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
