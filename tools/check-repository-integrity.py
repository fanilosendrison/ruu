#!/usr/bin/env python3
"""Ruu-owned binding to the canonical proto-ring Repository Integrity substrate."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Mapping

from proto_ring.repository_integrity import (
    CommandObligation,
    IntegrityProfile,
    IntegrityVerdict,
    ObligationStatus,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]


def _relative_paths(root: Path, pattern: str) -> tuple[str, ...]:
    return tuple(
        path.relative_to(root).as_posix()
        for path in sorted(root.glob(pattern))
        if path.is_file()
    )


def canonical_obligations(root: Path = ROOT) -> tuple[CommandObligation, ...]:
    """Return Ruu's ordered, repository-owned current-state obligations."""

    python = sys.executable
    maintained_python = (
        *_relative_paths(root, "tools/*.py"),
        *_relative_paths(root, "tools/qualification/*.py"),
        *_relative_paths(root, "tools/tests/*.py"),
    )
    json_documents = (
        *_relative_paths(root, "docs/adr/schemas/*.json"),
        "qualification/lineage/lineage-v2.schema.json",
        "qualification/state-space/post-baseline/qualification-metadata-v1.schema.json",
    )

    obligations = [
        CommandObligation(
            name="Maintained Python syntax",
            argv=(python, "-m", "py_compile", *maintained_python),
        )
    ]
    obligations.extend(
        CommandObligation(
            name=f"JSON syntax: {path}",
            argv=(python, "-m", "json.tool", path),
        )
        for path in json_documents
    )
    obligations.extend(
        (
            CommandObligation(
                name="ADR metadata tests",
                argv=(python, "tools/tests/test-adr-metadata.py"),
            ),
            CommandObligation(
                name="Projection Integrity tests",
                argv=(python, "tools/tests/test-projection-integrity.py"),
            ),
            CommandObligation(
                name="Historical qualification tests",
                argv=(python, "tools/tests/test-historical-qualification.py"),
            ),
            CommandObligation(
                name="Repository Integrity binding tests",
                argv=(python, "tools/tests/test-repository-integrity.py"),
            ),
            CommandObligation(
                name="Qualification infrastructure tests",
                argv=(python, "tools/tests/test-qualification-infrastructure.py"),
            ),
            CommandObligation(
                name="ADR metadata check",
                argv=(python, "tools/adr-metadata.py", "check"),
            ),
            CommandObligation(
                name="Accepted ADR body immutability",
                argv=(
                    python,
                    "-m",
                    "proto_ring.accepted_adr_body",
                ),
            ),
            CommandObligation(
                name="Shared Governance Provider binding",
                argv=(
                    python,
                    "-m",
                    "proto_ring.shared_governance_provider",
                ),
            ),
            CommandObligation(
                name="Retained lineage currentness",
                argv=(python, "tools/generate-qualification-lineage.py"),
            ),
            CommandObligation(
                name="Active manifest currentness",
                argv=(python, "tools/generate-current-manifest.py"),
            ),
            CommandObligation(
                name="Qualification layout",
                argv=(python, "tools/verify-qualification-layout.py"),
            ),
            CommandObligation(
                name="Markdown links",
                argv=(python, "tools/verify-markdown-links.py"),
            ),
            CommandObligation(
                name="Git whitespace",
                argv=(python, "tools/check-git-whitespace.py"),
            ),
        )
    )
    return tuple(obligations)


def integrity_profile(root: Path = ROOT) -> IntegrityProfile:
    """Bind generic evaluation to Ruu's local validation membership."""

    return IntegrityProfile(
        obligations=canonical_obligations(root),
        continue_after_non_satisfied=True,
    )


def run(repository: Path = ROOT, *, env: Mapping[str, str]) -> int:
    result = evaluate(repository, integrity_profile(repository), env=env)

    for obligation in result.obligations:
        if obligation.status is ObligationStatus.SATISFIED:
            continue
        detail = f": {obligation.detail}" if obligation.detail else ""
        print(
            f"ERROR: {obligation.name}: {obligation.status.value}{detail}",
            file=sys.stderr,
        )
    for error in result.errors:
        print(f"ERROR: repository integrity substrate: {error}", file=sys.stderr)

    if result.verdict is not IntegrityVerdict.PASS:
        print("repository integrity: FAILED", file=sys.stderr)
        return 1

    print("repository integrity: OK")
    return 0


def main() -> int:
    return run(ROOT, env=os.environ)


if __name__ == "__main__":
    raise SystemExit(main())
