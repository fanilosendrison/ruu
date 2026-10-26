#!/usr/bin/env python3
"""Tests for Ruu's authoritative executable binding projection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
CHECKER = TOOLS / "check-proto-ring-binding-registry.py"
EXPECTED = "4ae1a2a549d7dae8e4cce7f727b9bc5330f3823f"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def load_checker():
    spec = importlib.util.spec_from_file_location("check_binding_registry", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


class ProtoRingBindingRegistryTests(unittest.TestCase):
    def test_live_registry_is_native_provider_authority(self) -> None:
        binding = checker.load_executable_provider_binding(ROOT)
        self.assertEqual("fanilosendrison/proto-ring", binding.repository)
        self.assertEqual(EXPECTED, binding.commit)
        self.assertEqual([], checker.check(ROOT))

    def test_complete_projected_binding_is_exact(self) -> None:
        state = checker.invoke_compat_result(
            ROOT,
            "repository-governance-state.compose",
            {"repository": str(ROOT), "binding_ids": [checker.PROTO_RING_BINDING_ID]},
        )
        projected = state["bindings"][checker.PROTO_RING_BINDING_ID]
        self.assertEqual(EXPECTED, projected["identity"]["commit"])
        self.assertEqual("governance_binding_registry", projected["authority"]["source"])
        self.assertEqual("executable_provider_binding", projected["authority"]["responsibility"])

    def test_missing_binding_fails_closed(self) -> None:
        with mock.patch.object(
            checker,
            "load_executable_provider_binding",
            side_effect=checker.ProtoRingExecutableError("missing binding"),
        ):
            self.assertEqual(["missing binding"], checker.check(ROOT))

    def test_checker_has_no_python_package_authority(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("requirements.txt", source)
        self.assertNotIn("metadata.distribution", source)
        self.assertNotIn("direct_url.json", source)

    def test_cli_executes_live_routed_check(self) -> None:
        self.assertEqual(0, checker.main([]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
