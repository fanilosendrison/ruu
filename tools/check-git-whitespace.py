#!/usr/bin/env python3
"""Bind Ruu's whitespace obligation to the pinned proto-ring provider."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

from proto_ring import git_whitespace

ROOT = Path(__file__).resolve().parents[1]


def check(repository: Path, *, env: Mapping[str, str]) -> list[str]:
    """Evaluate Ruu's whitespace obligation through the shared mechanism."""

    return git_whitespace.check(repository, env=env)


def main() -> int:
    errors = check(ROOT, env=os.environ)
    if errors:
        print("git whitespace check: FAILED")
        for error in errors:
            print(error)
        return 1

    print("git whitespace check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
