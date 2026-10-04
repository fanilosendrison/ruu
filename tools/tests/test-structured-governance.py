#!/usr/bin/env python3
"""Composition tests for Ruu structured governance."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import socket
import subprocess
import sys
import unittest
import urllib.request
from unittest import mock

from proto_ring import (
    evidence_requirements,
    exact_evidence_binding,
    github_authoritative_ref_monotonicity,
    repository_governance_state,
    repository_integrity,
)
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
                "repository_governance_state_contract",
                "repository_integrity_contract",
                "evidence_requirements_contract",
            },
            set(self.bindings.bindings),
        )
        executable = self.bindings.bindings["proto_ring_executable"]
        self.assertEqual(
            "dedb01a3a9b7a18930c9da75afa3773b5ad67f69",
            executable.identity.commit,
        )
        self.assertEqual(
            "executable_dependency_manifest", executable.authority.source_id
        )
        contract = self.bindings.bindings[
            "repository_governance_state_contract"
        ]
        self.assertEqual("repository_governance_state_contract", contract.id)
        self.assertEqual("governance_contract", contract.kind.value)
        self.assertEqual("logical_provider", contract.scope.kind.value)
        self.assertEqual("fanilosendrison/proto-ring", contract.identity.repository)
        self.assertEqual(
            "9a1ed2d71d079b0118177c2a509ca356c371a597",
            contract.identity.commit,
        )
        self.assertEqual(
            "docs/contracts/repository-governance-state.md",
            contract.identity.path,
        )
        self.assertEqual(
            "governance_contract_bindings", contract.authority.responsibility_id
        )
        self.assertEqual(
            "governance_binding_registry", contract.authority.source_id
        )

    def test_compatibility_helper_projects_one_canonical_state(self) -> None:
        checker = load_checker()
        real_load = checker.repository_governance_state.load

        with mock.patch.object(
            checker.repository_governance_state,
            "load",
            wraps=real_load,
        ) as canonical_load:
            values = checker.load_structured_governance(ROOT)

        self.assertEqual(1, canonical_load.call_count)
        self.assertEqual(7, len(values))

    def test_canonical_state_preserves_complete_ruu_governance(self) -> None:
        state = repository_governance_state.load(ROOT)
        self.assertEqual(ROOT.resolve(), state.repository)
        self.assertEqual(2, state.repository_governance_model.model_version)
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
            set(state.repository_governance_model.capabilities),
        )
        self.assertNotIn(
            "repository_governance_state",
            state.repository_governance_model.capabilities,
        )

        objects = state.governed_objects
        self.assertIsNotNone(objects)
        assert objects is not None
        self.assertEqual({"architecture_decisions"}, set(objects.interfaces))
        self.assertEqual(
            {f"ADR-{number:03d}" for number in range(1, 92)},
            set(objects.interfaces["architecture_decisions"].objects),
        )

        integrity = state.repository_integrity
        self.assertIsNotNone(integrity)
        assert integrity is not None
        self.assertEqual(25, len(integrity.order))
        self.assertEqual(set(integrity.validations), set(integrity.order))
        self.assertEqual(
            frozenset({2}),
            integrity.validations[
                "authoritative_ref_monotonicity_effective_rules"
            ].command.undetermined_exit_codes,
        )

        projections = state.projection_registry
        self.assertIsNotNone(projections)
        assert projections is not None
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
            set(projections.projections),
        )

        evidence = state.evidence_requirements
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(
            {
                "post_baseline_artifact_binding",
                "post_baseline_recorded_output_binding",
            },
            set(evidence.requirements),
        )
        for requirement in evidence.requirements.values():
            self.assertEqual(
                "qualification_evidence_binding", requirement.responsibility_id
            )
            self.assertIsNone(requirement.target)
            self.assertIs(
                evidence_requirements.InstantiationKind.SOURCE,
                requirement.instances.kind,
            )

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
                "repository_governance_state_contract",
                "repository_integrity_contract",
                "evidence_requirements_contract",
            },
            set(state.governance_bindings.bindings),
        )

    def test_canonical_state_construction_is_read_only_and_non_executing(self) -> None:
        before = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain=v1", "-z"],
            check=True,
            capture_output=True,
        ).stdout
        real_popen = subprocess.Popen
        observed_git: list[tuple[str, ...]] = []

        def guarded_popen(*args, **kwargs):
            command = args[0] if args else kwargs.get("args")
            if not isinstance(command, (list, tuple)):
                raise AssertionError(f"non-vector process command: {command!r}")
            if (
                len(command) < 4
                or tuple(command[:3]) != ("git", "-C", str(ROOT))
                or command[3] not in {"rev-parse", "symbolic-ref", "ls-files"}
            ):
                raise AssertionError(f"unexpected state-construction process: {command!r}")
            observed_git.append(tuple(command))
            return real_popen(*args, **kwargs)

        with mock.patch.object(subprocess, "Popen", new=guarded_popen), mock.patch.object(
            repository_integrity,
            "evaluate_consumer_profile",
            side_effect=AssertionError("Repository Integrity evaluation is forbidden"),
        ) as integrity_evaluate, mock.patch.object(
            exact_evidence_binding,
            "evaluate",
            side_effect=AssertionError("Exact Evidence Binding evaluation is forbidden"),
        ) as evidence_evaluate, mock.patch.object(
            github_authoritative_ref_monotonicity,
            "run",
            side_effect=AssertionError("ARM provider observation is forbidden"),
        ) as arm_run, mock.patch.object(
            socket,
            "create_connection",
            side_effect=AssertionError("network access is forbidden"),
        ), mock.patch.object(
            urllib.request,
            "urlopen",
            side_effect=AssertionError("network access is forbidden"),
        ):
            state = repository_governance_state.load(ROOT)

        after = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain=v1", "-z"],
            check=True,
            capture_output=True,
        ).stdout
        self.assertEqual(ROOT.resolve(), state.repository)
        self.assertEqual(before, after)
        self.assertGreater(len(observed_git), 0)
        integrity_evaluate.assert_not_called()
        evidence_evaluate.assert_not_called()
        arm_run.assert_not_called()

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
