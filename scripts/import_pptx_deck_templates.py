#!/usr/bin/env python3
"""Batch-import external PPTX files as ppt-master deck templates."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.deck.pptx_deck_template_import import (  # noqa: E402
    DECK_TITLES,
    DeckTemplateImportError,
    export_preview_for_slug,
    import_pptx_to_builtin_deck,
)


DEFAULT_PPTX = [
    r"e:\EdgeDownload\global_ai_capital_2026.pptx",
    r"e:\EdgeDownload\pritzker_2026.pptx",
    r"e:\EdgeDownload\swiss_grid_systems.pptx",
    r"e:\EdgeDownload\sugar_rush_memphis.pptx",
    r"e:\EdgeDownload\indie_bookstore_zine_guide.pptx",
    r"e:\EdgeDownload\glassmorphism_demo.pptx",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Import PPTX files as deck templates")
    parser.add_argument("pptx_files", nargs="*", help="Paths to .pptx files")
    args = parser.parse_args()
    paths = [Path(p) for p in (args.pptx_files or DEFAULT_PPTX)]

    ok: list[str] = []
    failed: list[tuple[str, str]] = []

    for path in paths:
        if not path.is_file():
            failed.append((str(path), "file not found"))
            print(f"SKIP not found: {path}", file=sys.stderr)
            continue
        slug_guess = path.stem.lower()
        title = DECK_TITLES.get(slug_guess)
        try:
            result = import_pptx_to_builtin_deck(path, title=title, overwrite=True)
            export_preview_for_slug(result["slug"])
            ok.append(f"{path.name} -> deck:{result['slug']}")
            print(f"OK {path.name} -> deck:{result['slug']}")
        except (DeckTemplateImportError, OSError, ValueError) as exc:
            failed.append((str(path), str(exc)))
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)

    print(f"\nDone: {len(ok)} succeeded, {len(failed)} failed")
    for name, err in failed:
        print(f"  - {name}: {err[:200]}", file=sys.stderr)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
