"""Strategist stage: page plan via LLM with deterministic fallback."""
from __future__ import annotations

import logging
from typing import Any

from app.services.llm.provider import LlmError, chat_completion, extract_json
from app.services.ppt_master_worker.defaults import build_design_defaults
from app.services.ppt_master_worker.prompts import (
    build_strategist_system,
    build_strategist_user,
    write_spec_lock,
)
from app.services.ppt_master_worker.workspace import (
    list_layout_svgs,
    pick_layout_for_page,
    resolve_template_dir,
)

logger = logging.getLogger(__name__)


def _fallback_pages(
    *,
    topic: str,
    page_count: int,
    layout_files: list[str],
) -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    for i in range(1, page_count + 1):
        layout = pick_layout_for_page(layout_files, i, page_count)
        if i == 1:
            title, brief = "封面", f"主标题与副标题，主题：{topic}"
        elif i == page_count:
            title, brief = "结语", "总结与致谢"
        else:
            title, brief = f"第 {i} 页", f"围绕「{topic}」展开要点"
        pages.append(
            {
                "file": f"{i:02d}_{layout.replace('.svg', '')}.svg",
                "layout_file": layout,
                "title": title,
                "brief": brief,
            }
        )
    return pages


async def run_strategist(
    *,
    project_dir,
    topic: str,
    page_count: int,
    language: str,
    template_source_path: str | None,
    extra_content: str,
    channel: str,
    tier: str,
    model: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    template_dir = resolve_template_dir(template_source_path)
    layout_files = list_layout_svgs(template_dir) if template_dir else []
    defaults = build_design_defaults(
        topic=topic,
        page_count=page_count,
        language=language,
        template_title=template_dir.name if template_dir else "",
    )

    pages: list[dict[str, Any]]
    try:
        messages = [
            {"role": "system", "content": build_strategist_system(language)},
            {
                "role": "user",
                "content": build_strategist_user(
                    topic=topic,
                    page_count=page_count,
                    language=language,
                    layout_files=layout_files,
                    extra_content=extra_content,
                ),
            },
        ]
        text, _, _ = await chat_completion(messages, channel=channel, tier=tier, model=model or None)
        data = extract_json(text)
        raw_pages = data.get("pages") or []
        if not isinstance(raw_pages, list) or not raw_pages:
            raise LlmError("Strategist returned empty pages")
        pages = []
        for i, item in enumerate(raw_pages[:page_count], 1):
            if not isinstance(item, dict):
                continue
            layout = str(item.get("layout_file") or item.get("layout") or "").strip()
            if not layout:
                layout = pick_layout_for_page(layout_files, i, page_count)
            file_name = str(item.get("file") or f"{i:02d}_page.svg").strip()
            if not file_name.endswith(".svg"):
                file_name += ".svg"
            pages.append(
                {
                    "file": file_name,
                    "layout_file": layout,
                    "title": str(item.get("title") or f"Page {i}"),
                    "brief": str(item.get("brief") or ""),
                }
            )
        while len(pages) < page_count:
            idx = len(pages) + 1
            layout = pick_layout_for_page(layout_files, idx, page_count)
            pages.append(
                {
                    "file": f"{idx:02d}_page.svg",
                    "layout_file": layout,
                    "title": f"第 {idx} 页",
                    "brief": f"围绕「{topic}」展开",
                }
            )
        pages = pages[:page_count]
    except (LlmError, ValueError, KeyError) as exc:
        logger.warning("Strategist LLM fallback for job topic=%s: %s", topic[:80], exc)
        pages = _fallback_pages(topic=topic, page_count=page_count, layout_files=layout_files)

    write_spec_lock(project_dir, pages, defaults)
    sources = project_dir / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    (sources / "topic.md").write_text(
        f"# {topic}\n\n{extra_content.strip()}\n",
        encoding="utf-8",
    )
    if template_dir:
        meta = project_dir / "templates" / "chosen_template.txt"
        meta.parent.mkdir(parents=True, exist_ok=True)
        meta.write_text(str(template_dir), encoding="utf-8")
    return pages, defaults
