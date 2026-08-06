"""Subprocess wrappers for ppt-master CLI scripts."""
from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

from app.services.ppt_master_paths import ppt_master_root
from app.services.ppt_master_worker.workspace import parse_init_stdout, scripts_dir, workspace_root


async def _run_cmd(cmd: list[str], *, cwd: Path | None = None, timeout: float | None = None) -> subprocess.CompletedProcess:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError as exc:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f"Command timed out: {' '.join(cmd)}") from exc
    stdout = stdout_b.decode("utf-8", errors="replace")
    stderr = stderr_b.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        detail = stderr.strip() or stdout.strip() or f"exit {proc.returncode}"
        raise RuntimeError(f"{' '.join(cmd)} failed: {detail[:1200]}")
    return subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)


async def init_project(slug: str, *, canvas_format: str = "ppt169") -> Path:
    pm = scripts_dir() / "project_manager.py"
    ws = workspace_root()
    cmd = [sys.executable, str(pm), "init", slug, "--format", canvas_format, "--dir", str(ws)]
    root = ppt_master_root()
    result = await _run_cmd(cmd, cwd=root, timeout=120)
    project_path = parse_init_stdout(result.stdout)
    if not project_path:
        matches = sorted(ws.glob(f"{slug}_*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if matches:
            project_path = matches[0]
    if not project_path or not project_path.is_dir():
        raise RuntimeError(f"Could not locate initialized project for {slug}")
    return project_path.resolve()


async def finalize_project(project_dir: Path) -> None:
    script = scripts_dir() / "finalize_svg.py"
    root = ppt_master_root()
    await _run_cmd([sys.executable, str(script), str(project_dir)], cwd=root, timeout=600)


async def export_pptx(project_dir: Path) -> Path:
    script = scripts_dir() / "svg_to_pptx.py"
    root = ppt_master_root()
    await _run_cmd(
        [sys.executable, str(script), str(project_dir), "-s", "final"],
        cwd=root,
        timeout=600,
    )
    exports = project_dir / "exports"
    pptx_files = sorted(exports.glob("*.pptx"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pptx_files:
        raise RuntimeError("No pptx exported")
    return pptx_files[0]
