"""Validate Ruu's immutable ADR metadata migration evidence."""

from pathlib import Path
import subprocess
from typing import Any

from proto_ring_adr_boundary import (
    AdrMetadataError, decision_body_bytes, load_yaml, preserved_payload_bytes,
    repository_path, require_mapping as _require_mapping, sha256_hex,
)

def _git_baseline_blob(root: Path, commit: str, relative_path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{relative_path}"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise AdrMetadataError(
            f"baseline commit {commit} cannot provide {relative_path}: {detail}"
        )
    return result.stdout

def _baseline_ancestor_result(root: Path, baseline: str):
    return subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", baseline, "HEAD"],
        check=False,
        capture_output=True,
    )


def _migration_evidence_errors(
    root: Path,
    profile: dict[str, Any],
    records_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    section = profile["migration_evidence"]
    if not section["required"]:
        return []
    errors: list[str] = []
    try:
        path = repository_path(root, section["path"])
        evidence = _require_mapping(load_yaml(path), section["path"])
    except AdrMetadataError as error:
        return [f"migration evidence: {error}"]

    baseline = section["baseline_commit"]
    if evidence.get("schema_version") != 1:
        errors.append("migration evidence must use schema_version 1")
    if evidence.get("profile_version") != profile["profile_version"]:
        errors.append("migration evidence profile_version mismatch")
    if evidence.get("baseline_commit") != baseline:
        errors.append("migration evidence baseline_commit does not match profile")

    ancestor = _baseline_ancestor_result(root, baseline)
    if ancestor.returncode != 0:
        detail = ancestor.stderr.decode("utf-8", errors="replace").strip()
        errors.append(
            f"migration baseline commit {baseline} is unavailable or not an ancestor"
            + (f": {detail}" if detail else "")
        )

    expected = set(section["ids"])
    entries = evidence.get("records")
    if not isinstance(entries, list):
        return errors + ["migration evidence records must be a list"]

    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("migration evidence record must be a mapping")
            continue
        adr_id = entry.get("id")
        if not isinstance(adr_id, str):
            errors.append("migration evidence record id must be a string")
            continue
        if adr_id in seen:
            errors.append(f"duplicate migration evidence record {adr_id}")
        seen.add(adr_id)
        record = records_by_id.get(adr_id)
        if record is None:
            errors.append(f"migration evidence references missing {adr_id}")
            continue
        if entry.get("path") != record["relative_path"]:
            errors.append(f"migration evidence {adr_id} path mismatch")
            continue

        try:
            baseline_bytes = _git_baseline_blob(
                root, baseline, record["relative_path"]
            )
            baseline_payload = preserved_payload_bytes(baseline_bytes)
            current_payload = preserved_payload_bytes(record["data"])
            baseline_body = decision_body_bytes(baseline_bytes)
        except AdrMetadataError as error:
            errors.append(f"migration evidence {adr_id}: {error}")
            continue

        if current_payload != baseline_payload:
            errors.append(
                f"migration evidence {adr_id}: H1-to-EOF payload differs from baseline"
            )

        expected_hashes = {
            "baseline_file_sha256": sha256_hex(baseline_bytes),
            "baseline_payload_sha256": sha256_hex(baseline_payload),
            "migrated_payload_sha256": sha256_hex(current_payload),
            "before_decision_body_sha256": sha256_hex(baseline_body),
            "after_decision_body_sha256": sha256_hex(record["body"]),
        }
        for field, expected_hash in expected_hashes.items():
            if entry.get(field) != expected_hash:
                errors.append(
                    f"migration evidence {adr_id} {field} does not match actual bytes"
                )

    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        if missing:
            errors.append("migration evidence missing IDs: " + ", ".join(missing))
        if extra:
            errors.append("migration evidence has unexpected IDs: " + ", ".join(extra))
    return errors
