#!/usr/bin/env python3
"""Verify the immutable ADR-080 snapshot and the organized active evidence."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUALIFICATION = ROOT / "qualification"
SNAPSHOT = QUALIFICATION / "releases" / "adr-080-flat"
LINEAGE = QUALIFICATION / "lineage" / "lineage-v2.json"
CURRENT_MANIFEST = QUALIFICATION / "manifests" / "current.sha256"
STATE_PATTERN = re.compile(r"^state-space-audit-v(\d+)\.(md|py|txt)$")
SMOKE_PATTERN = re.compile(r"^git-.+-smoke-v\d+\.(sh|txt)$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EXPECTED_KINDS = {
    "state-space-report",
    "state-space-executable",
    "state-space-recorded-output",
    "git-smoke-script",
    "git-smoke-recorded-output",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative_path(value: str) -> Path | None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path


def verify_manifest(root: Path, manifest: Path, errors: list[str]) -> set[str]:
    registered: set[str] = set()
    for line_number, line in enumerate(manifest.read_text().splitlines(), start=1):
        if not line:
            continue
        try:
            expected, value = line.split("  ", maxsplit=1)
        except ValueError:
            errors.append(f"{manifest}: malformed line {line_number}")
            continue
        relative = safe_relative_path(value)
        if relative is None:
            errors.append(f"{manifest}: unsafe path {value}")
            continue
        if value in registered:
            errors.append(f"{manifest}: duplicate path {value}")
        registered.add(value)
        path = root / relative
        if not path.is_file():
            errors.append(f"{manifest}: missing {value}")
        elif sha256(path) != expected:
            errors.append(f"{manifest}: SHA mismatch {value}")
    return registered


def verify_lineage(errors: list[str]) -> tuple[int, set[str]]:
    data = json.loads(LINEAGE.read_text())
    if data.get("$schema") != "lineage-v2.schema.json":
        errors.append("lineage: unexpected schema reference")
    if data.get("schema_version") != 2:
        errors.append("lineage: schema_version must be 2")

    retention = data.get("retention_policy", {})
    required_policy = {
        "snapshot_is_immutable": True,
        "active_artifact_bytes_must_match_snapshot": True,
        "missing_historical_baseline_is_never_a_pass": True,
    }
    for key, expected_value in required_policy.items():
        if retention.get(key) is not expected_value:
            errors.append(f"lineage: retention policy {key} must be true")
    if "qualification/releases" not in retention.get("active_discovery_excludes", []):
        errors.append("lineage: immutable releases must be excluded from active discovery")

    snapshot_record = data.get("source_snapshot", {})
    if snapshot_record.get("path") != "qualification/releases/adr-080-flat":
        errors.append("lineage: unexpected source snapshot path")
    if snapshot_record.get("lineage_path") != "QUALIFICATION-LINEAGE.json":
        errors.append("lineage: unexpected legacy lineage path")
    if snapshot_record.get("manifest_path") != "MANIFEST.sha256":
        errors.append("lineage: unexpected snapshot manifest path")
    snapshot_manifest = SNAPSHOT / snapshot_record.get("manifest_path", "")
    if not snapshot_manifest.is_file():
        errors.append("lineage: snapshot manifest is missing")
    elif sha256(snapshot_manifest) != snapshot_record.get("manifest_sha256"):
        errors.append("lineage: snapshot manifest SHA mismatch")

    source_packages = data.get("source_packages", {})
    seen_ids: set[str] = set()
    seen_original: set[str] = set()
    seen_current: set[str] = set()
    state_roles: dict[int, set[str]] = defaultdict(set)

    for artifact in data.get("artifacts", []):
        artifact_id = artifact.get("artifact_id", "")
        original_value = artifact.get("original_path", "")
        current_value = artifact.get("current_path", "")
        expected = artifact.get("sha256", "")
        kind = artifact.get("kind", "")
        source = artifact.get("source", "")

        if not ARTIFACT_ID_PATTERN.fullmatch(artifact_id):
            errors.append(f"lineage: invalid artifact ID {artifact_id}")
        if artifact_id in seen_ids:
            errors.append(f"lineage: duplicate artifact ID {artifact_id}")
        seen_ids.add(artifact_id)
        if kind not in EXPECTED_KINDS:
            errors.append(f"lineage: invalid kind for {artifact_id}: {kind}")
        if artifact.get("status") != "RETAINED":
            errors.append(f"lineage: invalid status for {artifact_id}")
        if source not in source_packages:
            errors.append(f"lineage: unknown source for {artifact_id}: {source}")
        if not SHA256_PATTERN.fullmatch(expected):
            errors.append(f"lineage: invalid SHA-256 for {artifact_id}")
        if not current_value.startswith((
            "qualification/state-space/",
            "qualification/git-smoke/",
        )):
            errors.append(f"lineage: invalid active path for {artifact_id}")
        if original_value in seen_original:
            errors.append(f"lineage: duplicate original path {original_value}")
        seen_original.add(original_value)
        if current_value in seen_current:
            errors.append(f"lineage: duplicate current path {current_value}")
        seen_current.add(current_value)

        original_relative = safe_relative_path(original_value)
        current_relative = safe_relative_path(current_value)
        if original_relative is None or current_relative is None:
            errors.append(f"lineage: unsafe path in {artifact_id}")
            continue

        original = SNAPSHOT / original_relative
        current = ROOT / current_relative
        for label, path in (("snapshot", original), ("active", current)):
            if not path.is_file():
                errors.append(f"lineage: missing {label} artifact {path}")
            elif sha256(path) != expected:
                errors.append(f"lineage: SHA mismatch for {label} artifact {path}")

        state_match = STATE_PATTERN.match(Path(current_value).name)
        if state_match:
            version = int(state_match.group(1))
            state_roles[version].add(artifact.get("kind", ""))

    expected_roles = {
        "state-space-report",
        "state-space-executable",
        "state-space-recorded-output",
    }
    if sorted(state_roles) != list(range(2, 46)):
        errors.append(f"lineage: state-space versions are not contiguous v2..v45")
    for version, roles in state_roles.items():
        if roles != expected_roles:
            errors.append(f"lineage: incomplete roles for state-space v{version}: {sorted(roles)}")

    return len(seen_ids), seen_current


def discover_active_artifacts() -> set[str]:
    discovered: set[str] = set()
    for root in (QUALIFICATION / "state-space", QUALIFICATION / "git-smoke"):
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            name = path.name
            if STATE_PATTERN.match(name) or SMOKE_PATTERN.match(name):
                discovered.add(path.relative_to(ROOT).as_posix())
    return discovered


def verify_snapshot_permissions(errors: list[str]) -> None:
    for path in SNAPSHOT.rglob("*"):
        if path.stat().st_mode & 0o222:
            errors.append(f"snapshot: writable path {path.relative_to(ROOT)}")


def discover_active_manifest_files() -> set[str]:
    discovered: set[str] = set()
    release_root = QUALIFICATION / "releases"
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if release_root in path.parents or ".git" in path.parts:
            continue
        if path == CURRENT_MANIFEST or path.name == ".DS_Store":
            continue
        if "__pycache__" in path.parts:
            continue
        discovered.add(path.relative_to(ROOT).as_posix())
    return discovered


def main() -> None:
    errors: list[str] = []

    snapshot_verifier = subprocess.run(
        [sys.executable, "verify-qualification-lineage.py"],
        cwd=SNAPSHOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if snapshot_verifier.returncode != 0:
        errors.append("snapshot: legacy lineage verifier failed")
        errors.extend(
            f"snapshot: {line}"
            for line in snapshot_verifier.stdout.splitlines()
        )

    snapshot_manifest_paths = verify_manifest(
        SNAPSHOT, SNAPSHOT / "MANIFEST.sha256", errors
    )
    verify_snapshot_permissions(errors)
    artifact_count, registered = verify_lineage(errors)
    discovered = discover_active_artifacts()
    if discovered != registered:
        for path in sorted(discovered - registered):
            errors.append(f"active discovery: unregistered artifact {path}")
        for path in sorted(registered - discovered):
            errors.append(f"active discovery: undiscovered artifact {path}")

    current_manifest_paths: set[str] = set()
    if not CURRENT_MANIFEST.is_file():
        errors.append("active layout: current manifest is missing")
    else:
        current_manifest_paths = verify_manifest(ROOT, CURRENT_MANIFEST, errors)
        active_files = discover_active_manifest_files()
        for path in sorted(active_files - current_manifest_paths):
            errors.append(f"active manifest: unregistered file {path}")
        for path in sorted(current_manifest_paths - active_files):
            errors.append(f"active manifest: undiscovered file {path}")

    if errors:
        print("QUALIFICATION LAYOUT: FAIL")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)

    print("QUALIFICATION LAYOUT: PASS")
    print(f"snapshot manifest entries: {len(snapshot_manifest_paths)}")
    print(f"active registered artifacts: {artifact_count}")
    print(f"active manifest entries: {len(current_manifest_paths)}")


if __name__ == "__main__":
    main()
