"""Validate canonical ADR identities and schema projections."""

import json
from pathlib import Path
import re
from typing import Any

from proto_ring_adr_boundary import AdrMetadataError, repository_path, sha256_hex

def _h1_name(heading: str, adr_id: str, separators: list[str]) -> tuple[str, str]:
    matches = [separator for separator in separators if heading.startswith(adr_id + separator)]
    if len(matches) != 1:
        raise AdrMetadataError(
            f"H1 must use {adr_id} followed by one allowed separator, found {heading!r}"
        )
    separator = matches[0]
    name = heading[len(adr_id + separator) :]
    if not name:
        raise AdrMetadataError("H1 decision name must not be empty")
    return separator, name

def _derived_identity(
    path: Path, filename_pattern: re.Pattern[str], id_width: int
) -> tuple[str, str, int]:
    match = filename_pattern.fullmatch(path.name)
    if match is None:
        raise AdrMetadataError("filename does not match repository.filename_pattern")
    number_text = match.group("number")
    slug = match.group("slug")
    if len(number_text) != id_width:
        raise AdrMetadataError(f"filename number must use exactly {id_width} digits")
    number = int(number_text)
    if number < 1:
        raise AdrMetadataError("ADR number must be positive")
    return f"ADR-{number_text}", slug, number

def _load_schemas(
    root: Path, profile: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    errors: list[str] = []
    canonical = profile["canonical_schema"]
    try:
        vendored_path = repository_path(root, canonical["vendored_path"])
        vendored_bytes = vendored_path.read_bytes()
    except (AdrMetadataError, OSError) as error:
        return {}, {}, [f"canonical schema: {error}"]

    actual_hash = sha256_hex(vendored_bytes)
    if actual_hash != canonical["sha256"]:
        errors.append(
            "vendored canonical schema SHA-256 mismatch: "
            f"expected {canonical['sha256']}, found {actual_hash}"
        )
    try:
        base = json.loads(vendored_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"vendored canonical schema is invalid JSON: {error}")
        base = {}
    if not isinstance(base, dict):
        errors.append("vendored canonical schema must be a JSON object")
        base = {}
    if base.get("$id") != canonical["id"]:
        errors.append(
            "vendored canonical schema $id mismatch: "
            f"expected {canonical['id']}, found {base.get('$id')}"
        )

    try:
        overlay_path = repository_path(root, profile["local_overlay"]["path"])
        overlay_bytes = overlay_path.read_bytes()
        overlay = json.loads(overlay_bytes.decode("utf-8"))
    except (AdrMetadataError, OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"local overlay: {error}")
        overlay_bytes = b""
        overlay = {}
    if not isinstance(overlay, dict):
        errors.append("local overlay schema must be a JSON object")
        overlay = {}
    overlay_hash = sha256_hex(overlay_bytes)
    if overlay_hash != profile["local_overlay"]["sha256"]:
        errors.append(
            "local overlay SHA-256 mismatch: expected "
            f"{profile['local_overlay']['sha256']}, found {overlay_hash}"
        )
    if not overlay:
        errors.append("local overlay must be a non-empty JSON Schema")
    if overlay.get("$id") != profile["local_overlay"]["id"]:
        errors.append(
            "local overlay $id mismatch: expected "
            f"{profile['local_overlay']['id']}, found {overlay.get('$id')}"
        )

    properties = overlay.get("properties")
    required = overlay.get("required")
    if not isinstance(properties, dict):
        properties = {}
    if not isinstance(required, list):
        required = []
    expected_constraints = {
        "adr_profile_version": ("const", profile["profile_version"]),
        "domain": ("const", profile["repository"]["domain"]),
        "id": ("pattern", profile["repository"]["id_pattern"]),
    }
    for field, (keyword, expected) in expected_constraints.items():
        constraint = properties.get(field)
        if not isinstance(constraint, dict) or constraint.get(keyword) != expected:
            errors.append(f"local overlay {field} constraint mismatch")
        if field not in required:
            errors.append(f"local overlay must require {field}")
    return base, overlay, errors
