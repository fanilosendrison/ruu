#!/usr/bin/env python3
"""Mechanical checks for Ruu's routed Projection Registry."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys
import unittest

from proto_ring.adr_metadata import parse_adr

REPOSITORY = Path(__file__).resolve().parents[2]
CHECKER = REPOSITORY / "tools/check-structured-governance.py"
HISTORY = REPOSITORY / "docs/adr/README.md"
ADR_DIRECTORY = REPOSITORY / "docs/adr"
ENTRY = re.compile(
    r"(?m)^- \[(?P<id>ADR-[0-9]{3})(?:: | — )(?P<name>.+?)\]"
    r"\((?P<path>[^)]+)\) — (?P<status>[A-Za-z-]+)"
)


def load_checker():
    spec = importlib.util.spec_from_file_location("ruu_structured_governance", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProjectionIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            _model,
            cls.authority,
            cls.objects,
            cls.bindings,
            cls.integrity,
            cls.projections,
            _evidence,
        ) = load_checker().load_structured_governance(REPOSITORY)

    def test_registry_declares_exact_real_relations(self) -> None:
        self.assertEqual(
            {
                "adr_index",
                "adr_annotated_history",
                "active_repository_manifest",
                "retained_lineage",
                "retained_state_space_custody",
                "retained_git_smoke_custody",
                "retained_qualification_custody",
                "governed_adr_catalog",
                "executable_binding_registry_representation",
                "effective_proto_ring_realization",
            },
            set(self.projections.projections),
        )
        generated = self.projections.projections["active_repository_manifest"]
        self.assertEqual("repository_git_tree", generated.canonical_source_id)
        self.assertEqual("active_repository_manifest", generated.secondary_source_id)
        self.assertEqual("active_manifest_currentness", generated.validation_id)
        bounded = self.projections.projections["retained_state_space_custody"]
        self.assertEqual("immutable_adr080_snapshot", bounded.boundary_source_id)

    def test_executable_projections_have_independent_validations(self) -> None:
        registry = self.projections.projections[
            "executable_binding_registry_representation"
        ]
        realization = self.projections.projections["effective_proto_ring_realization"]
        self.assertEqual("executable_dependency_manifest", registry.canonical_source_id)
        self.assertEqual("governance_binding_registry", registry.secondary_source_id)
        self.assertEqual(
            "proto_ring_binding_registry_currentness", registry.validation_id
        )
        self.assertEqual("effective_proto_ring_provider", realization.secondary_source_id)
        self.assertEqual("proto_ring_provider_currentness", realization.validation_id)
        self.assertNotEqual(registry.validation_id, realization.validation_id)
        self.assertEqual("proto_ring_executable", registry.binding_id)
        self.assertEqual("proto_ring_executable", realization.binding_id)

    def test_governed_catalog_matches_canonical_adr_identities(self) -> None:
        canonical_ids = {
            str(parse_adr(path)[0]["id"])
            for path in ADR_DIRECTORY.glob("adr-[0-9][0-9][0-9]-*.md")
        }
        catalog_ids = set(self.objects.interfaces["architecture_decisions"].objects)
        self.assertEqual(canonical_ids, catalog_ids)
        projection = self.projections.projections["governed_adr_catalog"]
        self.assertEqual("governed_objects_check", projection.validation_id)

    def test_annotated_history_matches_canonical_adr_fields(self) -> None:
        entries = [match.groupdict() for match in ENTRY.finditer(HISTORY.read_text())]
        canonical = []
        for path in sorted(ADR_DIRECTORY.glob("adr-[0-9][0-9][0-9]-*.md")):
            metadata, _body = parse_adr(path)
            canonical.append(
                {
                    "id": metadata["id"],
                    "name": metadata["name"],
                    "path": path.name,
                    "status": metadata["status"],
                }
            )
        self.assertEqual(
            [record["id"] for record in canonical],
            [entry["id"] for entry in entries],
        )
        for expected, actual in zip(canonical, entries, strict=True):
            with self.subTest(adr_id=expected["id"]):
                self.assertEqual(expected["name"], actual["name"])
                self.assertEqual(expected["path"], actual["path"])
                self.assertEqual(
                    str(expected["status"]).lower(), actual["status"].lower()
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
