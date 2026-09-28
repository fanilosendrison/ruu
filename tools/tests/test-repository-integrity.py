#!/usr/bin/env python3
"""Consumer-binding tests for Ruu Repository Integrity."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from proto_ring.repository_integrity import CommandObligation

REPOSITORY = Path(__file__).resolve().parents[2]
PROVIDER_COMMIT = "72e6e9615703e4d3293175f023d1d953632c45a8"


def load_tool(name: str):
    path = REPOSITORY / "tools" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RepositoryIntegrityBindingTests(unittest.TestCase):
    def test_proto_ring_provider_is_immutably_pinned(self) -> None:
        requirements = (REPOSITORY / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/"
            f"proto-ring.git@{PROVIDER_COMMIT}\n",
            requirements,
        )
        self.assertNotIn("proto-ring.git@main", requirements)

    def test_authoritative_ref_monotonicity_binding(self) -> None:
        binding = (
            REPOSITORY
            / "docs/repository-governance/ruu-authoritative-ref-monotonicity.md"
        ).read_text(encoding="utf-8")
        _prefix, frontmatter, _body = binding.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        configuration = metadata["authoritative_ref_monotonicity"]

        self.assertEqual(
            {
                "repository": "fanilosendrison/proto-ring",
                "commit": "650a481b7dfa7c4d3671bd053c63642a5dab1087",
                "path": "docs/contracts/authoritative-ref-monotonicity.md",
            },
            configuration["contract"],
        )
        self.assertEqual(
            {
                "provider": "github",
                "owner": "fanilosendrison",
                "name": "ruu",
            },
            configuration["repository"],
        )
        self.assertEqual("refs/heads/main", configuration["authoritative_ref"])
        protection = configuration["protection"]
        self.assertEqual("github-repository-ruleset", protection["mechanism"])
        self.assertIs(type(protection["ruleset_id"]), int)
        self.assertGreater(protection["ruleset_id"], 0)

    def test_ruu_owns_exact_repository_integrity_membership(self) -> None:
        tool = load_tool("check-repository-integrity.py")
        obligations = tool.canonical_obligations(REPOSITORY)
        self.assertTrue(all(isinstance(item, CommandObligation) for item in obligations))
        self.assertEqual(
            [item.name for item in obligations],
            [
                "Maintained Python syntax",
                "JSON syntax: docs/adr/schemas/architecture-decision-record.schema.json",
                "JSON syntax: docs/adr/schemas/ruu-architecture-decision-record.schema.json",
                "JSON syntax: qualification/lineage/lineage-v2.schema.json",
                "JSON syntax: qualification/state-space/post-baseline/qualification-metadata-v1.schema.json",
                "ADR metadata tests",
                "Projection Integrity tests",
                "Historical qualification tests",
                "Repository Integrity binding tests",
                "Qualification infrastructure tests",
                "ADR metadata check",
                "Accepted ADR body immutability",
                "Shared Governance Provider binding",
                "Retained lineage currentness",
                "Active manifest currentness",
                "Qualification layout",
                "Markdown links",
                "Git whitespace",
            ],
        )
        self.assertEqual(obligations[-1].argv, (sys.executable, "tools/check-git-whitespace.py"))
        self.assertTrue(tool.integrity_profile(REPOSITORY).continue_after_non_satisfied)

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
            subprocess.run(["git", "-C", root, "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", root, "config", "user.name", "Ruu Test"], check=True)
            fixture = root / "fixture.txt"
            fixture.write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "-C", root, "add", "fixture.txt"], check=True)
            subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
            fixture.write_text("trailing whitespace  \n", encoding="utf-8")
            errors = tool.check(root, env={})
        self.assertEqual(len(errors), 1)
        self.assertIn("trailing whitespace", errors[0])

    def test_qualification_keeps_replay_distinct_from_repository_integrity(self) -> None:
        workflow = (REPOSITORY / ".github/workflows/qualification.yml").read_text(
            encoding="utf-8"
        )
        integrity = workflow.index("python3 tools/check-repository-integrity.py")
        historical = workflow.index("python3 tools/replay-historical-qualification.py latest")
        post_baseline = workflow.index("python3 tools/replay-post-baseline-qualification.py")
        git_smokes = workflow.index(
            "python3 tools/replay-git-smokes.py", post_baseline
        )
        self.assertLess(integrity, historical)
        self.assertLess(historical, post_baseline)
        self.assertLess(post_baseline, git_smokes)
        self.assertNotIn("run: git diff --check", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
