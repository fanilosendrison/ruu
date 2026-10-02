#!/usr/bin/env python3
"""Tests for Ruu's routed post-baseline evidence requirements."""

from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from proto_ring import evidence_requirements
from proto_ring.exact_evidence_binding import BindingStatus

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from qualification import postbaseline  # noqa: E402
from qualification import postbaseline_evidence_requirements as policies  # noqa: E402


class ExactEvidenceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policies = policies.load(ROOT)

    def test_registry_has_exact_distinct_requirements(self) -> None:
        artifact = self.policies.artifact
        recorded = self.policies.recorded_output
        self.assertEqual("post_baseline_artifact_binding", artifact.id)
        self.assertEqual("post_baseline_recorded_output_binding", recorded.id)
        self.assertIs(
            evidence_requirements.EvidenceClassKind.SOURCE,
            artifact.evidence_classes.kind,
        )
        self.assertEqual(
            frozenset({"recorded_output"}),
            recorded.evidence_classes.explicit_classes,
        )
        for requirement in (artifact, recorded):
            self.assertIs(
                evidence_requirements.InstantiationKind.SOURCE,
                requirement.instances.kind,
            )
            self.assertFalse(requirement.context.required)
            self.assertIsNone(requirement.target)

    def test_exact_sha_binding_matches_and_mismatches(self) -> None:
        digest = "a" * 64
        self.assertIs(
            policies.binding_status(self.policies.artifact, "report", digest, digest),
            BindingStatus.MATCH,
        )
        self.assertIs(
            policies.binding_status(
                self.policies.artifact, "report", "a" * 64, "b" * 64
            ),
            BindingStatus.MISMATCH,
        )

    def test_recorded_output_uses_its_distinct_requirement(self) -> None:
        digest = "a" * 64
        self.assertIs(
            policies.binding_status(
                self.policies.recorded_output,
                "recorded_output",
                digest,
                digest,
            ),
            BindingStatus.MATCH,
        )
        self.assertIs(
            policies.binding_status(
                self.policies.recorded_output, "report", digest, digest
            ),
            BindingStatus.MISMATCH,
        )

    def test_ruu_keeps_sha256_construction_local(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "artifact.txt"
            artifact.write_bytes(b"Ruu-owned bytes\n")
            self.assertEqual(
                hashlib.sha256(artifact.read_bytes()).hexdigest(),
                postbaseline.sha256(artifact),
            )
        self.assertIn("hashlib.sha256", inspect.getsource(postbaseline.sha256))
        self.assertNotIn("hashlib", inspect.getsource(policies.binding_status))

    def test_live_discovery_consumes_both_requirements(self) -> None:
        original = policies.binding_status
        with mock.patch.object(policies, "binding_status", wraps=original) as binding:
            discovery = postbaseline.discover(ROOT)
        self.assertEqual((), discovery.errors)
        self.assertGreaterEqual(len(discovery.qualifications), 1)
        requirement_ids = {call.args[0].id for call in binding.call_args_list}
        self.assertEqual(
            {
                "post_baseline_artifact_binding",
                "post_baseline_recorded_output_binding",
            },
            requirement_ids,
        )

    def test_discovery_fails_closed_when_registry_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "repository"
            shutil.copytree(
                ROOT,
                fixture,
                ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc"),
            )
            registry = fixture / "docs/repository-governance/ruu-evidence-requirements.md"
            registry.unlink()
            discovery = postbaseline.discover(fixture)
        self.assertEqual((), discovery.qualifications)
        self.assertIn("cannot load evidence requirements", discovery.errors[0])

    def test_adoption_does_not_restore_generic_development_validation(self) -> None:
        source = (ROOT / "tools/qualification/postbaseline.py").read_text()
        source += (ROOT / "tools/qualification/postbaseline_evidence_requirements.py").read_text()
        self.assertNotIn("DevelopmentValidationEvidence", source)
        self.assertNotIn("DevelopmentValidationDemand", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
