#!/usr/bin/env python3
"""Consumer tests for the Ruu Governed Objects profile."""

from __future__ import annotations

from pathlib import Path
import unittest

import yaml
from proto_ring import governance_authority, governed_objects
from proto_ring import repository_governance_model

ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    ROOT
    / "docs"
    / "repository-governance"
    / "ruu-governed-objects.md"
)
CONTRACT_COMMIT = "275a92523e37b30fabd060ec92df2706bb70ef80"


def load_profiles():
    model = repository_governance_model.load(ROOT)
    authority_route = model.capabilities["governance_authority"].routes["profile"]
    authority = governance_authority.load(ROOT, authority_route)
    catalog_route = model.capabilities["governed_objects"].routes["profile"]
    catalog = governed_objects.load(ROOT, catalog_route, authority)
    return model, authority, catalog


class GovernedObjectsProfileTests(unittest.TestCase):
    def test_profile_pins_contract_and_is_routed_exactly(self) -> None:
        model, _authority, catalog = load_profiles()
        route = model.capabilities["governed_objects"].routes["profile"]

        self.assertEqual(
            "docs/repository-governance/ruu-governed-objects.md",
            route.declared_path,
        )
        self.assertEqual(PROFILE_PATH.resolve(), route.target)
        self.assertEqual(PROFILE_PATH.resolve(), catalog.carrier)

        _prefix, frontmatter, _body = PROFILE_PATH.read_text(
            encoding="utf-8"
        ).split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        self.assertEqual(
            {
                "repository": "fanilosendrison/proto-ring",
                "commit": CONTRACT_COMMIT,
                "path": "docs/contracts/governed-objects.md",
            },
            metadata["governed_objects_contract"],
        )

    def test_governance_authority_owns_only_profile_route(self) -> None:
        _model, authority, _catalog = load_profiles()
        responsibility = authority.responsibilities[
            "governed_objects_profile_route"
        ]

        self.assertEqual(
            {"agents_governance_frontmatter": governance_authority.SourceRole.AUTHORITY},
            responsibility.roles,
        )
        self.assertEqual((), responsibility.precedence)

    def test_catalog_has_only_canonical_adr_objects(self) -> None:
        _model, _authority, catalog = load_profiles()

        self.assertEqual({"architecture_decisions"}, set(catalog.interfaces))
        self.assertEqual(
            {f"ADR-{number:03d}" for number in range(1, 91)},
            set(catalog.interfaces["architecture_decisions"].objects),
        )

    def test_accepted_and_superseded_responsibilities_are_exact(self) -> None:
        _model, _authority, catalog = load_profiles()
        objects = catalog.interfaces["architecture_decisions"].objects

        self.assertEqual(
            frozenset({"adr_metadata"}),
            objects["ADR-031"].responsibilities,
        )
        for identity, governed_object in objects.items():
            with self.subTest(identity=identity):
                if identity != "ADR-031":
                    self.assertEqual(
                        frozenset(
                            {
                                "adr_metadata",
                                "product_semantics",
                                "accepted_decisions",
                            }
                        ),
                        governed_object.responsibilities,
                    )
                self.assertEqual(frozenset(), governed_object.relations)


if __name__ == "__main__":
    unittest.main(verbosity=2)
