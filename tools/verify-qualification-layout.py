#!/usr/bin/env python3
"""Verify retained ADR-080 evidence and registered post-baseline evidence."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from qualification.postbaseline import discover as discover_postbaseline
from qualification.retained import (
    discover_artifacts as discover_retained_artifacts,
)
from qualification.retained import sha256, snapshot_permission_errors, verify_lineage

ROOT = Path(__file__).resolve().parent.parent
QUALIFICATION = ROOT / "qualification"
SNAPSHOT = QUALIFICATION / "releases" / "adr-080-flat"
SNAPSHOT_MANIFEST_COPY = QUALIFICATION / "manifests" / "adr-080-flat.sha256"
CURRENT_MANIFEST = QUALIFICATION / "manifests" / "current.sha256"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def safe_relative_path(value: str) -> Path | None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path


def verify_manifest(root: Path, manifest: Path, errors: list[str]) -> set[str]:
    registered: set[str] = set()
    ordered_paths: list[str] = []
    try:
        lines = manifest.read_text().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        errors.append(f"{manifest}: unreadable manifest: {error}")
        return registered
    for line_number, line in enumerate(lines, start=1):
        if not line:
            continue
        try:
            expected, value = line.split("  ", maxsplit=1)
        except ValueError:
            errors.append(f"{manifest}: malformed line {line_number}")
            continue
        if not SHA256_PATTERN.fullmatch(expected):
            errors.append(f"{manifest}: invalid SHA-256 on line {line_number}")
        relative = safe_relative_path(value)
        if relative is None:
            errors.append(f"{manifest}: unsafe path {value}")
            continue
        if value in registered:
            errors.append(f"{manifest}: duplicate path {value}")
        registered.add(value)
        ordered_paths.append(value)
        path = root / relative
        if path.is_symlink():
            errors.append(f"{manifest}: symlink path {value}")
        elif not path.is_file():
            errors.append(f"{manifest}: missing {value}")
        elif sha256(path) != expected:
            errors.append(f"{manifest}: SHA mismatch {value}")
    if ordered_paths != sorted(ordered_paths):
        errors.append(f"{manifest}: paths are not sorted")
    return registered


def discover_active_manifest_files() -> set[str]:
    discovered: set[str] = set()
    release_root = QUALIFICATION / "releases"
    for path in ROOT.rglob("*"):
        if not path.is_file() and not path.is_symlink():
            continue
        if release_root in path.parents or ".git" in path.parts:
            continue
        if path == CURRENT_MANIFEST or path.name == ".DS_Store":
            continue
        if "__pycache__" in path.parts:
            continue
        discovered.add(path.relative_to(ROOT).as_posix())
    return discovered


def verify_continuity(
    retained_versions: set[int], post_versions: list[int], errors: list[str]
) -> None:
    if not retained_versions:
        errors.append("state-space continuity: retained version set is empty")
        return
    retained_last = max(retained_versions)
    for version in post_versions:
        if version <= retained_last:
            errors.append(
                f"state-space continuity: post-baseline v{version} collides with "
                "retained history"
            )
    all_versions = retained_versions | set(post_versions)
    expected = set(range(min(retained_versions), max(all_versions) + 1))
    if all_versions != expected:
        missing = ", ".join(f"v{value}" for value in sorted(expected - all_versions))
        errors.append(f"state-space continuity: missing {missing}")


def verify_snapshot(errors: list[str]) -> int:
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
            for line in (
                snapshot_verifier.stdout + snapshot_verifier.stderr
            ).splitlines()
        )

    snapshot_manifest = SNAPSHOT / "MANIFEST.sha256"
    snapshot_paths = verify_manifest(SNAPSHOT, snapshot_manifest, errors)
    if not SNAPSHOT_MANIFEST_COPY.is_file():
        errors.append("snapshot: active manifest copy is missing")
    elif SNAPSHOT_MANIFEST_COPY.read_bytes() != snapshot_manifest.read_bytes():
        errors.append("snapshot: active manifest copy differs from immutable snapshot")
    errors.extend(snapshot_permission_errors(ROOT))
    return len(snapshot_paths)


def main() -> None:
    errors: list[str] = []
    snapshot_manifest_count = verify_snapshot(errors)

    retained = verify_lineage(ROOT)
    errors.extend(retained.errors)
    retained_discovered = discover_retained_artifacts(ROOT)
    if retained_discovered != retained.registered_paths:
        for path in sorted(retained_discovered - retained.registered_paths):
            errors.append(f"retained discovery: unregistered artifact {path}")
        for path in sorted(retained.registered_paths - retained_discovered):
            errors.append(f"retained discovery: undiscovered artifact {path}")

    postbaseline = discover_postbaseline(ROOT)
    errors.extend(postbaseline.errors)
    post_versions = [item.version for item in postbaseline.qualifications]
    verify_continuity(set(retained.versions), post_versions, errors)

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
    print(f"snapshot manifest entries: {snapshot_manifest_count}")
    print(f"retained registered artifacts: {retained.artifact_count}")
    print(
        "post-baseline registered qualifications: "
        f"{len(postbaseline.qualifications)}"
    )
    print(f"active manifest entries: {len(current_manifest_paths)}")


if __name__ == "__main__":
    main()
