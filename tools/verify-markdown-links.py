#!/usr/bin/env python3
"""Verify relative links in maintained Markdown documentation."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
MAINTAINED_ROOTS = (
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "qualification" / "README.md",
)
SKIPPED_PREFIXES = ("http://", "https://", "mailto:", "file://", "#")


def markdown_files() -> list[Path]:
    files: list[Path] = []
    for maintained_root in MAINTAINED_ROOTS:
        if maintained_root.is_file():
            files.append(maintained_root)
        elif maintained_root.is_dir():
            files.extend(maintained_root.rglob("*.md"))
    return sorted(files)


def main() -> None:
    errors: list[str] = []
    checked = 0
    for document in markdown_files():
        text = document.read_text()
        for match in LINK_PATTERN.finditer(text):
            raw_target = match.group(1).strip()
            target = raw_target.split(maxsplit=1)[0].strip("<>")
            if target.startswith(SKIPPED_PREFIXES):
                continue
            path_text = unquote(target.partition("#")[0])
            if not path_text:
                continue
            checked += 1
            resolved = (document.parent / path_text).resolve()
            if not resolved.exists():
                errors.append(
                    f"{document.relative_to(ROOT)}: missing link target {raw_target}"
                )

    if errors:
        print("MARKDOWN LINKS: FAIL")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)

    print(f"MARKDOWN LINKS: PASS ({checked} local targets checked)")


if __name__ == "__main__":
    main()
