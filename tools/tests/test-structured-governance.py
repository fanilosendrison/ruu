#!/usr/bin/env python3
"""Composition tests for Ruu's complete native governance projection."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_structured_governance_import import load_structured_governance
import check_structured_governance_import as loader

CAPABILITIES = {
    "architecture_decisions", "governance_authority", "governed_objects",
    "shared_governance_provider", "projection_integrity", "repository_integrity",
    "evidence_requirements", "authoritative_ref_monotonicity",
}
PROJECTIONS = {
    "adr_index", "adr_annotated_history", "active_repository_manifest",
    "retained_lineage", "retained_state_space_custody", "retained_git_smoke_custody",
    "retained_qualification_custody", "governed_adr_catalog",
    "effective_proto_ring_realization",
}
EVIDENCE_IDS = {
    "post_baseline_artifact_binding",
    "post_baseline_recorded_output_binding",
}


class StructuredGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.model,
            cls.authority,
            cls.objects,
            cls.bindings,
            cls.integrity,
            cls.projections,
            cls.evidence,
        ) = load_structured_governance(ROOT)

    def test_rgm_v2_declares_exact_applicable_capabilities(self) -> None:
        self.assertEqual(2, self.model["model_version"])
        self.assertEqual(CAPABILITIES, set(self.model["capabilities"]))
        self.assertEqual("registry", self.model["provider"]["binding"]["route"])
        routes = [
            route
            for capability in self.model["capabilities"].values()
            for route in capability["routes"].values()
        ]
        self.assertEqual(8, len(routes))
        self.assertTrue(all(route["route"][0] == "capabilities" for route in routes))

    def test_binding_registry_contains_exact_active_bindings(self) -> None:
        executable = self.bindings["bindings"]["proto_ring_executable"]
        self.assertEqual("4ae1a2a549d7dae8e4cce7f727b9bc5330f3823f", executable["identity"]["commit"])
        self.assertEqual("governance_binding_registry", executable["authority"]["source"])
        self.assertEqual(11, len(self.bindings["bindings"]))

    def test_complete_helper_invokes_one_complete_composition(self) -> None:
        checker = loader._MODULE
        real = checker.invoke_compat_result
        with mock.patch.object(checker, "invoke_compat_result", wraps=real) as invoke:
            values = checker.load_structured_governance(ROOT)
        self.assertEqual(1, invoke.call_count)
        self.assertEqual("repository-governance-state.compose", invoke.call_args.args[1])
        self.assertEqual("complete", invoke.call_args.args[2]["projection"])
        self.assertEqual(7, len(values))
        self.assertTrue(all(type(value) is dict for value in values))

    def test_complete_state_preserves_ruu_governance(self) -> None:
        objects = self.objects["interfaces"]["architecture_decisions"]["objects"]
        self.assertEqual({f"ADR-{number:03d}" for number in range(1, 95)}, set(objects))
        self.assertEqual(25, len(self.integrity["order"]))
        self.assertEqual(set(self.integrity["validations"]), set(self.integrity["order"]))
        self.assertEqual(PROJECTIONS, set(self.projections["projections"]))
        self.assertEqual(EVIDENCE_IDS, set(self.evidence["requirements"]))
        self.assertEqual(2, len(self.evidence["requirements"]))

    def test_complete_state_construction_is_read_only(self) -> None:
        before = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain=v1", "-z"],
            check=True,
            capture_output=True,
        ).stdout
        load_structured_governance(ROOT)
        after = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain=v1", "-z"],
            check=True,
            capture_output=True,
        ).stdout
        self.assertEqual(before, after)

    def test_authority_preserves_provider_and_qualification_ownership(self) -> None:
        provider = self.authority["responsibilities"]["executable_provider_binding"]["roles"]
        self.assertEqual(
            {
                "governance_binding_registry": "authority",
                "effective_proto_ring_provider": "secondary_representation",
            },
            provider,
        )
        self.assertNotIn("executable_dependency_manifest", self.authority["sources"])
        qualification = self.authority["responsibilities"]["qualification_execution_evidence"]["roles"]
        self.assertEqual("authority", qualification["post_baseline_qualification_evidence"])

    def test_persistent_integrity_owns_complete_order(self) -> None:
        self.assertEqual("repository_integrity_profile", self.integrity["authority"]["source"])
        self.assertEqual(25, len(self.integrity["order"]))
        self.assertIn("qualification_layout", self.integrity["order"])
        self.assertNotIn("historical_qualification_replay", self.integrity["order"])
        self.assertNotIn("git_smoke_replay", self.integrity["order"])

    def test_evidence_registry_is_responsibility_scoped_without_objects(self) -> None:
        self.assertEqual(EVIDENCE_IDS, set(self.evidence["requirements"]))
        for requirement in self.evidence["requirements"].values():
            self.assertEqual("qualification_evidence_binding", requirement["responsibility"])
            self.assertIsNone(requirement["target"])

    def test_obsolete_carriers_and_authority_are_absent(self) -> None:
        governance = ROOT / "docs/repository-governance"
        self.assertFalse((governance / "ruu-shared-governance-provider.md").exists())
        self.assertFalse((governance / "ruu-exact-evidence-binding.md").exists())
        self.assertNotIn("executable_dependency_manifest", (governance / "ruu-governance-authority.md").read_text())
        self.assertNotIn("executable_binding_registry_representation", (governance / "ruu-projection-integrity.md").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
