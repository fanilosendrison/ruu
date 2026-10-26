#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date as calendar_date
from pathlib import Path
import re
import sys
from typing import Any

import yaml
from adr_metadata_migration import _migration_evidence_errors
from adr_metadata_profile import RELATION_TYPES, load_profile
from adr_metadata_rendering import render_index
from adr_metadata_validation import _derived_identity, _h1_name, _load_schemas
from proto_ring_adr_boundary import (
    AdrMetadataError, configured_profile_path, decision_body_bytes,
    h1_text as _h1, load_json, load_yaml, parse_adr, preserved_payload_bytes,
    relation_target_errors, repository_path, require_mapping as _require_mapping,
    require_string as _require_string, require_string_list as _require_string_list,
    schema_errors, sha256_hex,
)

ROOT = Path(__file__).resolve().parents[1]

def collect_errors(root: Path, *, check_generated: bool = True) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    try:
        profile = load_profile(root)
    except AdrMetadataError as error:
        return [str(error)]

    base_schema, overlay_schema, schema_load_errors = _load_schemas(root, profile)
    errors.extend(schema_load_errors)
    repository = profile["repository"]
    try:
        adr_directory = repository_path(root, repository["adr_directory"])
    except AdrMetadataError as error:
        return errors + [str(error)]
    filename_pattern = re.compile(repository["filename_pattern"])
    id_pattern = re.compile(repository["id_pattern"])
    id_width = repository["id_width"]
    separators = repository["h1_separators"]
    preferred_separator = repository["preferred_h1_separator"]
    preferred_from = repository["preferred_h1_from"]
    legacy_ids = set(profile["legacy"]["unstructured"])
    null_date_ids = set(profile["legacy"]["null_dates"])

    excluded_markdown = set(repository["non_adr_markdown"])
    paths = sorted(
        path
        for path in adr_directory.glob("*.md")
        if path.name not in excluded_markdown
    )
    records_by_id: dict[str, dict[str, Any]] = {}
    legacy_found: set[str] = set()
    numbers: list[int] = []

    for path in paths:
        prefix = path.relative_to(root).as_posix()
        try:
            derived_id, _filename_slug, number = _derived_identity(
                path, filename_pattern, id_width
            )
        except AdrMetadataError as error:
            errors.append(f"{prefix}: {error}")
            continue
        numbers.append(number)
        if derived_id in records_by_id:
            errors.append(f"duplicate ADR identity {derived_id}")
            continue

        try:
            data = path.read_bytes()
            body = decision_body_bytes(data)
            heading = _h1(data)
            h1_separator, h1_name = _h1_name(heading, derived_id, separators)
        except (OSError, UnicodeError, AdrMetadataError) as error:
            errors.append(f"{prefix}: {error}")
            continue

        record = {
            "id": derived_id,
            "path": path,
            "relative_path": prefix,
            "data": data,
            "body": body,
            "metadata": None,
        }
        records_by_id[derived_id] = record

        if derived_id in legacy_ids:
            legacy_found.add(derived_id)
            continue
        if not data.startswith(b"---\n"):
            errors.append(f"{prefix}: {derived_id} is unstructured but not allowlisted")
            continue

        try:
            metadata, parsed_body = parse_adr(path)
        except AdrMetadataError as error:
            errors.append(f"{prefix}: {error}")
            continue
        record["metadata"] = metadata
        record["body"] = parsed_body
        for error in schema_errors(metadata, base_schema, overlay_schema):
            errors.append(f"{prefix}: {error}")

        metadata_id = metadata.get("id")
        if metadata_id != derived_id:
            errors.append(
                f"{prefix}: metadata id {metadata_id!r} does not match {derived_id}"
            )
        elif not id_pattern.fullmatch(metadata_id):
            errors.append(f"{prefix}: metadata id violates repository.id_pattern")

        name = metadata.get("name")
        if isinstance(name, str) and name != h1_name:
            errors.append(
                f"{prefix}: H1 name {h1_name!r} does not equal metadata name {name!r}"
            )
        if number >= preferred_from and h1_separator != preferred_separator:
            errors.append(
                f"{prefix}: ADR-{number:03d} must use preferred H1 separator "
                f"{preferred_separator!r}"
            )

        actual_body_hash = sha256_hex(parsed_body)
        if metadata.get("decision_body_sha256") != actual_body_hash:
            errors.append(
                f"{prefix}: decision_body_sha256 mismatch; expected {actual_body_hash}"
            )

        decision_date = metadata.get("date")
        if decision_date is None and derived_id not in null_date_ids:
            errors.append(f"{prefix}: null date is not allowlisted for {derived_id}")
        if decision_date is not None and derived_id in null_date_ids:
            errors.append(f"{prefix}: stale legacy null_dates entry {derived_id}")
        if isinstance(decision_date, str):
            try:
                parsed_date = calendar_date.fromisoformat(decision_date)
            except ValueError:
                pass
            else:
                if parsed_date > calendar_date.today():
                    errors.append(f"{prefix}: future date {decision_date} is forbidden")

    all_ids = set(records_by_id)
    for adr_id in sorted(legacy_ids - legacy_found):
        errors.append(f"stale legacy unstructured entry {adr_id}")
    for adr_id in sorted(null_date_ids - all_ids):
        errors.append(f"stale legacy null_dates entry {adr_id}")

    if len(numbers) != len(set(numbers)):
        errors.append("duplicate ADR numbers")
    if numbers:
        expected_numbers = list(range(1, max(numbers) + 1))
        if sorted(numbers) != expected_numbers:
            errors.append(
                "ADR IDs must be contiguous from 1 through " + str(max(numbers))
            )

    for adr_id, record in sorted(records_by_id.items()):
        metadata = record["metadata"]
        if not isinstance(metadata, dict):
            continue
        relations = metadata.get("relations")
        if not isinstance(relations, dict):
            continue
        for relation_type in RELATION_TYPES:
            targets = relations.get(relation_type)
            if not isinstance(targets, list):
                continue
            for relation_error in relation_target_errors(
                source_id=adr_id,
                relation_type=relation_type,
                targets=targets,
                known_ids=all_ids,
            ):
                errors.append(f"{record['relative_path']}: {relation_error}")

    errors.extend(_migration_evidence_errors(root, profile, records_by_id))

    generated = profile["generated_index"]
    if check_generated and generated["required"]:
        try:
            expected_index = render_index(root)
            index_path = repository_path(root, generated["path"])
            actual_index = index_path.read_text(encoding="utf-8")
            if actual_index != expected_index:
                errors.append(
                    f"generated ADR index is stale; run {profile['commands']['render']}"
                )
        except (AdrMetadataError, OSError, UnicodeError) as error:
            errors.append(f"generated ADR index: {error}")
    return errors

def check_command(root: Path) -> int:
    errors = collect_errors(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"ADR metadata: FAILED ({len(errors)} errors)", file=sys.stderr)
        return 1
    profile, records = _structured_records_if_possible(root)
    legacy_count = len(profile["legacy"]["unstructured"])
    print(f"ADR metadata: OK ({len(records)} structured, {legacy_count} unstructured)")
    return 0

def _structured_records_if_possible(
    root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    profile = load_profile(root)
    adr_directory = repository_path(root, profile["repository"]["adr_directory"])
    records: list[dict[str, Any]] = []
    legacy_ids = set(profile["legacy"]["unstructured"])
    filename_pattern = re.compile(profile["repository"]["filename_pattern"])
    id_width = profile["repository"]["id_width"]
    for path in sorted(adr_directory.glob("adr-*.md")):
        adr_id, _, _ = _derived_identity(path, filename_pattern, id_width)
        if adr_id not in legacy_ids:
            metadata, body = parse_adr(path)
            records.append({"path": path, "metadata": metadata, "body": body})
    return profile, records

def render_command(root: Path) -> int:
    errors = collect_errors(root, check_generated=False)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ADR index rendering refused because source validation failed", file=sys.stderr)
        return 1
    try:
        profile = load_profile(root)
        rendered = render_index(root)
        output_path = repository_path(root, profile["generated_index"]["path"])
        output_path.write_text(rendered, encoding="utf-8", newline="\n")
    except (AdrMetadataError, OSError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Rendered {output_path.relative_to(root)}")
    return 0

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and render Ruu ADR metadata")
    parser.add_argument("command", choices=("check", "render"))
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    arguments = parse_args(argv)
    root = arguments.root.resolve()
    if arguments.command == "check":
        return check_command(root)
    return render_command(root)


if __name__ == "__main__":
    raise SystemExit(main())
