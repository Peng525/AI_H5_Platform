"""Generate benchmark deck: LLM SVG pages -> svg_to_pptx export."""
from __future__ import annotations

import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from scripts.ppt_benchmark.console import safe_print
from .config import PPT_MASTER, RESULTS_DIR, profile_credentials
from .cost import (
    DEEPSEEK_PROFILE,
    add_usage,
    build_cost_record,
    estimate_usd,
    is_cost_tracked,
    normalize_usage,
    write_cost_json,
)
from .llm_client import BenchmarkLlmError, chat_completion
from .prompts import PAGE_SPECS, build_page_system_prompt, build_page_user_prompt
from .scorer import format_result_md, score_file

SVG_SCRIPT = PPT_MASTER / "skills" / "ppt-master" / "scripts" / "svg_to_pptx.py"


def _extract_svg(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:svg|xml)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    m = re.search(r"(<svg[\s\S]*?</svg>)", raw, re.IGNORECASE)
    if not m:
        raise BenchmarkLlmError("Model did not return valid SVG")
    return m.group(1)


def _export_pptx(project_dir: Path) -> Path:
    if not SVG_SCRIPT.is_file():
        raise FileNotFoundError(f"svg_to_pptx not found: {SVG_SCRIPT}")
    cmd = [sys.executable, str(SVG_SCRIPT), str(project_dir), "-s", "final"]
    proc = subprocess.run(
        cmd,
        cwd=str(PPT_MASTER),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"svg_to_pptx failed: {proc.stderr[:800] or proc.stdout[:800]}")
    exports = project_dir / "exports"
    pptx_files = sorted(exports.glob("*.pptx"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pptx_files:
        raise RuntimeError("No pptx in exports/")
    return pptx_files[0]


def run_single(profile: str, bench_type: str, *, dry_run: bool = False) -> dict:
    if bench_type not in PAGE_SPECS:
        raise ValueError(f"Unknown type: {bench_type}")

    date_str = date.today().strftime("%Y%m%d")
    slug = f"benchmark-{profile}-{bench_type}-{date_str}"
    project_dir = PPT_MASTER / "projects" / slug
    svg_dir = project_dir / "svg_output"
    svg_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    track_cost = is_cost_tracked(profile)
    usage_totals = normalize_usage(None) if track_cost else None
    page_records: list[dict] = [] if track_cost else []
    pages_ok = 0
    errors: list[str] = []
    model_id = profile_credentials(profile)["model"]

    system = build_page_system_prompt(bench_type, profile)
    for i, page in enumerate(PAGE_SPECS[bench_type], 1):
        out_path = svg_dir / page["file"]
        if dry_run:
            continue
        try:
            content, usage = chat_completion(
                profile,
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": build_page_user_prompt(bench_type, page)},
                ],
            )
            svg = _extract_svg(content)
            out_path.write_text(svg, encoding="utf-8")
            pages_ok += 1
            if track_cost:
                page_usage = normalize_usage(usage)
                usage_totals = add_usage(usage_totals, page_usage)
                page_cost = estimate_usd(profile, page_usage) or {}
                page_records.append(
                    {
                        "page": i,
                        "file": page["file"],
                        "usage": page_usage,
                        **page_cost,
                    }
                )
                safe_print(
                    f"  [{profile}/{bench_type}] page {i}/8 OK -> {page['file']} "
                    f"({page_usage['total_tokens']} tok, ${page_cost.get('estimated_usd_total', 0):.4f})"
                )
            else:
                tok = int(usage.get("total_tokens") or 0)
                safe_print(f"  [{profile}/{bench_type}] page {i}/8 OK -> {page['file']} ({tok} tok)")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{page['file']}: {exc}")
            safe_print(f"  [{profile}/{bench_type}] page {i}/8 FAIL: {exc}")

    elapsed_min = (time.time() - start) / 60.0
    cost: dict | None = None
    cost_record: dict | None = None
    cost_json_path: Path | None = None
    if track_cost and usage_totals is not None:
        cost = estimate_usd(profile, usage_totals)
        est_usd = (cost or {}).get("estimated_usd_total", 0)
        cost_record = build_cost_record(
            date_str=date_str,
            profile=profile,
            bench_type=bench_type,
            model=model_id,
            page_records=page_records,
            totals=usage_totals,
        )
        cost_json_path = write_cost_json(cost_record)
    else:
        est_usd = 0

    result: dict = {
        "profile": profile,
        "type": bench_type,
        "project_dir": project_dir,
        "pages_ok": pages_ok,
        "errors": errors,
        "elapsed_min": elapsed_min,
        "est_usd": est_usd,
    }
    if track_cost:
        result.update(
            {
                "cost": cost,
                "usage": usage_totals,
                "cost_record": cost_record,
                "cost_json": cost_json_path,
            }
        )

    if pages_ok == 0:
        result["export_path"] = None
        result["score"] = {"page_count": 0, "scores": {}, "core_avg": 0}
        md = format_result_md(
            date_str=date_str,
            profile=profile,
            bench_type=bench_type,
            project_path=project_dir,
            export_path=Path("-"),
            elapsed_min=elapsed_min,
            est_usd=est_usd,
            score=result["score"],
            cost=cost if track_cost else None,
            usage=usage_totals if track_cost else None,
            page_records=page_records if track_cost else None,
            cost_json=cost_json_path if track_cost else None,
            error="; ".join(errors) or "无页面生成",
        )
        out_md = RESULTS_DIR / f"{date_str}-{profile}-{bench_type}-phase1.md"
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(md, encoding="utf-8")
        result["result_md"] = out_md
        return result

    try:
        export_path = _export_pptx(project_dir)
        result["export_path"] = export_path
        result["score"] = score_file(export_path, bench_type, elapsed_min, est_usd)
    except Exception as exc:  # noqa: BLE001
        result["export_path"] = None
        result["score"] = {"page_count": pages_ok, "scores": {}, "core_avg": 0}
        errors.append(str(exc))

    md = format_result_md(
        date_str=date_str,
        profile=profile,
        bench_type=bench_type,
        project_path=project_dir,
        export_path=result.get("export_path") or Path("-"),
        elapsed_min=elapsed_min,
        est_usd=est_usd,
        score=result["score"],
        cost=cost if track_cost else None,
        usage=usage_totals if track_cost else None,
        page_records=page_records if track_cost else None,
        cost_json=cost_json_path if track_cost else None,
        error="; ".join(errors),
    )
    out_md = RESULTS_DIR / f"{date_str}-{profile}-{bench_type}-phase1.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(md, encoding="utf-8")
    result["result_md"] = out_md
    return result


def write_summary(rows: list[dict]) -> Path:
    """Write Phase 1 summary table."""
    from .cost import cost_from_result

    by_profile: dict[str, dict[str, float]] = {}
    cost_by_profile: dict[str, dict[str, float | None]] = {}
    for r in rows:
        p = r["profile"]
        t = r["type"]
        by_profile.setdefault(p, {})[t] = r.get("score", {}).get("core_avg", 0)
        cost_by_profile.setdefault(p, {})[t] = cost_from_result(r)

    lines = [
        "# Phase 1 横评汇总",
        "",
        f"生成时间：{date.today().isoformat()}",
        "",
        "费用列仅追踪 DeepSeek（deepseek-v4-pro）；其他模型请自行查看中转账单。",
        "DeepSeek 估算费用请与 [platform.deepseek.com/usage](https://platform.deepseek.com/usage) 对照。",
        "",
        "| active_profile | 调研 | 报告 | 学术 | 三类均分 | 费用(USD) | 备注 |",
        "|----------------|------|------|------|----------|-----------|------|",
    ]
    for p, types in by_profile.items():
        a = types.get("调研", 0)
        b = types.get("报告", 0)
        c = types.get("学术", 0)
        vals = [v for v in (a, b, c) if v]
        avg = round(sum(vals) / len(vals), 2) if vals else 0
        if p == DEEPSEEK_PROFILE:
            costs = cost_by_profile.get(p, {})
            cost_vals = [v for v in costs.values() if v is not None]
            total_cost = round(sum(cost_vals), 4) if cost_vals else None
            cost_str = f"${total_cost:.4f}" if total_cost is not None else "-"
        else:
            cost_str = "自行查看"
        note = "失败" if not vals else ""
        lines.append(
            f"| {p} | {a or '-'} | {b or '-'} | {c or '-'} | {avg or '-'} | {cost_str} | {note} |"
        )

    path = RESULTS_DIR / f"{date.today().strftime('%Y%m%d')}-phase1-summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
