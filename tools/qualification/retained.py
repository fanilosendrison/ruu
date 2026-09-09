"""Verify ADR-080 snapshot lineage and byte-identical retained projections."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from qualification.snapshot_authority import load as load_snapshot_authority

ROOT = Path(__file__).resolve().parents[2]
STATE_PATTERN = re.compile(r"^state-space-audit-v(\d+)\.(md|py|txt)$")
SOURCE_STATE_PATTERN = re.compile(
    r"(?i)^state-space-audit-v(\d+)\.(md|py|txt)$"
)
SMOKE_PATTERN = re.compile(r"^git-.+-smoke-v\d+\.(sh|txt)$")
SOURCE_SMOKE_PATTERN = re.compile(r"^git-(.+)-smoke-v\d+\.(sh|txt)$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EXPECTED_KINDS = {
    "state-space-report",
    "state-space-executable",
    "state-space-recorded-output",
    "git-smoke-script",
    "git-smoke-recorded-output",
}
STATE_KINDS_BY_EXTENSION = {
    "md": "state-space-report",
    "py": "state-space-executable",
    "txt": "state-space-recorded-output",
}
SMOKE_KINDS_BY_EXTENSION = {
    "sh": "git-smoke-script",
    "txt": "git-smoke-recorded-output",
}


@dataclass(frozen=True)
class Verification:
    artifact_count: int
    registered_paths: frozenset[str]
    versions: frozenset[int]
    errors: tuple[str, ...]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative_path(value: str) -> Path | None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path


def _load_object(path: Path, label: str, errors: list[str]) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"{label}: invalid JSON: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: root must be an object")
        return None
    return {str(key): item for key, item in value.items()}


def _expected_path(
    original_value: str,
    kind: str,
    artifact_id: str,
    errors: list[str],
) -> tuple[str | None, int | None]:
    original_name = Path(original_value).name
    state_match = SOURCE_STATE_PATTERN.fullmatch(original_name)
    if state_match:
        version = int(state_match.group(1))
        extension = state_match.group(2).lower()
        if kind != STATE_KINDS_BY_EXTENSION[extension]:
            errors.append(f"lineage: kind/path mismatch for {artifact_id}")
        return (
            f"qualification/state-space/v{version:03d}/{original_name.lower()}",
            version,
        )

    smoke_match = SOURCE_SMOKE_PATTERN.fullmatch(original_name)
    if smoke_match:
        extension = smoke_match.group(2)
        if kind != SMOKE_KINDS_BY_EXTENSION[extension]:
            errors.append(f"lineage: kind/path mismatch for {artifact_id}")
        return (
            f"qualification/git-smoke/{smoke_match.group(1)}/{original_name.lower()}",
            None,
        )

    errors.append(f"lineage: unsupported original path for {artifact_id}")
    return None, None


def verify_lineage(root: Path = ROOT) -> Verification:
    qualification = root / "qualification"
    snapshot = qualification / "releases" / "adr-080-flat"
    lineage_path = qualification / "lineage" / "lineage-v2.json"
    source_lineage = snapshot / "QUALIFICATION-LINEAGE.json"
    errors: list[str] = []
    authority = load_snapshot_authority(source_lineage, errors)
    expected_versions = set(authority.versions)
    data = _load_object(lineage_path, "lineage", errors)
    if data is None:
        return Verification(0, frozenset(), authority.versions, tuple(errors))

    if data.get("$schema") != "lineage-v2.schema.json":
        errors.append("lineage: unexpected schema reference")
    if data.get("schema_version") != 2:
        errors.append("lineage: schema_version must be 2")

    retention_value = data.get("retention_policy")
    retention = retention_value if isinstance(retention_value, dict) else {}
    if not isinstance(retention_value, dict):
        errors.append("lineage: retention_policy must be an object")
    required_policy = {
        "snapshot_is_immutable": True,
        "active_artifact_bytes_must_match_snapshot": True,
        "missing_historical_baseline_is_never_a_pass": True,
    }
    for key, expected_value in required_policy.items():
        if retention.get(key) is not expected_value:
            errors.append(f"lineage: retention policy {key} must be true")
    if "qualification/releases" not in retention.get(
        "active_discovery_excludes", []
    ):
        errors.append("lineage: immutable releases must be excluded from active discovery")
    if retention.get("retained_discovery_excludes") != [
        "qualification/state-space/post-baseline"
    ]:
        errors.append("lineage: post-baseline evidence must be excluded from retained discovery")

    snapshot_value = data.get("source_snapshot")
    snapshot_record = snapshot_value if isinstance(snapshot_value, dict) else {}
    if not isinstance(snapshot_value, dict):
        errors.append("lineage: source_snapshot must be an object")
    if snapshot_record.get("path") != "qualification/releases/adr-080-flat":
        errors.append("lineage: unexpected source snapshot path")
    if snapshot_record.get("lineage_path") != "QUALIFICATION-LINEAGE.json":
        errors.append("lineage: unexpected legacy lineage path")
    if snapshot_record.get("manifest_path") != "MANIFEST.sha256":
        errors.append("lineage: unexpected snapshot manifest path")
    snapshot_manifest = snapshot / "MANIFEST.sha256"
    if not snapshot_manifest.is_file():
        errors.append("lineage: snapshot manifest is missing")
    elif sha256(snapshot_manifest) != snapshot_record.get("manifest_sha256"):
        errors.append("lineage: snapshot manifest SHA mismatch")

    source_packages_value = data.get("source_packages")
    source_packages = (
        source_packages_value if isinstance(source_packages_value, dict) else {}
    )
    if not isinstance(source_packages_value, dict):
        errors.append("lineage: source_packages must be an object")
    elif source_packages != authority.sources:
        errors.append("lineage: source_packages differ from immutable snapshot authority")
    artifacts_value = data.get("artifacts")
    if not isinstance(artifacts_value, list):
        errors.append("lineage: artifacts must be an array")
        artifacts_value = []

    seen_ids: set[str] = set()
    seen_original: set[str] = set()
    seen_current: set[str] = set()
    state_roles: dict[int, set[str]] = defaultdict(set)

    for index, value in enumerate(artifacts_value):
        if not isinstance(value, dict):
            errors.append(f"lineage: artifact {index} must be an object")
            continue
        artifact = {str(key): item for key, item in value.items()}
        artifact_id = artifact.get("artifact_id")
        original_value = artifact.get("original_path")
        current_value = artifact.get("current_path")
        expected = artifact.get("sha256")
        kind = artifact.get("kind")
        source = artifact.get("source")
        label = artifact_id if isinstance(artifact_id, str) else f"artifact-{index}"

        if not isinstance(artifact_id, str) or not ARTIFACT_ID_PATTERN.fullmatch(
            artifact_id
        ):
            errors.append(f"lineage: invalid artifact ID {artifact_id}")
        elif artifact_id in seen_ids:
            errors.append(f"lineage: duplicate artifact ID {artifact_id}")
        else:
            seen_ids.add(artifact_id)
        if kind not in EXPECTED_KINDS:
            errors.append(f"lineage: invalid kind for {label}: {kind}")
        if artifact.get("status") != "RETAINED":
            errors.append(f"lineage: invalid status for {label}")
        if not isinstance(source, str) or source not in source_packages:
            errors.append(f"lineage: unknown source for {label}: {source}")
        if not isinstance(expected, str) or not SHA256_PATTERN.fullmatch(expected):
            errors.append(f"lineage: invalid SHA-256 for {label}")
            expected = ""
        if not isinstance(original_value, str) or not isinstance(current_value, str):
            errors.append(f"lineage: paths must be strings for {label}")
            continue

        snapshot_artifact = authority.artifacts.get(original_value)
        if snapshot_artifact is None:
            errors.append(f"lineage: artifact is absent from snapshot authority: {label}")
        else:
            if artifact_id != snapshot_artifact.artifact_id:
                errors.append(f"lineage: artifact ID differs from snapshot authority: {label}")
            if kind != snapshot_artifact.kind:
                errors.append(f"lineage: kind differs from snapshot authority: {label}")
            if source != snapshot_artifact.source:
                errors.append(f"lineage: source differs from snapshot authority: {label}")
            if expected != snapshot_artifact.sha256:
                errors.append(f"lineage: SHA differs from snapshot authority: {label}")

        expected_current, state_version = _expected_path(
            original_value, str(kind), label, errors
        )
        if current_value != expected_current:
            errors.append(f"lineage: retained path mismatch for {label}: {current_value}")
        if current_value.startswith("qualification/state-space/post-baseline/"):
            errors.append(
                f"lineage: post-baseline artifact cannot be snapshot-backed: {label}"
            )
        if original_value in seen_original:
            errors.append(f"lineage: duplicate original path {original_value}")
        seen_original.add(original_value)
        if current_value in seen_current:
            errors.append(f"lineage: duplicate current path {current_value}")
        seen_current.add(current_value)

        original_relative = safe_relative_path(original_value)
        current_relative = safe_relative_path(current_value)
        if original_relative is None or current_relative is None:
            errors.append(f"lineage: unsafe path in {label}")
            continue
        if len(original_relative.parts) != 1:
            errors.append(f"lineage: snapshot artifact must be a flat path: {label}")
        original = snapshot / original_relative
        current = root / current_relative
        for location, path in (("snapshot", original), ("active", current)):
            if path.is_symlink():
                errors.append(f"lineage: symlink {location} artifact {path}")
            elif not path.is_file():
                errors.append(f"lineage: missing {location} artifact {path}")
            elif sha256(path) != expected:
                errors.append(f"lineage: SHA mismatch for {location} artifact {path}")
        if state_version is not None:
            state_roles[state_version].add(str(kind))

    if seen_original != set(authority.artifacts):
        for path in sorted(set(authority.artifacts) - seen_original):
            errors.append(f"lineage: missing snapshot-authority artifact {path}")
        for path in sorted(seen_original - set(authority.artifacts)):
            errors.append(f"lineage: extra non-authoritative artifact {path}")

    expected_roles = {
        "state-space-report",
        "state-space-executable",
        "state-space-recorded-output",
    }
    if set(state_roles) != expected_versions:
        missing = ", ".join(
            f"v{value}" for value in sorted(expected_versions - set(state_roles))
        )
        extra = ", ".join(
            f"v{value}" for value in sorted(set(state_roles) - expected_versions)
        )
        errors.append(
            "lineage: retained state-space versions differ from snapshot lineage; "
            f"missing [{missing}], extra [{extra}]"
        )
    for version, roles in state_roles.items():
        if roles != expected_roles:
            errors.append(
                f"lineage: incomplete roles for state-space v{version}: {sorted(roles)}"
            )

    return Verification(
        artifact_count=len(seen_ids),
        registered_paths=frozenset(seen_current),
        versions=frozenset(expected_versions),
        errors=tuple(errors),
    )


def discover_artifacts(root: Path = ROOT) -> set[str]:
    qualification = root / "qualification"
    post_root = qualification / "state-space" / "post-baseline"
    discovered: set[str] = set()
    for path in (qualification / "state-space").rglob("*"):
        if not path.is_file() or post_root in path.parents:
            continue
        if STATE_PATTERN.fullmatch(path.name):
            discovered.add(path.relative_to(root).as_posix())
    for path in (qualification / "git-smoke").rglob("*"):
        if path.is_file() and SMOKE_PATTERN.fullmatch(path.name):
            discovered.add(path.relative_to(root).as_posix())
    return discovered


def snapshot_permission_errors(root: Path = ROOT) -> tuple[str, ...]:
    snapshot = root / "qualification" / "releases" / "adr-080-flat"
    errors: list[str] = []
    for path in (snapshot, *snapshot.rglob("*")):
        if path.is_symlink():
            errors.append(f"snapshot: symlink path {path.relative_to(root)}")
        if path.lstat().st_mode & 0o222:
            errors.append(f"snapshot: writable path {path.relative_to(root)}")
    return tuple(errors)
