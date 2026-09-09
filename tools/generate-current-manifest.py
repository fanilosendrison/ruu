#!/usr/bin/env python3
"""Generate the SHA-256 manifest for the active repository layout."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "qualification" / "manifests" / "current.sha256"
EXCLUDED_DIRECTORIES = {
    ROOT / ".git",
    ROOT / "qualification" / "releases",
}
EXCLUDED_FILES = {
    OUTPUT,
    ROOT / ".DS_Store",
}


def is_excluded(path: Path) -> bool:
    if path in EXCLUDED_FILES or "__pycache__" in path.parts:
        return True
    return any(directory == path or directory in path.parents for directory in EXCLUDED_DIRECTORIES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    files = sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not is_excluded(path)
    )
    lines = [f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}" for path in files]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n")
    print(f"generated {OUTPUT.relative_to(ROOT)} with {len(lines)} entries")


if __name__ == "__main__":
    main()
