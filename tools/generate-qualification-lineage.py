#!/usr/bin/env python3
"""Generate retained qualification lineage from the immutable ADR-080 snapshot."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUALIFICATION = ROOT / "qualification"
SNAPSHOT = QUALIFICATION / "releases" / "adr-080-flat"
SOURCE_LINEAGE = SNAPSHOT / "QUALIFICATION-LINEAGE.json"
OUTPUT = QUALIFICATION / "lineage" / "lineage-v2.json"
STATE_PATTERN = re.compile(r"(?i)^state-space-audit-v(\d+)\.(md|py|txt)$")
SMOKE_PATTERN = re.compile(r"^git-(.+)-smoke-v\d+\.(sh|txt)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def active_path(original_path: str) -> str:
    name = Path(original_path).name
    state_match = STATE_PATTERN.match(name)
    if state_match:
        version = int(state_match.group(1))
        return f"qualification/state-space/v{version:03d}/{name.lower()}"

    smoke_match = SMOKE_PATTERN.match(name)
    if smoke_match:
        family = smoke_match.group(1)
        return f"qualification/git-smoke/{family}/{name.lower()}"

    raise ValueError(f"unsupported qualification artifact path: {original_path}")


def artifact_record(
    artifact_id: str,
    kind: str,
    source: str,
    record: dict[str, str],
) -> dict[str, str]:
    original_path = record["path"]
    current_path = active_path(original_path)
    expected_sha256 = record["sha256"]

    original = SNAPSHOT / original_path
    current = ROOT / current_path
    for label, path in (("snapshot", original), ("active", current)):
        if not path.is_file():
            raise FileNotFoundError(f"{label} artifact missing: {path}")
        actual = sha256(path)
        if actual != expected_sha256:
            raise ValueError(
                f"{label} artifact hash mismatch for {path}: "
                f"{actual} != {expected_sha256}"
            )

    return {
        "artifact_id": artifact_id,
        "kind": kind,
        "status": "RETAINED",
        "source": source,
        "original_path": original_path,
        "current_path": current_path,
        "sha256": expected_sha256,
    }


def main() -> None:
    source = json.loads(SOURCE_LINEAGE.read_text())
    artifacts: list[dict[str, str]] = []

    state_roles = {
        "report": "state-space-report",
        "executable": "state-space-executable",
        "recorded_output": "state-space-recorded-output",
    }
    for audit in source["state_space_audits"]:
        version = int(audit["version"])
        for role, kind in state_roles.items():
            artifacts.append(
                artifact_record(
                    f"state-space-v{version:03d}-{role.replace('_', '-')}",
                    kind,
                    audit["source"],
                    audit[role],
                )
            )

    smoke_roles = {
        "script": "git-smoke-script",
        "recorded_output": "git-smoke-recorded-output",
    }
    for smoke in source["git_smokes"]:
        for role, kind in smoke_roles.items():
            record = smoke.get(role)
            if record is None:
                continue
            artifacts.append(
                artifact_record(
                    f"{smoke['id']}-{role.replace('_', '-')}",
                    kind,
                    smoke["source"],
                    record,
                )
            )

    output = {
        "$schema": "lineage-v2.schema.json",
        "schema_version": 2,
        "generated_for": "Ruu retained layout derived from the immutable ADR-080 flat package",
        "generated_on": "2026-09-08",
        "source_snapshot": {
            "path": "qualification/releases/adr-080-flat",
            "lineage_path": "QUALIFICATION-LINEAGE.json",
            "manifest_path": "MANIFEST.sha256",
            "manifest_sha256": sha256(SNAPSHOT / "MANIFEST.sha256"),
        },
        "retention_policy": {
            "snapshot_is_immutable": True,
            "active_artifact_bytes_must_match_snapshot": True,
            "active_discovery_excludes": ["qualification/releases"],
            "retained_discovery_excludes": [
                "qualification/state-space/post-baseline"
            ],
            "missing_historical_baseline_is_never_a_pass": True,
        },
        "source_packages": source["sources"],
        "artifacts": sorted(artifacts, key=lambda item: item["artifact_id"]),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"generated {OUTPUT.relative_to(ROOT)} with {len(artifacts)} artifacts")


if __name__ == "__main__":
    main()
