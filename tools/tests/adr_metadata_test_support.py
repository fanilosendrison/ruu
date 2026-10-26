#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import proto_ring_adr_boundary as shared_adr_metadata
from check_structured_governance_import import load_structured_governance
from proto_ring_executable_binding import invoke_compat_result

SCRIPT = TOOLS / "adr-metadata.py"

spec = importlib.util.spec_from_file_location("adr_metadata", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
adr_metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adr_metadata)


def write_repository_governance(fixture_root: Path) -> None:
    (fixture_root / "AGENTS.md").write_text(
        "---\n"
        "repository_governance:\n"
        "  model_version: 1\n"
        "  provider:\n"
        '    id: "proto-ring"\n'
        "    binding:\n"
        '      capability: "shared_governance_provider"\n'
        '      route: "binding"\n'
        "  capabilities:\n"
        "    architecture_decisions:\n"
        "      configuration: {}\n"
        "      routes:\n"
        '        profile: "docs/adr/adr-profile.yaml"\n'
        "    shared_governance_provider:\n"
        "      configuration:\n"
        "        required: true\n"
        "      routes:\n"
        '        binding: "docs/repository-governance/test-shared-governance-provider.md"\n'
        "---\n"
        "# Test repository directives\n",
        encoding="utf-8",
    )
    binding = (
        fixture_root
        / "docs"
        / "repository-governance"
        / "test-shared-governance-provider.md"
    )
    binding.parent.mkdir(parents=True, exist_ok=True)
    binding.write_text(
        "# Test Shared Governance Provider binding target\n", encoding="utf-8"
    )


def copy_adr_fixture(temporary: str) -> Path:
    fixture_root = Path(temporary)
    shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
    write_repository_governance(fixture_root)
    return fixture_root


def structured_adr_bytes(
    adr_id: str, name: str, separator: str, context_body: bytes
) -> bytes:
    metadata = {
        "okf_version": "1.0",
        "adr_profile_version": "0.1.0",
        "kind": "KnowledgeAsset",
        "asset_type": "architecture-decision-record",
        "domain": "ruu",
        "severity": "strict",
        "name": name,
        "id": adr_id,
        "status": "accepted",
        "date": "2026-09-10",
        "decision_body_sha256": adr_metadata.sha256_hex(context_body),
        "relation_completeness": "complete",
        "relations": {
            "clarifies": [],
            "amends": [],
            "supersedes": [],
            "confirms": [],
        },
        "governs": [],
    }
    frontmatter = adr_metadata.yaml.safe_dump(metadata, sort_keys=False).encode()
    return b"---\n" + frontmatter + b"---\n\n# " + adr_id.encode() + separator.encode() + name.encode() + b"\n\n" + context_body


def disable_git_bound_validation(fixture_root: Path) -> None:
    profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
    profile = adr_metadata.load_yaml(profile_path)
    profile["migration_evidence"] = {
        "path": "docs/adr/metadata-migration-evidence.yaml",
        "required": False,
        "baseline_commit": None,
        "ids": [],
    }
    profile["generated_index"]["required"] = False
    profile_path.write_text(
        adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
    )


