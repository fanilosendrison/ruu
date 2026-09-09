"""Discover and validate post-ADR-080 state-space qualification metadata."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POST_BASELINE_ROOT = ROOT / "qualification" / "state-space" / "post-baseline"
SCHEMA = POST_BASELINE_ROOT / "qualification-metadata-v1.schema.json"
METADATA_NAME = "qualification-metadata.json"
SCHEMA_REFERENCE = "../qualification-metadata-v1.schema.json"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_FILENAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
DIRECTORY_PATTERN = re.compile(r"^v(\d{3,})$")
STATE_ARTIFACT_PATTERN = re.compile(
    r"^state-space-audit-v(\d+)\.(md|py|txt)$"
)
METADATA_KEYS = {
    "$schema",
    "schema_version",
    "qualification_id",
    "qualification_kind",
    "provenance",
    "baseline",
    "version",
    "artifacts",
    "supporting_artifacts",
    "replay",
}
PRIMARY_ROLES = {"report", "executable", "recorded_output"}


@dataclass(frozen=True)
class Artifact:
    path: Path
    expected_sha256: str


@dataclass(frozen=True)
class Qualification:
    qualification_id: str
    version: int
    directory: Path
    report: Artifact
    executable: Artifact
    recorded_output: Artifact
    supporting_artifacts: tuple[Artifact, ...]
    expected_exit_code: int


@dataclass(frozen=True)
class Discovery:
    qualifications: tuple[Qualification, ...]
    registered_paths: frozenset[str]
    errors: tuple[str, ...]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _safe_relative_path(value: str) -> Path | None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or len(path.parts) != 1:
        return None
    return path


def _exact_keys(
    value: dict[str, object],
    expected: set[str],
    label: str,
    errors: list[str],
) -> bool:
    actual = set(value)
    if actual == expected:
        return True
    errors.append(
        f"{label}: keys must be exactly {', '.join(sorted(expected))}; "
        f"found {', '.join(sorted(actual))}"
    )
    return False


def _artifact(
    value: object,
    role: str,
    directory: Path,
    metadata_label: str,
    root: Path,
    errors: list[str],
    registered: set[str],
) -> Artifact | None:
    label = f"{metadata_label}: {role}"
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    record = {str(key): item for key, item in value.items()}
    if not _exact_keys(record, {"path", "sha256"}, label, errors):
        return None
    path_value = record.get("path")
    expected = record.get("sha256")
    if not isinstance(path_value, str):
        errors.append(f"{label} path must be a string")
        return None
    relative = _safe_relative_path(path_value)
    if relative is None or not ARTIFACT_FILENAME_PATTERN.fullmatch(path_value):
        errors.append(f"{label} path must be one safe lowercase local filename")
        return None
    if not isinstance(expected, str) or not SHA256_PATTERN.fullmatch(expected):
        errors.append(f"{label} has an invalid SHA-256")
        return None

    path = directory / relative
    registered.add(_relative(path, root))
    if path.is_symlink():
        errors.append(f"{metadata_label}: {role} artifact must not be a symlink")
    elif not path.is_file():
        errors.append(f"{metadata_label}: missing {role} artifact {path_value}")
    elif sha256(path) != expected:
        errors.append(f"{metadata_label}: SHA mismatch for {role} artifact {path_value}")
    return Artifact(path=path, expected_sha256=expected)


def _metadata_object(path: Path, errors: list[str]) -> dict[str, object] | None:
    label = path.as_posix()
    try:
        value = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"{label}: invalid metadata: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: metadata must be an object")
        return None
    return {str(key): item for key, item in value.items()}


def discover(root: Path = ROOT) -> Discovery:
    post_root = root / "qualification" / "state-space" / "post-baseline"
    schema = post_root / SCHEMA.name
    errors: list[str] = []
    registered: set[str] = set()
    qualifications: list[Qualification] = []
    seen_ids: set[str] = set()
    seen_versions: set[int] = set()

    if schema.is_symlink():
        errors.append("post-baseline: qualification metadata schema must not be a symlink")
    elif not schema.is_file():
        errors.append("post-baseline: qualification metadata schema is missing")
    if not post_root.is_dir():
        return Discovery(tuple(), frozenset(), tuple(errors))

    for metadata_path in sorted(post_root.rglob(METADATA_NAME)):
        metadata_label = _relative(metadata_path, root)
        registered.add(metadata_label)
        local_error_count = len(errors)
        if metadata_path.is_symlink():
            errors.append(f"{metadata_label}: metadata must not be a symlink")
            continue
        metadata = _metadata_object(metadata_path, errors)
        if metadata is None:
            continue
        _exact_keys(metadata, METADATA_KEYS, metadata_label, errors)

        version_value = metadata.get("version")
        version = (
            version_value
            if isinstance(version_value, int) and not isinstance(version_value, bool)
            else None
        )
        if version is None or version < 1:
            errors.append(f"{metadata_label}: version must be a positive integer")
            continue
        if version in seen_versions:
            errors.append(f"{metadata_label}: duplicate post-baseline version v{version}")
        seen_versions.add(version)

        qualification_id = metadata.get("qualification_id")
        expected_id = f"state-space-v{version:03d}"
        if qualification_id != expected_id:
            errors.append(
                f"{metadata_label}: qualification_id must be {expected_id}"
            )
        elif qualification_id in seen_ids:
            errors.append(
                f"{metadata_label}: duplicate qualification ID {qualification_id}"
            )
        else:
            seen_ids.add(qualification_id)

        if metadata.get("$schema") != SCHEMA_REFERENCE:
            errors.append(f"{metadata_label}: unexpected schema reference")
        if metadata.get("schema_version") != 1:
            errors.append(f"{metadata_label}: schema_version must be 1")
        if metadata.get("qualification_kind") != "state-space":
            errors.append(f"{metadata_label}: qualification_kind must be state-space")
        if metadata.get("provenance") != "POST_BASELINE":
            errors.append(f"{metadata_label}: provenance must be POST_BASELINE")
        if metadata.get("baseline") != "ADR-080":
            errors.append(f"{metadata_label}: baseline must be ADR-080")

        directory_match = DIRECTORY_PATTERN.fullmatch(metadata_path.parent.name)
        if metadata_path.parent.parent != post_root or directory_match is None:
            errors.append(
                f"{metadata_label}: metadata directory must be "
                f"qualification/state-space/post-baseline/v{version:03d}"
            )
        elif int(directory_match.group(1)) != version:
            errors.append(f"{metadata_label}: directory version does not match metadata")

        artifacts_value = metadata.get("artifacts")
        artifacts: dict[str, object] = {}
        if not isinstance(artifacts_value, dict):
            errors.append(f"{metadata_label}: artifacts must be an object")
        else:
            artifacts = {str(key): item for key, item in artifacts_value.items()}
            if set(artifacts) != PRIMARY_ROLES:
                errors.append(
                    f"{metadata_label}: artifacts must contain exactly "
                    "executable, recorded_output, report"
                )

        primary = {
            role: _artifact(
                artifacts.get(role),
                role,
                metadata_path.parent,
                metadata_label,
                root,
                errors,
                registered,
            )
            for role in sorted(PRIMARY_ROLES)
            if role in artifacts
        }

        expected_names = {
            "report": f"state-space-audit-v{version}.md",
            "executable": f"state-space-audit-v{version}.py",
            "recorded_output": f"state-space-audit-v{version}.txt",
        }
        for role, expected_name in expected_names.items():
            artifact = primary.get(role)
            if artifact is not None and artifact.path.name != expected_name:
                errors.append(
                    f"{metadata_label}: {role} filename must be {expected_name}"
                )

        supporting: list[Artifact] = []
        supporting_value = metadata.get("supporting_artifacts")
        if not isinstance(supporting_value, list):
            errors.append(f"{metadata_label}: supporting_artifacts must be an array")
        else:
            for index, value in enumerate(supporting_value):
                artifact = _artifact(
                    value,
                    f"supporting_artifacts[{index}]",
                    metadata_path.parent,
                    metadata_label,
                    root,
                    errors,
                    registered,
                )
                if artifact is not None:
                    if STATE_ARTIFACT_PATTERN.fullmatch(artifact.path.name):
                        errors.append(
                            f"{metadata_label}: primary state-space artifacts "
                            "cannot be registered as supporting artifacts"
                        )
                    supporting.append(artifact)

        all_artifacts = [*primary.values(), *supporting]
        all_paths = [artifact.path for artifact in all_artifacts]
        if len(all_paths) != len(set(all_paths)):
            errors.append(f"{metadata_label}: duplicate artifact path")

        report = primary.get("report")
        executable = primary.get("executable")
        recorded_output = primary.get("recorded_output")
        if report is not None and report.path.is_file() and not report.path.is_symlink():
            try:
                heading = report.path.read_text().splitlines()[:1]
            except UnicodeDecodeError:
                errors.append(f"{metadata_label}: report is not valid UTF-8")
                heading = []
            expected_heading = f"# State-Space Audit v{version}"
            if not heading or not heading[0].startswith(expected_heading):
                errors.append(
                    f"{metadata_label}: report heading must start with {expected_heading}"
                )
        if executable is not None and executable.path.is_file():
            if executable.path.stat().st_mode & 0o111 == 0:
                errors.append(f"{metadata_label}: executable artifact is not executable")

        replay_value = metadata.get("replay")
        expected_exit_code = -1
        if not isinstance(replay_value, dict):
            errors.append(f"{metadata_label}: replay must be an object")
        else:
            replay = {str(key): item for key, item in replay_value.items()}
            _exact_keys(
                replay,
                {"expected_exit_code", "runner", "stdout_sha256"},
                f"{metadata_label}: replay",
                errors,
            )
            if replay.get("runner") != "python3":
                errors.append(f"{metadata_label}: replay runner must be python3")
            if replay.get("expected_exit_code") != 0:
                errors.append(f"{metadata_label}: expected_exit_code must be 0")
            else:
                expected_exit_code = 0
            stdout_hash = replay.get("stdout_sha256")
            if not isinstance(stdout_hash, str) or not SHA256_PATTERN.fullmatch(
                stdout_hash
            ):
                errors.append(f"{metadata_label}: replay stdout_sha256 is invalid")
            elif (
                recorded_output is not None
                and stdout_hash != recorded_output.expected_sha256
            ):
                errors.append(
                    f"{metadata_label}: replay stdout SHA must match recorded output SHA"
                )

        if (
            len(errors) == local_error_count
            and isinstance(qualification_id, str)
            and report is not None
            and executable is not None
            and recorded_output is not None
        ):
            qualifications.append(
                Qualification(
                    qualification_id=qualification_id,
                    version=version,
                    directory=metadata_path.parent,
                    report=report,
                    executable=executable,
                    recorded_output=recorded_output,
                    supporting_artifacts=tuple(supporting),
                    expected_exit_code=expected_exit_code,
                )
            )

    allowed_control_files = {schema}
    for path in sorted(post_root.rglob("*")):
        if (not path.is_file() and not path.is_symlink()) or path in allowed_control_files:
            continue
        relative = _relative(path, root)
        if relative not in registered:
            errors.append(f"post-baseline discovery: unregistered artifact {relative}")

    return Discovery(
        qualifications=tuple(sorted(qualifications, key=lambda item: item.version)),
        registered_paths=frozenset(registered),
        errors=tuple(errors),
    )
