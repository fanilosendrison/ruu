#!/usr/bin/env python3
"""Mechanical checks for Ruu's local Projection Integrity bindings."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from proto_ring.adr_metadata import parse_adr

REPOSITORY = Path(__file__).resolve().parents[2]
POLICY = REPOSITORY / "docs/repository-governance/ruu-projection-integrity.md"
HISTORY = REPOSITORY / "docs/adr/README.md"
ADR_DIRECTORY = REPOSITORY / "docs/adr"
ENTRY = re.compile(
    r"(?m)^- \[(?P<id>ADR-[0-9]{3})(?:: | — )(?P<name>.+?)\]"
    r"\((?P<path>[^)]+)\) — (?P<status>[A-Za-z-]+)"
)


class ProjectionIntegrityTests(unittest.TestCase):
    def test_policy_binds_immutable_shared_contract(self) -> None:
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn(
            "fanilosendrison/proto-ring\n"
            "ae8d05935553086b68d5d832dc9d3317328f0c89\n"
            "docs/contracts/projection-integrity.md",
            policy,
        )
        for local_boundary in (
            "Ruu owner mappings",
            "Qualification and evidence boundary",
            "Active manifest",
            "Immutable retained evidence",
            "Repository Integrity profile",
        ):
            with self.subTest(local_boundary=local_boundary):
                self.assertIn(local_boundary, policy)

    def test_annotated_history_matches_canonical_adr_fields(self) -> None:
        entries = [match.groupdict() for match in ENTRY.finditer(HISTORY.read_text())]
        canonical = []
        for path in sorted(ADR_DIRECTORY.glob("adr-[0-9][0-9][0-9]-*.md")):
            metadata, _body = parse_adr(path)
            canonical.append(
                {
                    "id": metadata["id"],
                    "name": metadata["name"],
                    "path": path.name,
                    "status": metadata["status"],
                }
            )

        self.assertEqual(
            [record["id"] for record in canonical],
            [entry["id"] for entry in entries],
        )
        for expected, actual in zip(canonical, entries, strict=True):
            with self.subTest(adr_id=expected["id"]):
                self.assertEqual(expected["name"], actual["name"])
                self.assertEqual(expected["path"], actual["path"])
                self.assertEqual(
                    str(expected["status"]).lower(),
                    actual["status"].lower(),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
