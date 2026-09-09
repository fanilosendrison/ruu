#!/usr/bin/env python3
"""Replay retained Git smoke suites when Git meets the V1 minimum."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SMOKE_ROOT = ROOT / "qualification" / "git-smoke"
MINIMUM_GIT_VERSION = (2, 28, 0)
VERSION_PATTERN = re.compile(r"git version (\d+)\.(\d+)(?:\.(\d+))?")


def installed_git_version() -> tuple[int, int, int] | None:
    try:
        completed = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    match = VERSION_PATTERN.search(completed.stdout)
    if completed.returncode != 0 or match is None:
        return None
    return tuple(int(value or 0) for value in match.groups())


def display_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def require_supported_git() -> tuple[int, int, int]:
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
    return version


def replay_environment(temporary_root: Path) -> dict[str, str]:
    environment = os.environ.copy()
    original_path = environment.get("PATH", os.defpath)
    system_mktemp = shutil.which("mktemp", path=original_path)
    if system_mktemp is None:
        print("MKTEMP_UNAVAILABLE: Git smoke suites require mktemp")
        sys.exit(3)

    wrapper_directory = temporary_root / "commands"
    wrapper_directory.mkdir()
    wrapper = wrapper_directory / "mktemp"
    wrapper.write_text(
        "#!/usr/bin/env python3\n"
        "import os, pathlib, subprocess, sys\n"
        "result = subprocess.run([os.environ['RUU_SYSTEM_MKTEMP'], "
        "*sys.argv[1:]], capture_output=True, check=False)\n"
        "sys.stderr.buffer.write(result.stderr)\n"
        "if result.returncode:\n"
        "    sys.stdout.buffer.write(result.stdout)\n"
        "    raise SystemExit(result.returncode)\n"
        "for line in result.stdout.decode().splitlines():\n"
        "    print(pathlib.Path(line).resolve())\n"
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
    environment["PATH"] = f"{wrapper_directory}{os.pathsep}{original_path}"
    environment["RUU_SYSTEM_MKTEMP"] = system_mktemp
    return environment


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-version",
        action="store_true",
        help="check the Git minimum without executing smoke suites",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    version = require_supported_git()
    if arguments.check_version:
        print(
            "GIT VERSION: PASS "
            f"({display_version(version)} >= "
            f"{display_version(MINIMUM_GIT_VERSION)})"
        )
        return

    print(f"git version: {display_version(version)}")
    scripts = sorted(SMOKE_ROOT.rglob("git-*-smoke-v*.sh"))
    if not scripts:
        print("GIT SMOKES: FAIL (no retained smoke scripts discovered)")
        sys.exit(1)

    failures: list[str] = []
    with tempfile.TemporaryDirectory(
        prefix="ruu-git-smokes-", dir=ROOT.parent
    ) as temporary:
        environment = replay_environment(Path(temporary))
        for script in scripts:
            completed = subprocess.run(
                ["bash", str(script)],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
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
