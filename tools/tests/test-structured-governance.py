#!/usr/bin/env python3
"""Composition tests for Ruu structured governance."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

from proto_ring.governance_authority import SourceRole, role_of

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/check-structured-governance.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_structured_governance", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
        ) = load_checker().load_structured_governance(ROOT)

    def test_rgm_v2_declares_exact_applicable_capabilities(self) -> None:
        self.assertEqual(2, self.model.model_version)
        self.assertEqual(
            {
                "architecture_decisions",
                "governance_authority",
                "governed_objects",
                "shared_governance_provider",
                "projection_integrity",
                "repository_integrity",
                "evidence_requirements",
                "authoritative_ref_monotonicity",
            },
            set(self.model.capabilities),
        )
        self.assertEqual("registry", self.model.provider.binding.route)

    def test_binding_registry_contains_exact_active_bindings(self) -> None:
        self.assertEqual(
            {
                "proto_ring_executable",
                "shared_governance_provider_contract",
                "projection_integrity_contract",
                "exact_evidence_binding_contract",
                "governance_authority_contract",
                "governed_objects_contract",
                "authoritative_ref_monotonicity_contract",
                "repository_governance_model_contract",
                "repository_integrity_contract",
                "evidence_requirements_contract",
            },
            set(self.bindings.bindings),
        )
        executable = self.bindings.bindings["proto_ring_executable"]
        self.assertEqual(
            "890ed560e61e205067bdf3628e419302613ef06e",
            executable.identity.commit,
        )
        self.assertEqual(
            "executable_dependency_manifest", executable.authority.source_id
        )

    def test_authority_preserves_executable_and_qualification_ownership(self) -> None:
        self.assertIs(
            SourceRole.AUTHORITY,
            role_of(
                self.authority,
                "executable_provider_binding",
                "executable_dependency_manifest",
            ),
        )
        self.assertIs(
            SourceRole.SECONDARY_REPRESENTATION,
            role_of(
                self.authority,
                "executable_provider_binding",
                "governance_binding_registry",
            ),
        )
        self.assertIs(
            SourceRole.AUTHORITY,
            role_of(
                self.authority,
                "qualification_execution_evidence",
                "post_baseline_qualification_evidence",
            ),
        )

    def test_persistent_integrity_owns_complete_order(self) -> None:
        self.assertEqual("repository_integrity_profile", self.integrity.authority.source)
        self.assertEqual(25, len(self.integrity.order))
        self.assertEqual(set(self.integrity.validations), set(self.integrity.order))
        self.assertEqual(
            frozenset({2}),
            self.integrity.validations[
                "authoritative_ref_monotonicity_effective_rules"
            ].command.undetermined_exit_codes,
        )
        self.assertIn("qualification_layout", self.integrity.order)
        self.assertNotIn("historical_qualification_replay", self.integrity.order)
        self.assertNotIn("git_smoke_replay", self.integrity.order)

    def test_evidence_registry_is_responsibility_scoped_without_objects(self) -> None:
        self.assertEqual(
            {
                "post_baseline_artifact_binding",
                "post_baseline_recorded_output_binding",
            },
            set(self.evidence.requirements),
        )
        for requirement in self.evidence.requirements.values():
            self.assertEqual(
                "qualification_evidence_binding", requirement.responsibility_id
            )
            self.assertIsNone(requirement.target)

    def test_obsolete_carriers_and_duplicate_pins_are_absent(self) -> None:
        governance = ROOT / "docs/repository-governance"
        self.assertFalse((governance / "ruu-shared-governance-provider.md").exists())
        self.assertFalse((governance / "ruu-exact-evidence-binding.md").exists())
        self.assertNotIn(
            "governance_authority_contract:",
            (governance / "ruu-governance-authority.md").read_text(),
        )
        self.assertNotIn(
            "governed_objects_contract:",
            (governance / "ruu-governed-objects.md").read_text(),
        )
        arm = (governance / "ruu-authoritative-ref-monotonicity.md").read_text()
        self.assertNotIn("  contract:\n", arm)


if __name__ == "__main__":
    unittest.main(verbosity=2)
