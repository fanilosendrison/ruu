#!/usr/bin/env python3
"""Strict Ruu adapter for the bound native proto-ring executable."""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Final

import yaml

from proto_ring_execution_custody import (
    ProviderExecutionCustodyError,
    executable_snapshot,
    provider_process_environment as _provider_process_environment,
)
from proto_ring_result_validation import ProtoRingResultShapeError, validate_result
from proto_ring_source_realization import (
    SourceRealizationError,
    git_environment as _git_environment,
    source_is_exact as _source_realization_is_exact,
)
from proto_ring_structured_value import StructuredValueError
from proto_ring_structured_value import decode as _decode_structured_value
from proto_ring_structured_value import encode as _encode_structured_value

PROTO_RING_REPOSITORY: Final = "fanilosendrison/proto-ring"
PROTO_RING_TRANSPORT_VERSION: Final = 1
PROTO_RING_BINDING_ID: Final = "proto_ring_executable"
_BINDINGS_PATH: Final = Path("docs/repository-governance/ruu-governance-bindings.md")
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")


class ProtoRingExecutableError(RuntimeError):
    """The native provider cannot safely be used for this invocation."""

class ProtoRingControlledFailure(ProtoRingExecutableError):
    """A typed provider operation rejected semantically valid transport."""
    def __init__(self, category: str, stage: str | None, detail: str) -> None:
        location = f" at {stage}" if stage else ""
        super().__init__(f"{category}{location}: {detail}")
        self.category = category
        self.stage = stage
        self.detail = detail


@dataclass(frozen=True)
class ExecutableProviderBinding:
    repository: str
    commit: str

@dataclass(frozen=True)
class Realization:
    binary: Path
    manifest: dict[str, Any]


def _frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ProtoRingExecutableError(f"cannot read provider binding: {error}") from error
    if not text.startswith("---\n"):
        raise ProtoRingExecutableError("provider binding has no YAML frontmatter")
    try:
        _opening, frontmatter, _body = text.split("---\n", 2)
        value = yaml.safe_load(frontmatter)
    except (ValueError, yaml.YAMLError) as error:
        raise ProtoRingExecutableError("provider binding frontmatter is invalid") from error
    if not isinstance(value, dict):
        raise ProtoRingExecutableError("provider binding frontmatter must be a mapping")
    return value


def load_executable_provider_binding(root: Path) -> ExecutableProviderBinding:
    """Load only the authoritative executable binding from the local registry."""

    value = _frontmatter(root / _BINDINGS_PATH)
    try:
        bindings = value["governance_bindings"]["bindings"]
        binding = bindings[PROTO_RING_BINDING_ID]
        kind = binding["kind"]
        scope_kind = binding["scope"]["kind"]
        identity = binding["identity"]
        repository = identity["repository"]
        commit = identity["commit"]
        authority = binding["authority"]
    except (KeyError, TypeError) as error:
        raise ProtoRingExecutableError(
            f"Governance Binding Registry requires {PROTO_RING_BINDING_ID}"
        ) from error
    if kind != "executable_provider" or scope_kind != "logical_provider":
        raise ProtoRingExecutableError("proto_ring_executable has an invalid kind or scope")
    if repository != PROTO_RING_REPOSITORY:
        raise ProtoRingExecutableError(
            f"proto_ring_executable repository must be {PROTO_RING_REPOSITORY}"
        )
    if not isinstance(commit, str) or _HEX40.fullmatch(commit) is None:
        raise ProtoRingExecutableError("proto_ring_executable commit must be 40 lowercase hex")
    if authority != {
        "responsibility": "executable_provider_binding",
        "source": "governance_binding_registry",
    }:
        raise ProtoRingExecutableError("proto_ring_executable authority is invalid")
    return ExecutableProviderBinding(repository=repository, commit=commit)


def cache_base() -> Path:
    configured = os.environ.get("XDG_CACHE_HOME")
    if configured:
        candidate = Path(configured)
        if not candidate.is_absolute():
            raise ProtoRingExecutableError("XDG_CACHE_HOME must be absolute when set")
        return candidate
    return Path.home() / ".cache"


def managed_provider_root(binding: ExecutableProviderBinding) -> Path:
    return cache_base() / "ruu" / "proto-ring" / binding.commit


def _binary_path(provider_root: Path) -> Path:
    name = "proto-ring-compat.exe" if os.name == "nt" else "proto-ring-compat"
    return provider_root / "build" / "release" / name


def _canonical_json(value: object) -> bytes:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtoRingExecutableError("provider realization manifest is invalid") from error
    if not isinstance(value, dict):
        raise ProtoRingExecutableError("provider realization manifest must be an object")
    if _canonical_json(value) != path.read_bytes():
        raise ProtoRingExecutableError("provider realization manifest is not canonical JSON")
    return value


def _source_is_exact(source: Path, binding: ExecutableProviderBinding) -> None:
    try:
        _source_realization_is_exact(source, binding)
    except SourceRealizationError as error:
        raise ProtoRingExecutableError(str(error)) from error


def _has_transport_version(value: object) -> bool:
    return type(value) is int and value == PROTO_RING_TRANSPORT_VERSION


def _validate_identity(response: dict[str, Any], binding: ExecutableProviderBinding) -> None:
    value = response.get("value")
    if (
        not isinstance(value, dict)
        or not _has_transport_version(value.get("transport_version"))
        or value
        != {
            "source_repository": binding.repository,
            "source_commit": binding.commit,
            "transport_version": PROTO_RING_TRANSPORT_VERSION,
        }
    ):
        raise ProtoRingExecutableError("engine.identity does not match the provider binding")


def _require_external_provider_root(root: Path, provider_root: Path) -> None:
    repository = root.resolve()
    realization = provider_root.resolve()
    if realization == repository or repository in realization.parents:
        raise ProtoRingExecutableError("provider realization must remain outside Ruu")


def _require_external_provider_path(
    root: Path, provider_root: Path, candidate: Path
) -> None:
    try:
        relative = candidate.relative_to(provider_root)
    except ValueError as error:
        raise ProtoRingExecutableError("provider path escapes its realization root") from error
    current = provider_root
    for component in relative.parts:
        current /= component
        if current.is_symlink():
            raise ProtoRingExecutableError("provider realization contains a symlink")
    repository = root.resolve()
    resolved = candidate.resolve()
    if resolved == repository or repository in resolved.parents:
        raise ProtoRingExecutableError("provider path resolves inside Ruu")


def realized_provider(root: Path) -> Realization:
    """Resolve and validate an already prepared provider; never build implicitly."""

    binding = load_executable_provider_binding(root)
    provider_root = managed_provider_root(binding)
    _require_external_provider_root(root, provider_root)
    source = provider_root / "source"
    manifest_path = provider_root / "realization.json"
    binary = _binary_path(provider_root)
    for candidate in (source, manifest_path, binary):
        _require_external_provider_path(root, provider_root, candidate)
    manifest = _read_manifest(manifest_path)
    if not binary.is_file():
        raise ProtoRingExecutableError(
            "native proto-ring provider is absent; run tools/prepare-proto-ring-provider.py"
        )
    if (
        not _has_transport_version(manifest.get("transport_version"))
        or {
            key: manifest.get(key)
            for key in ("repository", "commit", "transport_version")
        }
        != {
            "repository": binding.repository,
            "commit": binding.commit,
            "transport_version": PROTO_RING_TRANSPORT_VERSION,
        }
    ):
        raise ProtoRingExecutableError("provider realization manifest does not match the binding")
    expected_digest = manifest.get("binary_sha256")
    if not isinstance(expected_digest, str):
        raise ProtoRingExecutableError(
            "provider realization binary digest does not match manifest"
        )
    try:
        with executable_snapshot(binary, expected_digest) as snapshot:
            _source_is_exact(source, binding)
            identity = _invoke_binary(snapshot, "engine.identity", {}, binding=None)
            _validate_identity(identity, binding)
    except ProviderExecutionCustodyError as error:
        raise ProtoRingExecutableError(str(error)) from error
    return Realization(binary=binary, manifest=manifest)


def _response_for(
    binary: Path, operation: str, payload: dict[str, Any]
) -> tuple[int, bytes, bytes]:
    request = {
        "transport_version": PROTO_RING_TRANSPORT_VERSION,
        "operation": operation,
        "input": payload,
    }
    completed = subprocess.run(
        [str(binary)],
        input=_canonical_json(request),
        capture_output=True,
        check=False,
        env=_provider_process_environment(),
    )
    return completed.returncode, completed.stdout, completed.stderr


def _decode_response(
    operation: str, returncode: int, stdout: bytes, stderr: bytes
) -> dict[str, Any]:
    if returncode == 70:
        raise ProtoRingExecutableError("provider failed internally")
    try:
        lines = stdout.decode("utf-8").splitlines()
        if len(lines) != 1:
            raise ValueError("response count")
        response = json.loads(lines[0])
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        raise ProtoRingExecutableError("provider emitted an invalid compatibility response") from error
    if not isinstance(response, dict):
        raise ProtoRingExecutableError("provider response must be an object")
    outcome = response.get("outcome")
    if returncode == 0 and outcome == "result":
        if (
            not _has_transport_version(response.get("transport_version"))
            or response.get("operation") != operation
            or "value" not in response
        ):
            raise ProtoRingExecutableError("provider result response is malformed")
        return response
    if returncode == 0 and outcome == "controlled_failure":
        error = response.get("error")
        if (
            not _has_transport_version(response.get("transport_version"))
            or response.get("operation") != operation
            or not isinstance(error, dict)
            or not isinstance(error.get("category"), str)
            or not (error.get("stage") is None or isinstance(error.get("stage"), str))
            or not isinstance(error.get("detail"), str)
        ):
            raise ProtoRingExecutableError(
                "provider controlled-failure response is malformed"
            )
        return response
    if returncode == 2 and outcome == "transport_error":
        error = response.get("error")
        if not _has_transport_version(response.get("transport_version")) or error != {"category": "invalid_request"}:
            raise ProtoRingExecutableError("provider transport-error response is malformed")
        raise ProtoRingExecutableError("provider rejected the compatibility request")
    raise ProtoRingExecutableError("provider returned invalid compatibility exit semantics")


def _invoke_binary(
    binary: Path,
    operation: str,
    payload: dict[str, Any],
    binding: ExecutableProviderBinding | None,
) -> dict[str, Any]:
    response = _decode_response(operation, *_response_for(binary, operation, payload))
    if binding is not None and operation == "engine.identity":
        _validate_identity(response, binding)
    return response


def _verified_identity(binary: Path, binding: ExecutableProviderBinding) -> None:
    _validate_identity(_invoke_binary(binary, "engine.identity", {}, None), binding)


def invoke_compat(root: Path, operation: str, input: dict[str, Any]) -> dict[str, Any]:
    """Invoke one validated transport-v1 operation through the realized executable."""

    binding = load_executable_provider_binding(root)
    realization = realized_provider(root)
    try:
        with executable_snapshot(
            realization.binary, realization.manifest["binary_sha256"]
        ) as snapshot:
            _verified_identity(snapshot, binding)
            return _invoke_binary(snapshot, operation, input, binding)
    except ProviderExecutionCustodyError as error:
        raise ProtoRingExecutableError(str(error)) from error


def _validated_result(
    operation: str, input: dict[str, Any], value: object
) -> dict[str, Any]:
    try:
        return validate_result(operation, input, value)
    except ProtoRingResultShapeError as error:
        raise ProtoRingExecutableError(
            f"provider {operation} result is malformed: {error}"
        ) from error


def invoke_compat_result(
    root: Path, operation: str, input: dict[str, Any]
) -> dict[str, Any]:
    """Return a strict result value or raise a typed controlled failure."""

    response = invoke_compat(root, operation, input)
    if response["outcome"] == "controlled_failure":
        error = response["error"]
        raise ProtoRingControlledFailure(
            error["category"], error.get("stage"), error["detail"]
        )
    return _validated_result(operation, input, response["value"])


def _invoke_test_binary(
    binary: Path, operation: str, input: dict[str, Any]
) -> dict[str, Any]:
    """Test-only low-level boundary with an explicit binary path."""

    return _invoke_binary(binary, operation, input, None)


def _invoke_test_binary_result(
    binary: Path, operation: str, input: dict[str, Any]
) -> dict[str, Any]:
    """Test-only strict result handling for fake executable qualification."""

    response = _invoke_test_binary(binary, operation, input)
    if response["outcome"] == "controlled_failure":
        error = response["error"]
        raise ProtoRingControlledFailure(
            error["category"], error.get("stage"), error["detail"]
        )
    return _validated_result(operation, input, response["value"])


def to_structured_value(value: object) -> dict[str, Any]:
    try:
        return _encode_structured_value(value)
    except StructuredValueError as error:
        raise ProtoRingExecutableError(str(error)) from error


def from_structured_value(value: object) -> object:
    try:
        return _decode_structured_value(value)
    except StructuredValueError as error:
        raise ProtoRingExecutableError(str(error)) from error
