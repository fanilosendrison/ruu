#!/usr/bin/env python3
"""Core negative paths and live checks for Ruu's native provider boundary."""
from __future__ import annotations
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest
from unittest import mock
ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
EXPECTED = "4ae1a2a549d7dae8e4cce7f727b9bc5330f3823f"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import proto_ring_executable_binding as boundary
import proto_ring_result_validation as result_shapes
from proto_ring_source_test_support import source_fixture, source_git, symlinked_git_source
def load_script(name: str):
    path = TOOLS / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
checker = load_script("check-proto-ring-provider.py")
ProcessScopedProviderRealizationTests = load_script(
    "tests/test-process-scoped-provider-realization.py"
).ProcessScopedProviderRealizationTests
from proto_ring_preparation_tests import NativeProviderPreparationTests  # noqa: E402,F401
def fake_executable(directory: str, responses: list[object], exit_code: int = 0) -> Path:
    path = Path(directory) / "fake-proto-ring"
    lines = "".join(json.dumps(response) + "\n" for response in responses)
    script = (
        "#!/usr/bin/env python3\n"
        "import json,sys\n"
        "json.load(sys.stdin)\n"
        f"sys.stdout.write({lines!r})\n"
        f"raise SystemExit({exit_code})\n"
    )
    path.write_text(script)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def result(operation: str, value: object, *, version: int = 1) -> dict[str, object]:
    return {
        "transport_version": version,
        "operation": operation,
        "outcome": "result",
        "value": value,
    }


class NativeProviderCoreNegativePathTests(unittest.TestCase):
    """The exact 33 qualified fail-closed provider regressions."""

    def setUp(self) -> None:
        boundary._clear_process_realizations_for_tests()
        self.binding = boundary.ExecutableProviderBinding(
            "fanilosendrison/proto-ring", EXPECTED
        )

    def _source_git(self, **arguments):
        return source_git(EXPECTED, **arguments)

    def _binding_fixture(self, temporary: str, old: str, new: str) -> Path:
        root = Path(temporary)
        target = root / "docs/repository-governance/ruu-governance-bindings.md"
        target.parent.mkdir(parents=True)
        text = (ROOT / "docs/repository-governance/ruu-governance-bindings.md").read_text()
        self.assertEqual(1, text.count(old))
        target.write_text(text.replace(old, new, 1))
        return root

    def test_01_missing_provider_realization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(os.environ, {"XDG_CACHE_HOME": temporary}):
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary.realized_provider(ROOT)

    def test_02_missing_binary(self) -> None:
        manifest = {"repository": self.binding.repository, "commit": EXPECTED, "transport_version": 1, "binary_sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(boundary, "load_executable_provider_binding", return_value=self.binding), mock.patch.object(boundary, "managed_provider_root", return_value=Path(temporary)), mock.patch.object(boundary, "_read_manifest", return_value=manifest):
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "absent"):
                boundary.realized_provider(ROOT)

    def test_03_malformed_realization_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "realization.json"
            path.write_text("not-json")
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._read_manifest(path)

    def test_04_noncanonical_manifest_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "realization.json"
            path.write_text('{"repository": "x"}\n')
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "not canonical"):
                boundary._read_manifest(path)

    def test_05_manifest_repository_mismatch(self) -> None:
        self._manifest_mismatch("repository", "other/repository")

    def test_06_manifest_commit_mismatch(self) -> None:
        self._manifest_mismatch("commit", "b" * 40)

    def test_07_manifest_transport_version_mismatch(self) -> None:
        self._manifest_mismatch("transport_version", 2)
        self._manifest_mismatch("transport_version", True)

    def _manifest_mismatch(self, key: str, bad: object) -> None:
        manifest = {"repository": self.binding.repository, "commit": EXPECTED, "transport_version": 1, "binary_sha256": "a" * 64}
        manifest[key] = bad
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "binary"
            binary.write_bytes(b"binary")
            with mock.patch.object(boundary, "load_executable_provider_binding", return_value=self.binding), mock.patch.object(boundary, "managed_provider_root", return_value=Path(temporary)), mock.patch.object(boundary, "_read_manifest", return_value=manifest), mock.patch.object(boundary, "_binary_path", return_value=binary):
                with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "manifest does not match"):
                    boundary.realized_provider(ROOT)

    def test_08_binary_sha_mismatch(self) -> None:
        manifest = {"repository": self.binding.repository, "commit": EXPECTED, "transport_version": 1, "binary_sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "binary"
            binary.write_bytes(b"binary")
            with mock.patch.object(boundary, "load_executable_provider_binding", return_value=self.binding), mock.patch.object(boundary, "managed_provider_root", return_value=Path(temporary)), mock.patch.object(boundary, "_read_manifest", return_value=manifest), mock.patch.object(boundary, "_binary_path", return_value=binary):
                with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "digest"):
                    boundary.realized_provider(ROOT)

    def test_09_provider_source_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._source_is_exact(Path(temporary) / "missing", self.binding)

    def test_10_provider_source_head_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first, second = self._source_git(head="b" * 40)
            with first, second, self.assertRaisesRegex(boundary.ProtoRingExecutableError, "HEAD"):
                boundary._source_is_exact(source_fixture(temporary), self.binding)

    def test_11_provider_source_not_detached(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first, second = self._source_git(detached=False)
            with first, second, self.assertRaisesRegex(boundary.ProtoRingExecutableError, "detached"):
                boundary._source_is_exact(source_fixture(temporary), self.binding)

    def test_12_provider_source_origin_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first, second = self._source_git(origin="https://example.invalid/repo.git")
            with first, second, self.assertRaisesRegex(boundary.ProtoRingExecutableError, "origin"):
                boundary._source_is_exact(source_fixture(temporary), self.binding)
        with tempfile.TemporaryDirectory() as temporary:
            source = symlinked_git_source(temporary)
            first, second = self._source_git()
            with first, second, self.assertRaisesRegex(
                boundary.ProtoRingExecutableError, "Git directory is redirected"
            ):
                boundary._source_is_exact(source, self.binding)

    def test_13_tracked_dirty_source(self) -> None:
        self._assert_dirty("tracked", "")
        with tempfile.TemporaryDirectory() as temporary:
            first, second = self._source_git(index_entries="S Cargo.toml")
            with first, second, self.assertRaisesRegex(
                boundary.ProtoRingExecutableError, "non-ordinary"
            ):
                boundary._source_is_exact(source_fixture(temporary), self.binding)
        with tempfile.TemporaryDirectory() as temporary:
            source = source_fixture(temporary)
            (source / "Cargo.toml").write_text("substituted bytes")
            tree = "100644 blob " + "0" * 40 + " Cargo.toml"
            first, second = self._source_git(tree_listing=tree)
            with first, second, self.assertRaisesRegex(
                boundary.ProtoRingExecutableError, "bytes differ"
            ):
                boundary._source_is_exact(source, self.binding)

    def test_14_cached_dirty_source(self) -> None:
        self._assert_dirty("cached", "")

    def test_15_untracked_source_input(self) -> None:
        self._assert_dirty(None, "?? input")
        with tempfile.TemporaryDirectory() as temporary:
            first, second = self._source_git(replacement="refs/replace/" + EXPECTED)
            with first, second, self.assertRaisesRegex(
                boundary.ProtoRingExecutableError, "replacement refs"
            ):
                boundary._source_is_exact(source_fixture(temporary), self.binding)

    def test_16_ignored_source_input(self) -> None:
        self._assert_dirty(None, "!! input")

    def _assert_dirty(self, dirty: str | None, status: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first, second = self._source_git(dirty=dirty, status=status)
            with first, second, self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._source_is_exact(source_fixture(temporary), self.binding)

    def test_17_engine_identity_repository_mismatch(self) -> None:
        self._identity_mismatch("source_repository", "other/repository")

    def test_18_engine_identity_commit_mismatch(self) -> None:
        self._identity_mismatch("source_commit", "b" * 40)

    def test_19_engine_identity_transport_mismatch(self) -> None:
        self._identity_mismatch("transport_version", 2)
        self._identity_mismatch("transport_version", True)

    def _identity_mismatch(self, key: str, bad: object) -> None:
        value = {"source_repository": self.binding.repository, "source_commit": EXPECTED, "transport_version": 1}
        value[key] = bad
        with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "identity"):
            boundary._validate_identity({"value": value}, self.binding)

    def test_20_relative_xdg_cache_home_rejected(self) -> None:
        with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": "relative"}):
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "absolute"):
                boundary.cache_base()

    def test_21_invalid_binding_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._binding_fixture(
                temporary,
                "identity:\n        repository: fanilosendrison/proto-ring\n        commit: " + EXPECTED,
                "identity:\n        repository: other/proto-ring\n        commit: " + EXPECTED,
            )
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "repository"):
                boundary.load_executable_provider_binding(root)

    def test_22_invalid_binding_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._binding_fixture(temporary, f"commit: {EXPECTED}", "commit: main")
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "40 lowercase"):
                boundary.load_executable_provider_binding(root)

    def test_23_invalid_binding_kind(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._binding_fixture(temporary, "kind: executable_provider", "kind: governance_contract")
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "kind or scope"):
                boundary.load_executable_provider_binding(root)

    def test_24_invalid_binding_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._binding_fixture(
                temporary,
                "proto_ring_executable:\n      kind: executable_provider\n      scope:\n        kind: logical_provider",
                "proto_ring_executable:\n      kind: executable_provider\n      scope:\n        kind: capability",
            )
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "kind or scope"):
                boundary.load_executable_provider_binding(root)

    def test_25_invalid_binding_authority_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._binding_fixture(
                temporary,
                "responsibility: executable_provider_binding\n        source: governance_binding_registry",
                "responsibility: executable_provider_binding\n        source: executable_dependency_manifest",
            )
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "authority"):
                boundary.load_executable_provider_binding(root)

    def test_26_transport_malformed_response(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, ["not-an-object"])
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_27_wrong_response_count(self) -> None:
        value = result("engine.identity", {"source_repository": self.binding.repository, "source_commit": EXPECTED, "transport_version": 1})
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, [value, value])
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_28_wrong_transport_version(self) -> None:
        responses = [
            (result("engine.identity", {}, version=2), 0),
            (result("engine.identity", {}, version=True), 0),
            (
                {
                    "transport_version": True,
                    "operation": "engine.identity",
                    "outcome": "controlled_failure",
                    "error": {"category": "invalid_input", "stage": None, "detail": "bad"},
                },
                0,
            ),
            (
                {
                    "transport_version": True,
                    "operation": "engine.identity",
                    "outcome": "transport_error",
                    "error": {"category": "invalid_request"},
                },
                2,
            ),
        ]
        for value, exit_code in responses:
            with self.subTest(outcome=value["outcome"], version=value["transport_version"]):
                with tempfile.TemporaryDirectory() as temporary:
                    binary = fake_executable(temporary, [value], exit_code=exit_code)
                    with self.assertRaises(boundary.ProtoRingExecutableError):
                        boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_29_wrong_operation(self) -> None:
        value = result("other.operation", {})
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, [value])
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_30_invalid_transport_exit_semantics(self) -> None:
        value = result("engine.identity", {})
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, [value], exit_code=1)
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_31_controlled_failure_shape_invalid(self) -> None:
        value = {"transport_version": 1, "operation": "engine.identity", "outcome": "controlled_failure", "error": {"category": 7}}
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, [value])
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_32_internal_failure_exit_handling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, [], exit_code=70)
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "internally"):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_33_currentness_does_not_prepare_implicitly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(os.environ, {"XDG_CACHE_HOME": temporary}), mock.patch("subprocess.run") as run:
            errors = checker.check(ROOT)
            self.assertTrue(errors)
            run.assert_not_called()
            self.assertEqual([], list(Path(temporary).iterdir()))

    def tearDown(self) -> None:
        boundary._clear_process_realizations_for_tests()

class NativeProviderPositiveTests(unittest.TestCase):
    def setUp(self) -> None:
        boundary._clear_process_realizations_for_tests()

    def tearDown(self) -> None:
        boundary._clear_process_realizations_for_tests()

    def test_live_native_provider_matches_authority(self) -> None:
        binding = boundary.load_executable_provider_binding(ROOT)
        self.assertEqual(EXPECTED, binding.commit)
        self.assertEqual([], checker.check(ROOT))

    def test_rgs_summary_and_complete_shapes_are_closed(self) -> None:
        summary = boundary.invoke_compat_result(
            ROOT,
            "repository-governance-state.compose",
            {"repository": str(ROOT)},
        )
        self.assertEqual(
            {"stage", "identity_present", "scope_paths", "components", "bindings"},
            set(summary),
        )
        self.assertNotIn("state", summary)
        request = {"repository": str(ROOT), "projection": "complete"}
        complete = boundary.invoke_compat_result(
            ROOT, "repository-governance-state.compose", request
        )
        unknown = copy.deepcopy(complete)
        unknown["state"]["repository_governance_model"]["provider"]["unknown"] = True
        with self.assertRaises(result_shapes.ProtoRingResultShapeError):
            result_shapes.validate_result(
                "repository-governance-state.compose", request, unknown
            )
        missing = copy.deepcopy(complete)
        del missing["state"]["projection_registry"]["projections"]["adr_index"]["mode"]
        with self.assertRaises(result_shapes.ProtoRingResultShapeError):
            result_shapes.validate_result(
                "repository-governance-state.compose", request, missing
            )

    def test_checker_has_no_python_package_or_override_authority(self) -> None:
        source = (TOOLS / "check-proto-ring-provider.py").read_text()
        boundary_source = (TOOLS / "proto_ring_executable_binding.py").read_text()
        self.assertNotIn("direct_url.json", source)
        self.assertNotIn("metadata.distribution", source)
        self.assertNotIn("PROTO_RING_BINARY", boundary_source)

    def test_cli_rejects_arguments(self) -> None:
        self.assertEqual(1, checker.main(["unexpected"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
