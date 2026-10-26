#!/usr/bin/env python3
"""Consume Ruu's complete routed governance state through native proto-ring."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result

ROOT = Path(__file__).resolve().parents[1]
_COMPONENTS = (
    "repository_governance_model",
    "governance_authority",
    "governed_objects",
    "governance_bindings",
    "repository_integrity",
    "projection_registry",
    "evidence_requirements",
)


def load_structured_governance(root: Path = ROOT) -> tuple[dict[str, object], ...]:
    """Return the seven plain complete-state components in historical tuple order."""

    value = invoke_compat_result(
        root,
        "repository-governance-state.compose",
        {"repository": str(root), "projection": "complete"},
    )
    state = value["state"]
    components = tuple(state[name] for name in _COMPONENTS)
    if not all(isinstance(component, dict) for component in components):
        raise ProtoRingExecutableError("complete governance state requires seven components")
    return components


def check(root: Path = ROOT) -> list[str]:
    try:
        load_structured_governance(root)
    except ProtoRingExecutableError as error:
        return [str(error)]
    return []


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: structured governance: {error}", file=sys.stderr)
        print("structured governance: FAILED", file=sys.stderr)
        return 1
    print("structured governance: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
