"""Native Proto-Ring boundary for generic ADR metadata operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from proto_ring_executable_binding import (
    ProtoRingExecutableError,
    from_structured_value,
    invoke_compat_result,
    to_structured_value,
)

ROOT = Path(__file__).resolve().parents[1]


class AdrMetadataError(ValueError):
    """A native generic ADR operation rejected the requested value."""


def _native(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return invoke_compat_result(ROOT, operation, payload)
    except ProtoRingExecutableError as error:
        raise AdrMetadataError(str(error)) from error


def _source_bytes(source: Path | bytes) -> bytes:
    return source.read_bytes() if isinstance(source, Path) else source


def _parse(mode: str, source: Path | bytes) -> dict[str, Any]:
    return _native(
        "adr-metadata.parse",
        {"mode": mode, "bytes_hex": _source_bytes(source).hex()},
    )


def configured_profile_path(root: Path) -> Path:
    value = invoke_compat_result(
        ROOT,
        "canonical-adr.resolve",
        {"mode": "configured_profile_path", "repository": str(root)},
    )
    return root / value["relative_path"]


def load_yaml(source: Path | bytes) -> object:
    return from_structured_value(_parse("load_yaml", source)["structured"])


def load_json(source: Path | bytes) -> object:
    return from_structured_value(_parse("load_json", source)["structured"])


def parse_adr(path: Path) -> tuple[dict[str, Any], bytes]:
    value = _parse("parse_adr", path)
    metadata = from_structured_value(value["metadata"])
    if not isinstance(metadata, dict):
        raise AdrMetadataError("ADR metadata must be a mapping")
    return metadata, bytes.fromhex(value["body_hex"])


def decision_body_bytes(data: bytes) -> bytes:
    return bytes.fromhex(_parse("decision_body", data)["body_hex"])


def h1_text(data: bytes) -> str:
    return _parse("h1", data)["text"]


def preserved_payload_bytes(data: bytes) -> bytes:
    return bytes.fromhex(_parse("preserved_payload", data)["payload_hex"])


def sha256_hex(data: bytes) -> str:
    return _parse("sha256", data)["sha256"]


def repository_path(root: Path, relative: object) -> Path:
    try:
        value = invoke_compat_result(
            ROOT,
            "adr-metadata.repository-path",
            {"repository": str(root), "relative": relative},
        )
    except ProtoRingExecutableError as error:
        raise AdrMetadataError(str(error)) from error
    return root.resolve() / value["relative"]


def _validation(mode: str, **values: object) -> dict[str, Any]:
    payload = {"mode": mode}
    payload.update({name: to_structured_value(value) for name, value in values.items()})
    return _native("adr-metadata.validation", payload)


def require_mapping(value: object, location: str) -> dict[str, Any]:
    try:
        decoded = from_structured_value(
            _validation("require_mapping", value=value)["value"]
        )
    except (AdrMetadataError, ProtoRingExecutableError) as error:
        raise AdrMetadataError(f"{location}: {error}") from error
    if not isinstance(decoded, dict):
        raise AdrMetadataError(f"{location}: required mapping result is invalid")
    return decoded


def require_string(value: object, location: str) -> str:
    try:
        return _validation("require_string", value=value)["text"]
    except AdrMetadataError as error:
        raise AdrMetadataError(f"{location}: {error}") from error


def require_string_list(value: object, location: str) -> list[str]:
    try:
        return _validation("require_string_list", value=value)["items"]
    except AdrMetadataError as error:
        raise AdrMetadataError(f"{location}: {error}") from error


def relation_target_errors(
    *, source_id: str, relation_type: str, targets: list[str], known_ids: set[str]
) -> list[str]:
    value = _validation(
        "relation_target_errors",
        source_id=source_id,
        relation_type=relation_type,
        targets=targets,
        known_ids=sorted(known_ids),
    )
    return [
        f"{relation_type}: self reference"
        if error["category"] == "self_reference"
        else f"{relation_type}: missing target {error['target']}"
        for error in value["errors"]
    ]


def schema_errors(value: object, schema: object, overlay_schema: object) -> list[str]:
    result = _validation(
        "schema_errors",
        value=value,
        schema=schema,
        overlay_schema=overlay_schema,
    )
    return [
        f"{error['schema']} schema is invalid: error at {error['path']}"
        for error in result["errors"]
    ]
