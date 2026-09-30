#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import yaml
from proto_ring.exact_evidence_binding import (
    BindingStatus,
    EvidenceBinding,
    EvidenceRequirement,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[2]
POSTBASELINE_PATH = ROOT / "tools" / "qualification" / "postbaseline.py"
EXECUTABLE_PROVIDER_COMMIT = "305d968c50db17cce43199ae3fa78d64da2aabdb"
EXACT_EVIDENCE_CONTRACT_COMMIT = "3bddcd4b49147f022466fdeb4acbf590e68890ce"
BINDING_PATH = (
    ROOT / "docs" / "repository-governance" / "ruu-exact-evidence-binding.md"
)


def load_postbaseline():
    spec = importlib.util.spec_from_file_location(
        "postbaseline_exact_evidence_binding",
        POSTBASELINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load post-baseline qualification module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


postbaseline = load_postbaseline()


class ExactEvidenceBindingTests(unittest.TestCase):
    def test_requirements_pin_exact_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/"
            f"proto-ring.git@{EXECUTABLE_PROVIDER_COMMIT}",
            requirements.splitlines(),
        )

    def test_local_binding_pins_exact_contract(self) -> None:
        text = BINDING_PATH.read_text(encoding="utf-8")
        _prefix, frontmatter, _body = text.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        self.assertEqual(
            {
                "repository": "fanilosendrison/proto-ring",
                "commit": EXACT_EVIDENCE_CONTRACT_COMMIT,
                "path": "docs/contracts/exact-evidence-binding.md",
            },
            metadata["exact_evidence_binding"]["contract"],
        )

    def test_postbaseline_imports_shared_objects(self) -> None:
        self.assertIs(postbaseline.BindingStatus, BindingStatus)
        self.assertIs(postbaseline.EvidenceRequirement, EvidenceRequirement)
        self.assertIs(postbaseline.EvidenceBinding, EvidenceBinding)
        self.assertIs(postbaseline.evaluate_evidence_binding, evaluate)

    def test_identical_exact_sha_matches(self) -> None:
        digest = "a" * 64
        self.assertIs(
            postbaseline._sha_binding_status("report", digest, digest),
            BindingStatus.MATCH,
        )

    def test_different_exact_sha_mismatches(self) -> None:
        self.assertIs(
            postbaseline._sha_binding_status("report", "a" * 64, "b" * 64),
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
        self.assertNotIn("hashlib", inspect.getsource(postbaseline._sha_binding_status))

    def test_artifact_treats_undetermined_as_existing_sha_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "qualification"
            directory.mkdir()
            path = directory / "report.md"
            path.write_text("report\n", encoding="utf-8")
            expected = postbaseline.sha256(path)
            errors: list[str] = []
            registered: set[str] = set()
            with mock.patch.object(
                postbaseline,
                "_sha_binding_status",
                return_value=BindingStatus.UNDETERMINED,
            ):
                postbaseline._artifact(
                    {"path": path.name, "sha256": expected},
                    "report",
                    directory,
                    "qualification/qualification-metadata.json",
                    root,
                    errors,
                    registered,
                )
        self.assertIn(
            "qualification/qualification-metadata.json: "
            "SHA mismatch for report artifact report.md",
            errors,
        )

    def test_replay_stdout_registration_uses_shared_binding_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            post_root = root / "qualification/state-space/post-baseline"
            version_root = post_root / "v046"
            version_root.mkdir(parents=True)
            (post_root / "qualification-metadata-v1.schema.json").write_text(
                "{}\n", encoding="utf-8"
            )
            contents = {
                "report": ("state-space-audit-v46.md", "# State-Space Audit v46\n"),
                "executable": ("state-space-audit-v46.py", "#!/usr/bin/env python3\n"),
                "recorded_output": ("state-space-audit-v46.txt", "PASS\n"),
            }
            artifacts = {}
            for role, (name, content) in contents.items():
                path = version_root / name
                path.write_text(content, encoding="utf-8")
                if role == "executable":
                    path.chmod(0o755)
                artifacts[role] = {
                    "path": name,
                    "sha256": postbaseline.sha256(path),
                }
            stdout_sha = artifacts["recorded_output"]["sha256"]
            metadata = {
                "$schema": "../qualification-metadata-v1.schema.json",
                "schema_version": 1,
                "qualification_id": "state-space-v046",
                "qualification_kind": "state-space",
                "provenance": "POST_BASELINE",
                "baseline": "ADR-080",
                "version": 46,
                "artifacts": artifacts,
                "supporting_artifacts": [],
                "replay": {
                    "expected_exit_code": 0,
                    "runner": "python3",
                    "stdout_sha256": stdout_sha,
                },
            }
            (version_root / "qualification-metadata.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            original = postbaseline._sha_binding_status
            with mock.patch.object(
                postbaseline,
                "_sha_binding_status",
                wraps=original,
            ) as binding_status:
                discovery = postbaseline.discover(root)

        self.assertEqual((), discovery.errors)
        binding_status.assert_any_call("recorded_output", stdout_sha, stdout_sha)

    def test_adoption_does_not_restore_generic_development_validation(self) -> None:
        source = POSTBASELINE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("DevelopmentValidationEvidence", source)
        self.assertNotIn("DevelopmentValidationDemand", source)


if __name__ == "__main__":
    unittest.main()
