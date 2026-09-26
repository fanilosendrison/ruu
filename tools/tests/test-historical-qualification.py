#!/usr/bin/env python3
"""Regression tests for retained historical qualification replay."""

from __future__ import annotations

import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]


class HistoricalQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="ruu-historical-tests-")
        self.root = Path(self.temporary.name) / "ruu"
        shutil.copytree(
            REPOSITORY,
            self.root,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_replay(
        self, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.root / "tools/replay-historical-qualification.py"),
                *arguments,
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_latest_is_derived_from_lineage(self) -> None:
        completed = self.run_replay("latest")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("v45 total: 16380 PASS", completed.stdout)

    def test_malformed_lineage_is_controlled_failure(self) -> None:
        lineage = (
            self.root
            / "qualification"
            / "releases"
            / "adr-080-flat"
            / "QUALIFICATION-LINEAGE.json"
        )
        lineage.chmod(lineage.stat().st_mode | stat.S_IWUSR)
        lineage.write_text("{\n")
        completed = self.run_replay("latest")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("INVALID_HISTORICAL_LINEAGE", completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_modified_recorded_output_is_rejected(self) -> None:
        output = (
            self.root
            / "qualification"
            / "releases"
            / "adr-080-flat"
            / "state-space-audit-v45.txt"
        )
        output.chmod(output.stat().st_mode | stat.S_IWUSR)
        output.write_text(output.read_text() + "tampered\n")
        completed = self.run_replay("latest")
        self.assertEqual(completed.returncode, 6)
        self.assertIn("HISTORICAL_ARTIFACT_HASH_MISMATCH", completed.stdout)

    def test_missing_baseline_is_not_a_pass(self) -> None:
        completed = self.run_replay("37")
        self.assertEqual(completed.returncode, 3)
        self.assertIn("NON_REPLAYABLE_MISSING_BASELINE", completed.stdout)
        self.assertNotIn("PASS", completed.stdout)

    def test_baseline_hash_mismatch_is_not_a_pass(self) -> None:
        archive = Path(self.temporary.name) / "wrong-baseline.tar"
        archive.write_bytes(b"not the admitted package")
        completed = self.run_replay(
            "37",
            "--baseline-archive",
            str(archive),
        )
        self.assertEqual(completed.returncode, 4)
        self.assertIn("BASELINE_HASH_MISMATCH", completed.stdout)
        self.assertNotIn("PASS", completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
