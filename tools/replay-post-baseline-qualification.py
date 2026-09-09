#!/usr/bin/env python3
"""Replay registered post-ADR-080 state-space qualifications."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys

from qualification.postbaseline import Qualification, discover


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "audit_version",
        nargs="?",
        default="all",
        help="numeric post-baseline audit version, or all (default)",
    )
    return parser.parse_args()


def select_qualifications(
    qualifications: tuple[Qualification, ...], value: str
) -> tuple[Qualification, ...]:
    if value == "all":
        return qualifications
    try:
        version = int(value)
    except ValueError:
        print(f"UNKNOWN_POST_BASELINE_VERSION: {value}")
        sys.exit(2)
    selected = tuple(item for item in qualifications if item.version == version)
    if not selected:
        print(f"UNKNOWN_POST_BASELINE_VERSION: v{version}")
        sys.exit(2)
    return selected


def main() -> None:
    arguments = parse_arguments()
    discovery = discover()
    if discovery.errors:
        print("POST-BASELINE METADATA: FAIL")
        for error in discovery.errors:
            print(f" - {error}")
        sys.exit(1)

    selected = select_qualifications(
        discovery.qualifications, arguments.audit_version
    )
    failures = 0
    for qualification in selected:
        completed = subprocess.run(
            [sys.executable, qualification.executable.path.name],
            cwd=qualification.directory,
            capture_output=True,
            check=False,
        )
        relative = qualification.executable.path.relative_to(
            qualification.directory.parents[3]
        )
        if completed.returncode != qualification.expected_exit_code:
            failures += 1
            print(
                f"{relative}: EXIT_CODE_MISMATCH "
                f"({completed.returncode} != {qualification.expected_exit_code})"
            )
        recorded = qualification.recorded_output.path.read_bytes()
        if completed.stdout != recorded:
            failures += 1
            print(
                f"{relative}: RECORDED_OUTPUT_MISMATCH "
                f"({sha256_bytes(completed.stdout)} != {sha256_bytes(recorded)})"
            )
        if completed.stderr:
            print(completed.stderr.decode(errors="replace").rstrip(), file=sys.stderr)
        if (
            completed.returncode == qualification.expected_exit_code
            and completed.stdout == recorded
        ):
            print(f"{relative}: PASS")

    if failures:
        print(f"POST-BASELINE STATE SPACE: FAIL ({failures} mismatches)")
        sys.exit(1)
    print(
        "POST-BASELINE STATE SPACE: PASS "
        f"({len(selected)} qualifications)"
    )


if __name__ == "__main__":
    main()
