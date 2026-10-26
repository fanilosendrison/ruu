"""Validate Ruu's repository-owned ADR profile declaration."""

from pathlib import Path
import re
from typing import Any

from proto_ring_adr_boundary import (
    AdrMetadataError, configured_profile_path, load_yaml,
    require_mapping as _require_mapping,
    require_string as _require_string,
    require_string_list as _require_string_list,
)

PROFILE_VERSION = "0.1.0"
RELATION_TYPES = ("clarifies", "amends", "supersedes", "confirms")

def load_profile(root: Path) -> dict[str, Any]:
    profile_path = configured_profile_path(root)
    profile = _require_mapping(load_yaml(profile_path), str(profile_path))
    if profile.get("profile_version") != PROFILE_VERSION:
        raise AdrMetadataError(
            f"{profile_path} must use profile_version {PROFILE_VERSION}"
        )

    canonical = _require_mapping(profile.get("canonical_schema"), "canonical_schema")
    for key in (
        "id",
        "repository",
        "source_path",
        "source_commit",
        "sha256",
        "vendored_path",
    ):
        _require_string(canonical.get(key), f"canonical_schema.{key}")
    if not re.fullmatch(r"[0-9a-f]{40}", canonical["source_commit"]):
        raise AdrMetadataError("canonical_schema.source_commit must be a full Git SHA")
    if not re.fullmatch(r"[0-9a-f]{64}", canonical["sha256"]):
        raise AdrMetadataError("canonical_schema.sha256 must be lowercase SHA-256")
    if not canonical["repository"].startswith("https://"):
        raise AdrMetadataError("canonical_schema.repository must use HTTPS")

    overlay = _require_mapping(profile.get("local_overlay"), "local_overlay")
    _require_string(overlay.get("id"), "local_overlay.id")
    overlay_hash = _require_string(overlay.get("sha256"), "local_overlay.sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", overlay_hash):
        raise AdrMetadataError("local_overlay.sha256 must be lowercase SHA-256")
    _require_string(overlay.get("path"), "local_overlay.path")

    repository = _require_mapping(profile.get("repository"), "repository")
    for key in (
        "display_name",
        "domain",
        "adr_directory",
        "filename_pattern",
        "id_pattern",
        "preferred_h1_separator",
    ):
        _require_string(repository.get(key), f"repository.{key}")
    if not isinstance(repository.get("id_width"), int) or repository["id_width"] < 1:
        raise AdrMetadataError("repository.id_width must be a positive integer")
    if repository.get("require_contiguous_ids") is not True:
        raise AdrMetadataError("repository.require_contiguous_ids must be true")
    if repository.get("retain_allocated_ids") is not True:
        raise AdrMetadataError("repository.retain_allocated_ids must be true")
    separators = _require_string_list(
        repository.get("h1_separators"), "repository.h1_separators"
    )
    if repository["preferred_h1_separator"] not in separators:
        raise AdrMetadataError(
            "repository.preferred_h1_separator must be listed in h1_separators"
        )
    if not isinstance(repository.get("preferred_h1_from"), int) or repository[
        "preferred_h1_from"
    ] < 1:
        raise AdrMetadataError("repository.preferred_h1_from must be a positive integer")
    if repository.get("reject_future_dates") is not True:
        raise AdrMetadataError("repository.reject_future_dates must be true")
    non_adr = _require_string_list(
        repository.get("non_adr_markdown"), "repository.non_adr_markdown"
    )
    if any(Path(name).name != name or not name.endswith(".md") for name in non_adr):
        raise AdrMetadataError(
            "repository.non_adr_markdown entries must be Markdown basenames"
        )
    try:
        re.compile(repository["filename_pattern"])
        re.compile(repository["id_pattern"])
    except re.error as error:
        raise AdrMetadataError(f"repository regex is invalid: {error}") from error

    legacy = _require_mapping(profile.get("legacy"), "legacy")
    _require_string_list(legacy.get("unstructured"), "legacy.unstructured")
    _require_string_list(legacy.get("null_dates"), "legacy.null_dates")

    generated_index = _require_mapping(profile.get("generated_index"), "generated_index")
    _require_string(generated_index.get("path"), "generated_index.path")
    if not isinstance(generated_index.get("required"), bool):
        raise AdrMetadataError("generated_index.required must be boolean")

    migration = _require_mapping(profile.get("migration_evidence"), "migration_evidence")
    _require_string(migration.get("path"), "migration_evidence.path")
    if not isinstance(migration.get("required"), bool):
        raise AdrMetadataError("migration_evidence.required must be boolean")
    _require_string_list(migration.get("ids"), "migration_evidence.ids")
    baseline = migration.get("baseline_commit")
    if migration["required"]:
        if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline):
            raise AdrMetadataError(
                "migration_evidence.baseline_commit must be a full Git SHA when required"
            )
    elif baseline is not None:
        raise AdrMetadataError(
            "migration_evidence.baseline_commit must be null when evidence is optional"
        )

    commands = _require_mapping(profile.get("commands"), "commands")
    _require_string(commands.get("check"), "commands.check")
    _require_string(commands.get("render"), "commands.render")
    return profile
