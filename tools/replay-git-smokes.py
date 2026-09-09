#!/usr/bin/env python3
"""Replay active Git smoke suites when the installed Git meets the V1 minimum."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SMOKE_ROOT = ROOT / "qualification" / "git-smoke"
MINIMUM_GIT_VERSION = (2, 28, 0)
VERSION_PATTERN = re.compile(r"git version (\d+)\.(\d+)(?:\.(\d+))?")


def installed_git_version() -> tuple[int, int, int] | None:
    completed = subprocess.run(
        ["git", "--version"], capture_output=True, text=True, check=False
    )
    match = VERSION_PATTERN.search(completed.stdout)
    if completed.returncode != 0 or match is None:
        return None
    return tuple(int(value or 0) for value in match.groups())


def display_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def main() -> None:
    version = installed_git_version()
    if version is None:
        print("GIT_VERSION_UNAVAILABLE: unable to determine the installed Git version")
        sys.exit(3)
    if version < MINIMUM_GIT_VERSION:
        print(
            "UNSUPPORTED_GIT_VERSION: "
            f"found {display_version(version)}, "
            f"required >= {display_version(MINIMUM_GIT_VERSION)}"
        )
        sys.exit(3)

    scripts = sorted(SMOKE_ROOT.rglob("git-*-smoke-v*.sh"))
    failures: list[str] = []
    for script in scripts:
        completed = subprocess.run(
            ["bash", str(script)], capture_output=True, text=True, check=False
        )
        relative = script.relative_to(ROOT)
        if completed.returncode == 0:
            print(f"{relative}: PASS")
            continue
        failures.append(str(relative))
        print(f"{relative}: FAIL ({completed.returncode})")
        if completed.stdout:
            print(completed.stdout.rstrip())
        if completed.stderr:
            print(completed.stderr.rstrip(), file=sys.stderr)

    if failures:
        print(f"GIT SMOKES: FAIL ({len(failures)} of {len(scripts)})")
        sys.exit(1)
    print(f"GIT SMOKES: PASS ({len(scripts)} scripts)")


if __name__ == "__main__":
    main()
