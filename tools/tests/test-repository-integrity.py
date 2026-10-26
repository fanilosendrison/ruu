#!/usr/bin/env python3
"""Consumer-binding tests for native Ruu Repository Integrity."""

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
TOOLS = REPOSITORY / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

EXPECTED_IDS = [
    "maintained_python_syntax", "json_syntax", "adr_metadata_tests",
    "projection_integrity_tests", "exact_evidence_binding_tests",
    "governed_objects_tests", "historical_qualification_tests",
    "repository_integrity_tests", "qualification_infrastructure_tests",
    "structured_governance_tests", "proto_ring_binding_registry_tests",
    "proto_ring_provider_tests", "adr_metadata_check",
    "accepted_adr_body_immutability", "proto_ring_binding_registry_currentness",
    "proto_ring_provider_currentness", "structured_governance_check",
    "governance_authority_check", "governed_objects_check",
    "authoritative_ref_monotonicity_effective_rules", "retained_lineage_currentness",
    "active_manifest_currentness", "qualification_layout", "markdown_links",
    "git_whitespace",
]


def load_tool(name: str):
    path = TOOLS / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def raw_profile() -> dict[str, object]:
    text = (REPOSITORY / "docs/repository-governance/ruu-repository-integrity.md").read_text()
    return yaml.safe_load(text.split("---\n", 2)[1])["repository_integrity"]


def satisfied_obligation(validation_id: str, instance: int) -> dict[str, object]:
    return {
        "id": validation_id,
        "status": "SATISFIED",
        "executed": True,
        "exit_code": "0",
        "instance": instance,
    }


def coherent_result(
    validation_obligations: list[tuple[str, list[dict[str, object]]]],
) -> dict[str, object]:
    validations = [
        {"id": validation_id, "status": "SATISFIED", "obligations": obligations}
        for validation_id, obligations in validation_obligations
    ]
    return {
        "verdict": "PASS",
        "state_relation": "EQUAL",
        "state_coherence_halt": False,
        "validations": validations,
        "obligations": [
            obligation
            for validation in validations
            for obligation in validation["obligations"]
        ],
    }


class RepositoryIntegrityBindingTests(unittest.TestCase):
    def test_python_provider_declaration_is_absent(self) -> None:
        self.assertEqual("jsonschema==4.25.1\nPyYAML==6.0.2\n", (REPOSITORY / "requirements.txt").read_text())

    def test_authoritative_ref_binding_keeps_only_ruu_coordinates(self) -> None:
        binding = (REPOSITORY / "docs/repository-governance/ruu-authoritative-ref-monotonicity.md").read_text()
        configuration = yaml.safe_load(binding.split("---", 2)[1])["authoritative_ref_monotonicity"]
        self.assertNotIn("contract", configuration)
        self.assertEqual({"provider": "github", "owner": "fanilosendrison", "name": "ruu"}, configuration["repository"])
        self.assertEqual("refs/heads/main", configuration["authoritative_ref"])
        self.assertEqual("github-repository-ruleset", configuration["protection"]["mechanism"])

    def test_persistent_profile_owns_exact_membership_and_order(self) -> None:
        profile = raw_profile()
        self.assertEqual(EXPECTED_IDS, profile["order"])
        self.assertEqual(set(EXPECTED_IDS), set(profile["validations"]))
        self.assertEqual("repository_integrity_profile", profile["authority"]["source"])
        self.assertTrue(profile["continue_after_non_satisfied"])
        command = profile["validations"]["authoritative_ref_monotonicity_effective_rules"]["command"]
        self.assertEqual([2], command["undetermined_exit_codes"])

    def test_accepted_adr_validation_keeps_identity_and_native_command(self) -> None:
        profile = raw_profile()
        validation = profile["validations"]["accepted_adr_body_immutability"]
        self.assertEqual(["tools/check-accepted-adr-body.py"], validation["command"]["arguments"])
        self.assertEqual(13, profile["order"].index("accepted_adr_body_immutability"))

    def test_profile_mapping_declaration_order_has_no_meaning(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        text = """---
repository_integrity:
  validations:
    second: {}
    first: {}
  order:
    - first
    - second
---
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "profile.md").write_text(text)
            with mock.patch.object(tool, "PROFILE", Path("profile.md")):
                self.assertEqual(["first", "second"], tool._expected_validation_ids(root))

    def test_runner_does_not_construct_membership(self) -> None:
        source = (TOOLS / "check-repository-integrity.py").read_text()
        self.assertNotIn("CommandObligation", source)
        self.assertNotIn("canonical_obligations", source)
        self.assertNotIn("tools/tests/test-", source)
        self.assertIn("repository-integrity.evaluate", source)

    def test_coherent_pass_accepts_multiple_concrete_obligations(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        expected = ["single_validation", "for_each_validation"]
        result = coherent_result(
            [
                ("single_validation", [satisfied_obligation("single_validation", 0)]),
                (
                    "for_each_validation",
                    [satisfied_obligation("for_each_validation", index) for index in range(4)],
                ),
            ]
        )
        with mock.patch.object(tool, "_expected_validation_ids", return_value=expected):
            self.assertTrue(tool._coherent_pass(result))

    def test_coherent_pass_requires_exact_top_level_flatten(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        expected = ["single_validation", "for_each_validation"]
        result = coherent_result(
            [
                ("single_validation", [satisfied_obligation("single_validation", 0)]),
                (
                    "for_each_validation",
                    [satisfied_obligation("for_each_validation", index) for index in range(4)],
                ),
            ]
        )
        with mock.patch.object(tool, "_expected_validation_ids", return_value=expected):
            missing = {**result, "obligations": result["obligations"][:-1]}
            self.assertFalse(tool._coherent_pass(missing))
            reordered = {**result, "obligations": list(result["obligations"])}
            reordered["obligations"][1:3] = reversed(reordered["obligations"][1:3])
            self.assertFalse(tool._coherent_pass(reordered))
            modified = {**result, "obligations": list(result["obligations"])}
            modified["obligations"][1] = {**modified["obligations"][1], "instance": 99}
            self.assertFalse(tool._coherent_pass(modified))

    def test_coherent_pass_accepts_zero_instance_satisfied_validation(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        result = coherent_result([("zero_for_each", [])])
        with mock.patch.object(
            tool, "_expected_validation_ids", return_value=["zero_for_each"]
        ):
            self.assertTrue(tool._coherent_pass(result))

    def test_coherent_pass_requires_parent_obligation_id(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        result = coherent_result(
            [("parent_validation", [satisfied_obligation("other_validation", 0)])]
        )
        with mock.patch.object(
            tool, "_expected_validation_ids", return_value=["parent_validation"]
        ):
            self.assertFalse(tool._coherent_pass(result))

    def test_whitespace_binding_sends_exact_environment(self) -> None:
        tool = load_tool("check-git-whitespace.py")
        repository = Path("consumer-root")
        environment = {"PATH": os.environ.get("PATH", "")}
        with mock.patch.object(
            tool,
            "invoke_compat_result",
            return_value={"status": "PASS", "domains": []},
        ) as invoke:
            self.assertEqual([], tool.check(repository, env=environment))
        self.assertEqual(
            {"repository": str(repository), "environment": environment},
            invoke.call_args.args[2],
        )

    def test_native_whitespace_binding_detects_worktree_errors(self) -> None:
        tool = load_tool("check-git-whitespace.py")
        with tempfile.TemporaryDirectory(prefix="ruu-whitespace-") as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", root], check=True)
            subprocess.run(["git", "-C", root, "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", root, "config", "user.name", "Ruu Test"], check=True)
            fixture = root / "fixture.txt"
            fixture.write_text("clean\n")
            subprocess.run(["git", "-C", root, "add", "fixture.txt"], check=True)
            subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
            fixture.write_text("trailing whitespace  \n")
            errors = tool.check(root, env={})
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(any("trailing whitespace" in error for error in errors))

    def test_qualification_keeps_replay_after_repository_integrity(self) -> None:
        workflow = (REPOSITORY / ".github/workflows/qualification.yml").read_text()
        prepare = workflow.index("python3 tools/prepare-proto-ring-provider.py")
        currentness = workflow.index("python3 tools/check-proto-ring-provider.py")
        integrity = workflow.index("python3 tools/check-repository-integrity.py")
        historical = workflow.index("python3 tools/replay-historical-qualification.py latest")
        post_baseline = workflow.index("python3 tools/replay-post-baseline-qualification.py")
        git_smokes = workflow.index("python3 tools/replay-git-smokes.py", post_baseline)
        self.assertLess(prepare, currentness)
        self.assertLess(currentness, integrity)
        self.assertLess(integrity, historical)
        self.assertLess(historical, post_baseline)
        self.assertLess(post_baseline, git_smokes)
        self.assertIn("run: git diff --check", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
