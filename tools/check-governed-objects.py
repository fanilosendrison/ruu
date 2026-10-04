#!/usr/bin/env python3
"""Validate the routed Ruu Governed Objects profile."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import governed_objects, repository_governance_state


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        state = repository_governance_state.load(ROOT)
        objects = state.governed_objects
        if objects is None:
            raise governed_objects.GovernedObjectsError(
                "governed_objects capability is required"
            )
    except (
        repository_governance_state.RepositoryGovernanceStateError,
        governed_objects.GovernedObjectsError,
    ) as error:
        print(f"ERROR: governed objects: {error}", file=sys.stderr)
        return 1

    print("governed objects: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
