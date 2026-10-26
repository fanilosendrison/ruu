#!/usr/bin/env python3
"""Consumer tests for Ruu's native Governed Objects projection."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_structured_governance_import import load_structured_governance


class GovernedObjectsProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model, cls.authority, cls.catalog, *_rest = load_structured_governance(ROOT)

    def test_profile_is_routed_exactly(self) -> None:
        route = self.model["capabilities"]["governed_objects"]["routes"]["profile"]
        self.assertEqual("docs/repository-governance/ruu-governed-objects.md", route["declared_path"])
        self.assertEqual(route["declared_path"], route["resolved_target"])

    def test_governance_authority_owns_only_profile_route(self) -> None:
        responsibility = self.authority["responsibilities"]["governed_objects_profile_route"]
        self.assertEqual({"agents_governance_frontmatter": "authority"}, responsibility["roles"])
        self.assertEqual([], responsibility["precedence"])

    def test_catalog_has_only_canonical_adr_objects(self) -> None:
        self.assertEqual({"architecture_decisions"}, set(self.catalog["interfaces"]))
        objects = self.catalog["interfaces"]["architecture_decisions"]["objects"]
        self.assertEqual({f"ADR-{number:03d}" for number in range(1, 95)}, set(objects))

    def test_accepted_and_superseded_responsibilities_are_exact(self) -> None:
        objects = self.catalog["interfaces"]["architecture_decisions"]["objects"]
        self.assertEqual({"adr_metadata"}, set(objects["ADR-031"]["responsibilities"]))
        for identity, governed_object in objects.items():
            with self.subTest(identity=identity):
                if identity != "ADR-031":
                    self.assertEqual(
                        {"adr_metadata", "product_semantics", "accepted_decisions"},
                        set(governed_object["responsibilities"]),
                    )
                self.assertEqual([], governed_object["relations"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
