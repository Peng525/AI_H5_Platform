"""Re-export benchmark projects, archive PPTX, rescore, write summary."""
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PPT_MASTER = ROOT / "ppt-master-main"
PROJECTS = PPT_MASTER / "projects"
RESULTS = ROOT / "docs" / "ppt-master-benchmark" / "results"
PPTX_ARCHIVE = RESULTS / "pptx"
SVG_SCRIPT = PPT_MASTER / "skills" / "ppt-master" / "scripts" / "svg_to_pptx.py"

sys.path.insert(0, str(ROOT))
from scripts.ppt_benchmark.cost import is_cost_tracked, load_cost_json  # noqa: E402
from scripts.ppt_benchmark.generator import _export_pptx, write_summary  # noqa: E402
from scripts.ppt_benchmark.scorer import format_result_md, score_file  # noqa: E402


def _parse_project_name(name: str) -> tuple[str, str, str] | None:
    # benchmark-{profile}-{type}-{date}
    if not name.startswith("benchmark-"):
        return None
    rest = name[len("benchmark-") :]
    for t in ("调研", "报告", "学术"):
        marker = f"-{t}-"
        if marker in rest:
            profile, _, date_part = rest.partition(marker)
            return profile, t, date_part
    return None


def export_and_archive(project_dir: Path) -> Path | None:
    svg_dir = project_dir / "svg_output"
    if not svg_dir.is_dir() or not list(svg_dir.glob("*.svg")):
        return None
    export_path = _export_pptx(project_dir)
    parsed = _parse_project_name(project_dir.name)
    if parsed:
        profile, bench_type, _date = parsed
        PPTX_ARCHIVE.mkdir(parents=True, exist_ok=True)
        dest = PPTX_ARCHIVE / f"{profile}-{bench_type}.pptx"
        shutil.copy2(export_path, dest)
        return dest
    return export_path


def _load_run_cost(profile: str, bench_type: str, date_str: str) -> tuple[dict | None, dict | None, list | None, float]:
    """Load DeepSeek cost sidecar if present."""
    if not is_cost_tracked(profile):
        return None, None, None, 0
    record = load_cost_json(date_str, profile, bench_type)
    if not record:
        return None, None, None, 0
    totals = record.get("totals") or {}
    cost = {
        "pricing_source": totals.get("pricing_source", "unknown"),
        "estimated_usd_input": totals.get("estimated_usd_input", 0),
        "estimated_usd_output": totals.get("estimated_usd_output", 0),
        "estimated_usd_total": totals.get("estimated_usd_total", 0),
    }
    usage = {
        k: totals.get(k, 0)
        for k in (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "prompt_cache_hit_tokens",
            "prompt_cache_miss_tokens",
        )
    }
    pages = record.get("pages")
    est_usd = float(cost["estimated_usd_total"])
    return cost, usage, pages, est_usd


def rescore_project(
    project_dir: Path,
    export_path: Path,
    elapsed_min: float = 15.0,
    est_usd: float | None = None,
) -> Path:
    parsed = _parse_project_name(project_dir.name)
    if not parsed:
        raise ValueError(project_dir.name)
    profile, bench_type, date_str = parsed
    cost, usage, page_records, loaded_usd = _load_run_cost(profile, bench_type, date_str)
    if est_usd is None:
        est_usd = loaded_usd
    cost_json_path = RESULTS / "costs" / f"{date_str}-{profile}-{bench_type}.json"
    score = score_file(export_path, bench_type, elapsed_min, est_usd)
    md = format_result_md(
        date_str=date_str,
        profile=profile,
        bench_type=bench_type,
        project_path=project_dir,
        export_path=export_path,
        elapsed_min=elapsed_min,
        est_usd=est_usd,
        score=score,
        cost=cost if is_cost_tracked(profile) else None,
        usage=usage if is_cost_tracked(profile) else None,
        page_records=page_records if is_cost_tracked(profile) else None,
        cost_json=cost_json_path if is_cost_tracked(profile) and cost_json_path.is_file() else None,
    )
    out = RESULTS / f"{date_str}-{profile}-{bench_type}-phase1.md"
    out.write_text(md, encoding="utf-8")
    return out


def main() -> int:
    rows: list[dict] = []
    for project_dir in sorted(PROJECTS.glob("benchmark-*")):
        if not project_dir.is_dir():
            continue
        parsed = _parse_project_name(project_dir.name)
        if not parsed:
            continue
        profile, bench_type, date_str = parsed
        try:
            archived = export_and_archive(project_dir)
            if not archived:
                print(f"SKIP (no svg): {project_dir.name}")
                continue
            rescore_project(project_dir, archived)
            from pptx import Presentation

            prs = Presentation(str(archived))
            _, _, _, est_usd = _load_run_cost(profile, bench_type, date_str)
            s = score_file(archived, bench_type, 15.0, est_usd)
            row: dict = {"profile": profile, "type": bench_type, "score": s}
            if is_cost_tracked(profile):
                row["est_usd"] = est_usd
                record = load_cost_json(date_str, profile, bench_type)
                if record:
                    row["cost_record"] = record
            rows.append(row)
            print(f"OK {profile}/{bench_type} -> {archived} ({len(prs.slides)} slides)")
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {project_dir.name}: {exc}")

    if rows:
        summary = write_summary(rows)
        print(f"Summary: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
