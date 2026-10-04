#!/usr/bin/env python3
"""Consumer-binding tests for Ruu Repository Integrity."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml

REPOSITORY = Path(__file__).resolve().parents[2]
EXECUTABLE_PROVIDER_COMMIT = "dedb01a3a9b7a18930c9da75afa3773b5ad67f69"


def load_tool(name: str):
    path = REPOSITORY / "tools" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RepositoryIntegrityBindingTests(unittest.TestCase):
    def test_proto_ring_provider_is_immutably_pinned(self) -> None:
        requirements = (REPOSITORY / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/"
            f"proto-ring.git@{EXECUTABLE_PROVIDER_COMMIT}\n",
            requirements,
        )
        self.assertNotIn("proto-ring.git@main", requirements)

    def test_authoritative_ref_binding_keeps_only_ruu_coordinates(self) -> None:
        binding = (
            REPOSITORY
            / "docs/repository-governance/ruu-authoritative-ref-monotonicity.md"
        ).read_text(encoding="utf-8")
        _prefix, frontmatter, _body = binding.split("---", 2)
        configuration = yaml.safe_load(frontmatter)["authoritative_ref_monotonicity"]
        self.assertNotIn("contract", configuration)
        self.assertEqual(
            {"provider": "github", "owner": "fanilosendrison", "name": "ruu"},
            configuration["repository"],
        )
        self.assertEqual("refs/heads/main", configuration["authoritative_ref"])
        self.assertEqual(
            "github-repository-ruleset", configuration["protection"]["mechanism"]
        )

    def test_persistent_profile_owns_exact_membership_and_order(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        profile = tool.load_profile(REPOSITORY)
        expected = (
            "maintained_python_syntax", "json_syntax", "adr_metadata_tests",
            "projection_integrity_tests", "exact_evidence_binding_tests",
            "governed_objects_tests", "historical_qualification_tests",
            "repository_integrity_tests", "qualification_infrastructure_tests",
            "structured_governance_tests", "proto_ring_binding_registry_tests",
            "proto_ring_provider_tests", "adr_metadata_check",
            "accepted_adr_body_immutability",
            "proto_ring_binding_registry_currentness",
            "proto_ring_provider_currentness", "structured_governance_check",
            "governance_authority_check", "governed_objects_check",
            "authoritative_ref_monotonicity_effective_rules",
            "retained_lineage_currentness", "active_manifest_currentness",
            "qualification_layout", "markdown_links", "git_whitespace",
        )
        self.assertEqual(expected, profile.order)
        self.assertEqual(set(profile.validations), set(expected))
        self.assertEqual("repository_integrity_profile", profile.authority.source)
        self.assertTrue(profile.continue_after_non_satisfied)
        self.assertEqual(
            frozenset({2}),
            profile.validations[
                "authoritative_ref_monotonicity_effective_rules"
            ].command.undetermined_exit_codes,
        )

    def test_dynamic_membership_uses_repository_path_instantiation(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        profile = tool.load_profile(REPOSITORY)
        python_instances = profile.validations["maintained_python_syntax"].instances
        self.assertEqual("repository_paths", python_instances.kind)
        self.assertEqual("append_all", python_instances.mode)
        self.assertEqual(
            ("tools/*.py", "tools/qualification/*.py", "tools/tests/*.py"),
            tuple(selector.value for selector in python_instances.selectors),
        )
        json_instances = profile.validations["json_syntax"].instances
        self.assertEqual("repository_paths", json_instances.kind)
        self.assertEqual("for_each", json_instances.mode)

    def test_runner_is_thin_and_does_not_construct_membership(self) -> None:
        source = (REPOSITORY / "tools/check-repository-integrity.py").read_text()
        self.assertNotIn("CommandObligation", source)
        self.assertNotIn("canonical_obligations", source)
        self.assertNotIn("tools/tests/test-", source)
        self.assertIn("evaluate_consumer_profile", source)

    def test_whitespace_binding_delegates_to_shared_provider(self) -> None:
        tool = load_tool("check-git-whitespace.py")
        root = Path("consumer-root")
        environment = {"PATH": os.environ.get("PATH", "")}
        with mock.patch.object(tool.git_whitespace, "check", return_value=["failure"]) as check:
            self.assertEqual(tool.check(root, env=environment), ["failure"])
        check.assert_called_once_with(root, env=environment)

    def test_shared_whitespace_binding_detects_worktree_errors(self) -> None:
        tool = load_tool("check-git-whitespace.py")
        with tempfile.TemporaryDirectory(prefix="ruu-whitespace-") as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", root], check=True)
            subprocess.run(
                ["git", "-C", root, "config", "user.email", "test@example.invalid"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", root, "config", "user.name", "Ruu Test"], check=True
            )
            fixture = root / "fixture.txt"
            fixture.write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "-C", root, "add", "fixture.txt"], check=True)
            subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
            fixture.write_text("trailing whitespace  \n", encoding="utf-8")
            errors = tool.check(root, env={})
        self.assertEqual(1, len(errors))
        self.assertIn("trailing whitespace", errors[0])

    def test_qualification_keeps_replay_after_repository_integrity(self) -> None:
        workflow = (REPOSITORY / ".github/workflows/qualification.yml").read_text()
        integrity = workflow.index("python3 tools/check-repository-integrity.py")
        historical = workflow.index("python3 tools/replay-historical-qualification.py latest")
        post_baseline = workflow.index("python3 tools/replay-post-baseline-qualification.py")
        git_smokes = workflow.index("python3 tools/replay-git-smokes.py", post_baseline)
        self.assertLess(integrity, historical)
        self.assertLess(historical, post_baseline)
        self.assertLess(post_baseline, git_smokes)
        self.assertIn("run: git diff --check", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
