#!/usr/bin/env python3
"""Tests for Ruu's executable binding registry currentness check."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
CHECKER = TOOLS / "check-proto-ring-binding-registry.py"
EXPECTED = "dedb01a3a9b7a18930c9da75afa3773b5ad67f69"
OTHER = "b" * 40
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


def make_fixture(temporary: str) -> Path:
    root = Path(temporary) / "repository"
    shutil.copytree(
        ROOT,
        root,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc"),
    )
    subprocess.run(
        ["git", "init", "-q", str(root)],
        check=True,
    )
    return root


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(old) < 1:
        raise AssertionError(f"fixture text not found: {old}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


class ProtoRingBindingRegistryTests(unittest.TestCase):
    def test_live_registry_copy_matches_requirements_authority(self) -> None:
        self.assertEqual(EXPECTED, checker.authoritative_proto_ring_commit(ROOT))
        self.assertEqual(EXPECTED, checker.binding_registry_proto_ring_commit(ROOT))
        self.assertEqual([], checker.check(ROOT))

    def test_registry_copy_stale_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = root / "docs/repository-governance/ruu-governance-bindings.md"
            replace_once(registry, EXPECTED, OTHER)
            self.assertIn("differs", checker.check(root)[0])

    def test_requirements_pin_changed_only_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            replace_once(root / "requirements.txt", EXPECTED, OTHER)
            self.assertIn("differs", checker.check(root)[0])

    def test_conflicting_requirement_declaration_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            requirements = root / "requirements.txt"
            requirements.write_text(
                requirements.read_text()
                + "proto_ring @ git+https://github.com/other/proto-ring.git@main\n"
            )
            self.assertIn("one exact", checker.check(root)[0])

    def test_missing_stable_binding_id_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = root / "docs/repository-governance/ruu-governance-bindings.md"
            replace_once(
                registry,
                "    proto_ring_executable:\n",
                "    renamed_proto_ring_executable:\n",
            )
            self.assertIn("proto_ring_executable", checker.check(root)[0])

    def test_checker_has_no_installed_provider_responsibility(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("importlib", source)
        self.assertNotIn("metadata.distribution", source)
        self.assertNotIn("direct_url.json", source)

    def test_cli_executes_live_routed_check(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("proto-ring binding registry: OK", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
