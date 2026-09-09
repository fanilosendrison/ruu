#!/usr/bin/env python3
"""Replay a state-space audit only against its exact admitted package baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "qualification" / "releases" / "adr-080-flat"
SOURCE_LINEAGE = SNAPSHOT / "QUALIFICATION-LINEAGE.json"
SNAPSHOT_COMPATIBLE_SOURCES = {"adr073", "adr080_pre_restoration"}
SNAPSHOT_COMPATIBLE_EXCEPTION_VERSIONS = {2}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_member_path(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts


def extract_zip(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            if not safe_member_path(member.filename):
                raise ValueError(f"unsafe archive path: {member.filename}")
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"archive symlink is not allowed: {member.filename}")
        package.extractall(destination)


def extract_tar(archive: Path, destination: Path) -> None:
    with tarfile.open(archive) as package:
        members = package.getmembers()
        for member in members:
            if not safe_member_path(member.name):
                raise ValueError(f"unsafe archive path: {member.name}")
            if member.issym() or member.islnk() or member.isdev():
                raise ValueError(f"unsafe archive member: {member.name}")
        package.extractall(destination, members=members)


def extract_archive(archive: Path, destination: Path) -> None:
    if zipfile.is_zipfile(archive):
        extract_zip(archive, destination)
        return
    if tarfile.is_tarfile(archive):
        extract_tar(archive, destination)
        return
    raise ValueError("baseline archive must be ZIP or TAR")


def find_unique(root: Path, name: str) -> Path:
    matches = list(root.rglob(name))
    if len(matches) != 1:
        raise ValueError(f"expected one {name}, found {len(matches)}")
    return matches[0]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "audit_version",
        help="historical audit version, or latest for the retained checkpoint",
    )
    parser.add_argument(
        "--baseline-archive",
        type=Path,
        help="exact historical source package required for snapshot-scoped audits",
    )
    return parser.parse_args()


def select_audit(
    lineage: dict[str, object], requested: str
) -> dict[str, object]:
    audits_value = lineage.get("state_space_audits")
    if not isinstance(audits_value, list):
        print("INVALID_HISTORICAL_LINEAGE: state_space_audits is missing")
        sys.exit(2)
    audits: list[dict[str, object]] = []
    for index, item in enumerate(audits_value):
        if not isinstance(item, dict):
            print(f"INVALID_HISTORICAL_LINEAGE: audit {index} must be an object")
            sys.exit(2)
        version = item.get("version")
        if not isinstance(version, int) or isinstance(version, bool):
            print(f"INVALID_HISTORICAL_LINEAGE: audit {index} has invalid version")
            sys.exit(2)
        audits.append({str(key): value for key, value in item.items()})
    versions = sorted(item["version"] for item in audits)
    if len(versions) != len(set(versions)):
        print("INVALID_HISTORICAL_LINEAGE: duplicate state-space version")
        sys.exit(2)
    if not versions:
        print("INVALID_HISTORICAL_LINEAGE: no state-space versions")
        sys.exit(2)
    if requested == "latest":
        version = versions[-1]
    else:
        try:
            version = int(requested)
        except ValueError:
            print(f"UNKNOWN_HISTORICAL_VERSION: {requested}")
            sys.exit(2)
    audit = next((item for item in audits if item.get("version") == version), None)
    if audit is None:
        print(f"UNKNOWN_HISTORICAL_VERSION: v{version}")
        sys.exit(2)
    return audit


def snapshot_compatible(audit: dict[str, object]) -> bool:
    version = audit.get("version")
    return (
        version in SNAPSHOT_COMPATIBLE_EXCEPTION_VERSIONS
        or audit.get("source") in SNAPSHOT_COMPATIBLE_SOURCES
    )


def audit_artifact(
    audit: dict[str, object], role: str, version: int
) -> tuple[str, str]:
    value = audit.get(role)
    if not isinstance(value, dict):
        raise ValueError(f"missing {role} for v{version}")
    path = value.get("path")
    expected_hash = value.get("sha256")
    if not isinstance(path, str) or not isinstance(expected_hash, str):
        raise ValueError(f"invalid {role} for v{version}")
    if not SHA256_PATTERN.fullmatch(expected_hash):
        raise ValueError(f"invalid {role} SHA-256 for v{version}")
    return path, expected_hash


def replay(
    script: Path,
    expected_script_hash: str,
    recorded_output: Path,
    expected_output_hash: str,
) -> int:
    for role, path, expected_hash in (
        ("executable", script, expected_script_hash),
        ("recorded output", recorded_output, expected_output_hash),
    ):
        if path.is_symlink() or not path.is_file():
            print(f"HISTORICAL_ARTIFACT_MISSING: {role} {path}")
            return 6
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            print(
                f"HISTORICAL_ARTIFACT_HASH_MISMATCH: {role} "
                f"{actual_hash} != {expected_hash}"
            )
            return 6

    completed = subprocess.run(
        [sys.executable, script.name],
        cwd=script.parent,
        capture_output=True,
        check=False,
    )
    sys.stdout.buffer.write(completed.stdout)
    sys.stderr.buffer.write(completed.stderr)
    if completed.returncode != 0:
        print(f"HISTORICAL_REPLAY_EXIT_MISMATCH: {completed.returncode} != 0")
        return 1
    expected_output = recorded_output.read_bytes()
    if completed.stdout != expected_output:
        print(
            "HISTORICAL_RECORDED_OUTPUT_MISMATCH: "
            f"{hashlib.sha256(completed.stdout).hexdigest()} != "
            f"{expected_output_hash}"
        )
        return 1
    return 0


def main() -> None:
    arguments = parse_arguments()
    try:
        lineage_value = json.loads(SOURCE_LINEAGE.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"INVALID_HISTORICAL_LINEAGE: {error}")
        sys.exit(2)
    if not isinstance(lineage_value, dict):
        print("INVALID_HISTORICAL_LINEAGE: root must be an object")
        sys.exit(2)
    lineage = {str(key): value for key, value in lineage_value.items()}
    audit = select_audit(lineage, arguments.audit_version)
    version = audit.get("version")
    source_id = audit.get("source")
    if not isinstance(version, int) or not isinstance(source_id, str):
        print("INVALID_HISTORICAL_LINEAGE: audit version/source is invalid")
        sys.exit(2)
    try:
        script_name, script_hash = audit_artifact(audit, "executable", version)
        output_name, output_hash = audit_artifact(audit, "recorded_output", version)
    except ValueError as error:
        print(f"INVALID_HISTORICAL_LINEAGE: {error}")
        sys.exit(2)

    if arguments.baseline_archive is None:
        if not snapshot_compatible(audit):
            print(
                "NON_REPLAYABLE_MISSING_BASELINE: "
                f"v{version} requires source package {source_id}"
            )
            sys.exit(3)
        script = SNAPSHOT / script_name
        recorded_output = SNAPSHOT / output_name
        sys.exit(replay(script, script_hash, recorded_output, output_hash))

    archive = arguments.baseline_archive.resolve()
    if not archive.is_file():
        print(f"NON_REPLAYABLE_MISSING_BASELINE: {archive}")
        sys.exit(3)

    sources = lineage.get("sources")
    if not isinstance(sources, dict) or not isinstance(sources.get(source_id), dict):
        print(f"INVALID_HISTORICAL_LINEAGE: missing source {source_id}")
        sys.exit(2)
    source_record = sources[source_id]
    expected_hash = source_record.get("package_sha256")
    if not isinstance(expected_hash, str) or not SHA256_PATTERN.fullmatch(expected_hash):
        print(f"INVALID_HISTORICAL_LINEAGE: invalid package SHA for {source_id}")
        sys.exit(2)
    actual_hash = sha256(archive)
    if actual_hash != expected_hash:
        print(
            "BASELINE_HASH_MISMATCH: "
            f"{actual_hash} != {expected_hash} ({source_id})"
        )
        sys.exit(4)

    with tempfile.TemporaryDirectory(prefix="ruu-qualification-replay-") as temporary:
        extracted = Path(temporary)
        try:
            extract_archive(archive, extracted)
            script = find_unique(extracted, script_name)
            recorded_output = find_unique(extracted, output_name)
        except ValueError as error:
            print(f"BASELINE_EXTRACTION_FAILED: {error}")
            sys.exit(5)
        sys.exit(replay(script, script_hash, recorded_output, output_hash))


if __name__ == "__main__":
    main()
