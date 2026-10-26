#!/usr/bin/env python3
"""Probe current Ruu native Repository Integrity obligation cardinality."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def _load_runner():
    path = TOOLS / "check-repository-integrity.py"
    spec = importlib.util.spec_from_file_location("check_repository_integrity", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    runner = _load_runner()
    result = runner.run_validation(ROOT)
    expected = runner._expected_validation_ids(ROOT)
    validations = result.get("validations")
    obligations = result.get("obligations")
    if (
        not runner._coherent_pass(result, ROOT)
        or expected is None
        or not isinstance(validations, list)
        or not isinstance(obligations, list)
        or len(validations) != 25
        or len(obligations) != 28
    ):
        print("current Repository Integrity cardinality: FAILED", file=sys.stderr)
        return 1
    by_id = {validation["id"]: validation for validation in validations}
    json_obligations = by_id["json_syntax"]["obligations"]
    if (
        len(json_obligations) != 4
        or sum(item["id"] == "json_syntax" for item in obligations) != 4
        or any(
            len(validation["obligations"]) != 1
            for validation in validations
            if validation["id"] != "json_syntax"
        )
        or obligations
        != [
            obligation
            for validation in validations
            for obligation in validation["obligations"]
        ]
    ):
        print("current Repository Integrity cardinality: FAILED", file=sys.stderr)
        return 1
    print("REPOSITORY_INTEGRITY_VALIDATION_COUNT=25")
    print("CURRENT_RUU_CONCRETE_OBLIGATION_COUNT=28")
    print("CURRENT_RUU_JSON_SYNTAX_OBLIGATIONS=4")
    print("TOP_LEVEL_OBLIGATIONS_EQUAL_EXACT_FLATTEN=YES")
    print("current Repository Integrity cardinality: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
