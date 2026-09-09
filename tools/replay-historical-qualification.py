#!/usr/bin/env python3
"""Replay a state-space audit only against its exact admitted package baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
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
CURRENT_SNAPSHOT_VERSIONS = {2, *range(38, 46)}


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
    parser.add_argument("audit_version", type=int, choices=range(2, 46))
    parser.add_argument(
        "--baseline-archive",
        type=Path,
        help="exact historical source package required for snapshot-scoped audits",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    lineage = json.loads(SOURCE_LINEAGE.read_text())
    audit = next(
        item
        for item in lineage["state_space_audits"]
        if item["version"] == arguments.audit_version
    )
    script_name = audit["executable"]["path"]

    if arguments.baseline_archive is None:
        if arguments.audit_version not in CURRENT_SNAPSHOT_VERSIONS:
            print(
                "NON_REPLAYABLE_MISSING_BASELINE: "
                f"v{arguments.audit_version} requires source package {audit['source']}"
            )
            sys.exit(3)
        script = SNAPSHOT / script_name
        completed = subprocess.run(
            [sys.executable, script.name], cwd=SNAPSHOT, check=False
        )
        sys.exit(completed.returncode)

    archive = arguments.baseline_archive.resolve()
    if not archive.is_file():
        print(f"NON_REPLAYABLE_MISSING_BASELINE: {archive}")
        sys.exit(3)

    source_record = lineage["sources"][audit["source"]]
    expected_hash = source_record["package_sha256"]
    actual_hash = sha256(archive)
    if actual_hash != expected_hash:
        print(
            "BASELINE_HASH_MISMATCH: "
            f"{actual_hash} != {expected_hash} ({audit['source']})"
        )
        sys.exit(4)

    with tempfile.TemporaryDirectory(prefix="ruu-qualification-replay-") as temporary:
        extracted = Path(temporary)
        try:
            extract_archive(archive, extracted)
            script = find_unique(extracted, script_name)
        except ValueError as error:
            print(f"BASELINE_EXTRACTION_FAILED: {error}")
            sys.exit(5)
        completed = subprocess.run(
            [sys.executable, script.name], cwd=script.parent, check=False
        )
        sys.exit(completed.returncode)


if __name__ == "__main__":
    main()
