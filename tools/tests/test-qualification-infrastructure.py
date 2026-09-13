#!/usr/bin/env python3
"""Hostile integration tests for the Ruu qualification infrastructure."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QualificationInfrastructureTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix="ruu-qualification-tests-"
        )
        self.root = Path(self.temporary.name) / "ruu"
        shutil.copytree(
            REPOSITORY,
            self.root,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"),
        )
        post_baseline = self.root / "qualification/state-space/post-baseline"
        metadata_paths = post_baseline.glob(
            "v[0-9][0-9][0-9]/qualification-metadata.json"
        )
        existing_versions = [int(path.parent.name[1:]) for path in metadata_paths]
        self.existing_post_baseline_count = len(existing_versions)
        self.next_post_baseline_version = max(existing_versions, default=45) + 1

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_tool(
        self,
        name: str,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.root / "tools" / name), *arguments],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

    def generate_manifest(self) -> None:
        completed = self.run_tool("generate-current-manifest.py")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def write_post_baseline(
        self,
        version: int,
        *,
        directory_name: str | None = None,
        provenance: str = "POST_BASELINE",
        include_report: bool = True,
        include_output_record: bool = True,
        create_output: bool = True,
        executable_output: str | None = None,
        recorded_output: str | None = None,
    ) -> Path:
        directory = (
            self.root
            / "qualification"
            / "state-space"
            / "post-baseline"
            / (directory_name or f"v{version:03d}")
        )
        directory.mkdir(parents=True, exist_ok=True)
        stem = f"state-space-audit-v{version}"
        report = directory / f"{stem}.md"
        executable = directory / f"{stem}.py"
        output = directory / f"{stem}.txt"

        if include_report:
            report.write_text(
                f"# State-Space Audit v{version} — Test fixture\n\n"
                "This fixture exercises post-baseline qualification plumbing.\n"
            )
        actual_output = executable_output or f"state-space v{version}: PASS\n"
        executable.write_text(
            "#!/usr/bin/env python3\n"
            f"print({actual_output.rstrip()!r})\n"
        )
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        expected_output = recorded_output or actual_output
        if create_output:
            output.write_text(expected_output)

        artifacts: dict[str, dict[str, str]] = {
            "executable": {
                "path": executable.name,
                "sha256": sha256(executable),
            }
        }
        if include_report:
            artifacts["report"] = {
                "path": report.name,
                "sha256": sha256(report),
            }
        if include_output_record:
            artifacts["recorded_output"] = {
                "path": output.name,
                "sha256": sha256(output) if output.is_file() else "0" * 64,
            }

        metadata = {
            "$schema": "../qualification-metadata-v1.schema.json",
            "schema_version": 1,
            "qualification_id": f"state-space-v{version:03d}",
            "qualification_kind": "state-space",
            "provenance": provenance,
            "baseline": "ADR-080",
            "version": version,
            "artifacts": artifacts,
            "supporting_artifacts": [],
            "replay": {
                "runner": "python3",
                "expected_exit_code": 0,
                "stdout_sha256": sha256(output) if output.is_file() else "0" * 64,
            },
        }
        (directory / "qualification-metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n"
        )
        return directory

    def refresh_artifact_hash(self, directory: Path, role: str) -> None:
        metadata_path = directory / "qualification-metadata.json"
        metadata = json.loads(metadata_path.read_text())
        artifact = directory / metadata["artifacts"][role]["path"]
        digest = sha256(artifact)
        metadata["artifacts"][role]["sha256"] = digest
        if role == "recorded_output":
            metadata["replay"]["stdout_sha256"] = digest
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")

    def assert_layout_fails(self, expected: str) -> None:
        self.generate_manifest()
        completed = self.run_tool("verify-qualification-layout.py")
        self.assertNotEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(expected, completed.stdout + completed.stderr)

    def test_missing_post_baseline_version_is_rejected(self) -> None:
        missing = self.next_post_baseline_version
        self.write_post_baseline(missing + 1)
        self.assert_layout_fails(f"missing v{missing}")

    def test_incomplete_post_baseline_qualification_is_rejected(self) -> None:
        self.write_post_baseline(self.next_post_baseline_version, include_report=False)
        self.assert_layout_fails("artifacts must contain exactly")

    def test_duplicate_post_baseline_version_is_rejected(self) -> None:
        version = self.next_post_baseline_version
        self.write_post_baseline(version)
        self.write_post_baseline(version, directory_name=f"v{version:03d}-duplicate")
        self.assert_layout_fails(f"duplicate post-baseline version v{version}")

    def test_missing_recorded_output_is_rejected(self) -> None:
        self.write_post_baseline(self.next_post_baseline_version, create_output=False)
        self.assert_layout_fails("missing recorded_output artifact")

    def test_unregistered_post_baseline_artifact_is_rejected(self) -> None:
        version = self.next_post_baseline_version
        directory = self.root / f"qualification/state-space/post-baseline/v{version:03d}"
        directory.mkdir(parents=True)
        (directory / f"state-space-audit-v{version}.py").write_text("pass\n")
        self.assert_layout_fails("unregistered artifact")

    def test_modified_retained_artifact_is_rejected(self) -> None:
        retained = (
            self.root
            / "qualification"
            / "state-space"
            / "v045"
            / "state-space-audit-v45.txt"
        )
        retained.write_text(retained.read_text() + "tampered\n")
        self.assert_layout_fails("SHA mismatch for active artifact")

    def test_retained_source_cannot_be_relabelled(self) -> None:
        lineage_path = self.root / "qualification" / "lineage" / "lineage-v2.json"
        lineage = json.loads(lineage_path.read_text())
        artifact = next(
            item
            for item in lineage["artifacts"]
            if item["artifact_id"] == "state-space-v045-executable"
        )
        artifact["source"] = "adr070"
        lineage_path.write_text(json.dumps(lineage, indent=2) + "\n")
        self.assert_layout_fails("source differs from snapshot authority")

    def test_new_evidence_cannot_use_retained_directory_shape(self) -> None:
        version = self.next_post_baseline_version
        directory = self.root / "qualification" / "state-space" / f"v{version:03d}"
        directory.mkdir()
        (directory / f"state-space-audit-v{version}.py").write_text("pass\n")
        self.assert_layout_fails("retained discovery: unregistered artifact")

    def test_snapshot_backed_claim_for_new_evidence_is_rejected(self) -> None:
        self.write_post_baseline(self.next_post_baseline_version, provenance="RETAINED")
        self.assert_layout_fails("provenance must be POST_BASELINE")

    def test_post_baseline_artifact_symlink_is_rejected(self) -> None:
        version = self.next_post_baseline_version
        directory = self.write_post_baseline(version)
        report = directory / f"state-space-audit-v{version}.md"
        report.unlink()
        report.symlink_to(f"state-space-audit-v{version}.txt")
        self.refresh_artifact_hash(directory, "report")
        self.assert_layout_fails("report artifact must not be a symlink")

    def test_invalid_utf8_report_is_controlled_failure(self) -> None:
        version = self.next_post_baseline_version
        directory = self.write_post_baseline(version)
        report = directory / f"state-space-audit-v{version}.md"
        report.write_bytes(b"\xff\xfe")
        self.refresh_artifact_hash(directory, "report")
        self.assert_layout_fails("report is not valid UTF-8")

    def test_malformed_post_baseline_metadata_is_controlled_failure(self) -> None:
        directory = (
            self.root
            / "qualification"
            / "state-space"
            / "post-baseline"
            / f"v{self.next_post_baseline_version:03d}"
        )
        directory.mkdir(parents=True)
        (directory / "qualification-metadata.json").write_text("{\n")
        self.assert_layout_fails("invalid metadata")

    def test_metadata_schema_rejects_nonlocal_artifact_paths(self) -> None:
        schema_path = (
            self.root
            / "qualification"
            / "state-space"
            / "post-baseline"
            / "qualification-metadata-v1.schema.json"
        )
        schema = json.loads(schema_path.read_text())
        pattern = schema["$defs"]["artifact"]["properties"]["path"]["pattern"]
        self.assertIsNone(re.fullmatch(pattern, "../artifact"))
        self.assertIsNone(re.fullmatch(pattern, "fixtures/artifact"))
        self.assertIsNotNone(
            re.fullmatch(
                pattern,
                f"state-space-audit-v{self.next_post_baseline_version}.py",
            )
        )

    def test_malformed_active_lineage_is_controlled_failure(self) -> None:
        lineage = self.root / "qualification" / "lineage" / "lineage-v2.json"
        lineage.write_text("{\n")
        completed = self.run_tool("verify-qualification-layout.py")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("lineage: invalid JSON", completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_local_virtual_environments_are_excluded_from_active_manifest(self) -> None:
        markers = [
            self.root / ".venv" / "bin" / "root-environment-specific",
            self.root
            / "tools"
            / "fixtures"
            / ".venv"
            / "bin"
            / "nested-environment-specific",
        ]
        for marker in markers:
            marker.parent.mkdir(parents=True)
            marker.write_text("must not enter the active manifest\n")

        self.generate_manifest()

        manifest = (
            self.root / "qualification" / "manifests" / "current.sha256"
        ).read_text()
        self.assertNotIn(".venv/", manifest)
        self.assertNotIn("environment-specific", manifest)
        completed = self.run_tool("verify-qualification-layout.py")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_stale_active_manifest_is_rejected(self) -> None:
        self.generate_manifest()
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n")
        completed = self.run_tool("verify-qualification-layout.py")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("SHA mismatch AGENTS.md", completed.stdout)

    def test_broken_markdown_link_is_rejected(self) -> None:
        readme = self.root / "qualification" / "README.md"
        readme.write_text(readme.read_text() + "\n[broken](missing-target.md)\n")
        completed = self.run_tool("verify-markdown-links.py")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("missing link target", completed.stdout)

    def test_ci_seals_snapshot_before_layout_verification(self) -> None:
        workflow = (self.root / ".github/workflows/qualification.yml").read_text()
        seal = workflow.index("chmod -R a-w qualification/releases/adr-080-flat")
        verify = workflow.index("python3 tools/verify-qualification-layout.py")
        self.assertLess(seal, verify)

    def test_git_smoke_runner_handles_canonical_temporary_paths(self) -> None:
        completed = self.run_tool("replay-git-smokes.py")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("git-native-observation-smoke-v5.sh: PASS", completed.stdout)

    def test_unsupported_git_version_is_not_a_pass(self) -> None:
        fake_bin = Path(self.temporary.name) / "bin"
        fake_bin.mkdir()
        fake_git = fake_bin / "git"
        fake_git.write_text("#!/usr/bin/env sh\necho 'git version 2.27.0'\n")
        fake_git.chmod(fake_git.stat().st_mode | stat.S_IXUSR)
        environment = os.environ.copy()
        environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"
        completed = self.run_tool(
            "replay-git-smokes.py",
            "--check-version",
            environment=environment,
        )
        self.assertEqual(completed.returncode, 3)
        self.assertIn("UNSUPPORTED_GIT_VERSION", completed.stdout)
        self.assertNotIn("PASS", completed.stdout)

    def test_post_baseline_replay_must_match_recorded_output(self) -> None:
        version = self.next_post_baseline_version
        self.write_post_baseline(
            version,
            executable_output=f"state-space v{version}: FAIL\n",
            recorded_output=f"state-space v{version}: PASS\n",
        )
        completed = self.run_tool("replay-post-baseline-qualification.py")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("RECORDED_OUTPUT_MISMATCH", completed.stdout)

    def test_contiguous_post_baseline_qualifications_verify_and_replay(self) -> None:
        first = self.next_post_baseline_version
        self.write_post_baseline(first)
        self.write_post_baseline(first + 1)
        self.generate_manifest()
        verified = self.run_tool("verify-qualification-layout.py")
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        replayed = self.run_tool("replay-post-baseline-qualification.py")
        self.assertEqual(replayed.returncode, 0, replayed.stdout + replayed.stderr)
        expected = self.existing_post_baseline_count + 2
        self.assertIn(f"PASS ({expected} qualifications)", replayed.stdout)

    def test_historical_latest_is_derived_from_lineage(self) -> None:
        completed = self.run_tool("replay-historical-qualification.py", "latest")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("v45 total: 16380 PASS", completed.stdout)

    def test_malformed_historical_lineage_is_controlled_failure(self) -> None:
        lineage = (
            self.root
            / "qualification"
            / "releases"
            / "adr-080-flat"
            / "QUALIFICATION-LINEAGE.json"
        )
        lineage.chmod(lineage.stat().st_mode | stat.S_IWUSR)
        lineage.write_text("{\n")
        completed = self.run_tool("replay-historical-qualification.py", "latest")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("INVALID_HISTORICAL_LINEAGE", completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_historical_replay_rejects_modified_recorded_output(self) -> None:
        output = (
            self.root
            / "qualification"
            / "releases"
            / "adr-080-flat"
            / "state-space-audit-v45.txt"
        )
        output.chmod(output.stat().st_mode | stat.S_IWUSR)
        output.write_text(output.read_text() + "tampered\n")
        completed = self.run_tool("replay-historical-qualification.py", "latest")
        self.assertEqual(completed.returncode, 6)
        self.assertIn("HISTORICAL_ARTIFACT_HASH_MISMATCH", completed.stdout)

    def test_missing_historical_baseline_is_not_a_pass(self) -> None:
        completed = self.run_tool("replay-historical-qualification.py", "37")
        self.assertEqual(completed.returncode, 3)
        self.assertIn("NON_REPLAYABLE_MISSING_BASELINE", completed.stdout)
        self.assertNotIn("PASS", completed.stdout)

    def test_historical_baseline_hash_mismatch_is_not_a_pass(self) -> None:
        archive = Path(self.temporary.name) / "wrong-baseline.tar"
        archive.write_bytes(b"not the admitted package")
        completed = self.run_tool(
            "replay-historical-qualification.py",
            "37",
            "--baseline-archive",
            str(archive),
        )
        self.assertEqual(completed.returncode, 4)
        self.assertIn("BASELINE_HASH_MISMATCH", completed.stdout)
        self.assertNotIn("PASS", completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
