#!/usr/bin/env python3
"""Tests for Ruu-owned post-baseline policy over native exact binding."""

from __future__ import annotations

import hashlib
import inspect
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
        self.assertEqual("source", artifact.evidence_classes.kind)
        self.assertEqual(frozenset({"recorded_output"}), recorded.evidence_classes.classes)
        for requirement in (artifact, recorded):
            self.assertEqual("source", requirement.instances.kind)
            self.assertFalse(requirement.context.required)
            self.assertIsNone(requirement.target)

    def test_exact_sha_binding_matches_and_mismatches(self) -> None:
        digest = "a" * 64
        self.assertEqual("MATCH", policies.binding_status(self.policies.artifact, "report", digest, digest))
        self.assertEqual(
            "MISMATCH",
            policies.binding_status(self.policies.artifact, "report", "a" * 64, "b" * 64),
        )

    def test_recorded_output_uses_its_distinct_requirement(self) -> None:
        digest = "a" * 64
        self.assertEqual(
            "MATCH",
            policies.binding_status(self.policies.recorded_output, "recorded_output", digest, digest),
        )
        self.assertEqual(
            "MISMATCH",
            policies.binding_status(self.policies.recorded_output, "report", digest, digest),
        )

    def test_ascii_sha_identity_is_hex_encoded_text(self) -> None:
        digest = "a" * 64
        with mock.patch.object(
            policies,
            "invoke_compat_result",
            return_value={"status": "MATCH"},
        ) as invoke:
            self.assertEqual(
                "MATCH",
                policies.binding_status(self.policies.artifact, "report", digest, digest),
            )
        payload = invoke.call_args.args[2]
        self.assertEqual(digest.encode("ascii").hex(), payload["requirement"]["subject_hex"])
        self.assertEqual(digest.encode("ascii").hex(), payload["binding"]["subject_hex"])
        self.assertNotEqual(digest, payload["requirement"]["subject_hex"])

    def test_ruu_keeps_sha256_construction_local(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "artifact.txt"
            artifact.write_bytes(b"Ruu-owned bytes\n")
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), postbaseline.sha256(artifact))
        self.assertIn("hashlib.sha256", inspect.getsource(postbaseline.sha256))
        self.assertNotIn("hashlib", inspect.getsource(policies.binding_status))

    def test_live_discovery_makes_exactly_five_native_calls(self) -> None:
        original = policies.invoke_compat_result
        calls: list[dict[str, object]] = []

        def observe(root, operation, payload):
            if operation == "exact-evidence-binding.evaluate":
                calls.append(payload)
            return original(root, operation, payload)

        with mock.patch.object(policies, "invoke_compat_result", side_effect=observe):
            discovery = postbaseline.discover(ROOT)
        self.assertEqual((), discovery.errors)
        self.assertEqual(5, len(calls))
        self.assertTrue(all(call["mode"] == "evaluate_binding" for call in calls))

    def test_discovery_fails_closed_when_registry_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "repository"
            shutil.copytree(ROOT, fixture, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc"))
            subprocess.run(["git", "init", "-q", str(fixture)], check=True)
            (fixture / "docs/repository-governance/ruu-evidence-requirements.md").unlink()
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
