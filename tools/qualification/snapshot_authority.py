"""Parse immutable ADR-080 lineage into retained-artifact expectations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SnapshotArtifact:
    artifact_id: str
    kind: str
    source: str
    sha256: str


@dataclass(frozen=True)
class SnapshotAuthority:
    sources: dict[str, object]
    artifacts: dict[str, SnapshotArtifact]
    versions: frozenset[int]


def _load_object(path: Path, errors: list[str]) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"snapshot source lineage: invalid JSON: {error}")
        return None
    if not isinstance(value, dict):
        errors.append("snapshot source lineage: root must be an object")
        return None
    return {str(key): item for key, item in value.items()}


def _register_artifact(
    artifacts: dict[str, SnapshotArtifact],
    record_value: object,
    artifact_id: str,
    kind: str,
    source: object,
    errors: list[str],
) -> None:
    if not isinstance(record_value, dict):
        errors.append(f"snapshot source lineage: missing record for {artifact_id}")
        return
    path = record_value.get("path")
    expected_hash = record_value.get("sha256")
    if not isinstance(path, str) or not isinstance(expected_hash, str):
        errors.append(f"snapshot source lineage: invalid record for {artifact_id}")
        return
    if path in artifacts:
        errors.append(f"snapshot source lineage: duplicate artifact path {path}")
        return
    if not isinstance(source, str):
        errors.append(f"snapshot source lineage: invalid source for {artifact_id}")
        return
    artifacts[path] = SnapshotArtifact(artifact_id, kind, source, expected_hash)


def load(path: Path, errors: list[str]) -> SnapshotAuthority:
    data = _load_object(path, errors)
    if data is None:
        return SnapshotAuthority({}, {}, frozenset())
    sources_value = data.get("sources")
    sources = sources_value if isinstance(sources_value, dict) else {}
    if not isinstance(sources_value, dict):
        errors.append("snapshot source lineage: sources must be an object")

    artifacts: dict[str, SnapshotArtifact] = {}
    version_list: list[int] = []
    audits = data.get("state_space_audits")
    if not isinstance(audits, list):
        errors.append("snapshot source lineage: state_space_audits must be an array")
        audits = []
    state_roles = {
        "report": "state-space-report",
        "executable": "state-space-executable",
        "recorded_output": "state-space-recorded-output",
    }
    for index, item in enumerate(audits):
        if not isinstance(item, dict):
            errors.append(f"snapshot source lineage: audit {index} must be an object")
            continue
        version = item.get("version")
        if not isinstance(version, int) or isinstance(version, bool):
            errors.append(f"snapshot source lineage: audit {index} has invalid version")
            continue
        version_list.append(version)
        for role, kind in state_roles.items():
            _register_artifact(
                artifacts,
                item.get(role),
                f"state-space-v{version:03d}-{role.replace('_', '-')}",
                kind,
                item.get("source"),
                errors,
            )

    smokes = data.get("git_smokes")
    if not isinstance(smokes, list):
        errors.append("snapshot source lineage: git_smokes must be an array")
        smokes = []
    smoke_roles = {
        "script": "git-smoke-script",
        "recorded_output": "git-smoke-recorded-output",
    }
    for index, item in enumerate(smokes):
        if not isinstance(item, dict):
            errors.append(f"snapshot source lineage: smoke {index} must be an object")
            continue
        smoke_id = item.get("id")
        if not isinstance(smoke_id, str):
            errors.append(f"snapshot source lineage: smoke {index} has invalid ID")
            continue
        for role, kind in smoke_roles.items():
            if item.get(role) is not None:
                _register_artifact(
                    artifacts,
                    item.get(role),
                    f"{smoke_id}-{role.replace('_', '-')}",
                    kind,
                    item.get("source"),
                    errors,
                )

    versions = set(version_list)
    if len(versions) != len(version_list):
        errors.append("snapshot source lineage: duplicate state-space version")
    if versions:
        expected = set(range(min(versions), max(versions) + 1))
        if versions != expected:
            missing = ", ".join(f"v{value}" for value in sorted(expected - versions))
            errors.append(f"snapshot source lineage: non-contiguous versions; missing {missing}")
    return SnapshotAuthority(
        {str(key): value for key, value in sources.items()},
        artifacts,
        frozenset(versions),
    )
