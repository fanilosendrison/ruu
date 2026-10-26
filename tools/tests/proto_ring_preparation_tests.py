"""Provider-preparation tests imported by the native-provider test carrier."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import proto_ring_execution_custody as execution_custody  # noqa: E402
import proto_ring_executable_binding as boundary  # noqa: E402
import proto_ring_source_realization as source_realization  # noqa: E402
from proto_ring_executable_binding import ProtoRingExecutableError  # noqa: E402


def _load_preparer():
    path = TOOLS / "prepare-proto-ring-provider.py"
    spec = importlib.util.spec_from_file_location("prepare_proto_ring_provider", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREPARER = _load_preparer()


class NativeProviderPreparationTests(unittest.TestCase):
    def test_provider_toolchain_uses_exact_source_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "rust-toolchain.toml").write_text(
                '[toolchain]\nchannel = "1.99.0"\nprofile = "minimal"\n'
            )
            with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                PREPARER.shutil, "which", return_value="/trusted/bin/rustup"
            ), mock.patch.object(
                PREPARER,
                "_run",
                side_effect=[
                    "/toolchains/1.99.0/bin/rustc",
                    "/toolchains/1.99.0/bin/cargo",
                    "rustc 1.99.0 (abc 2026-01-01)",
                    "cargo 1.99.0 (def 2026-01-01)",
                ],
            ) as run:
                actual = PREPARER._provider_toolchain(source)
        self.assertEqual(
            (
                "/toolchains/1.99.0/bin/rustc",
                "/toolchains/1.99.0/bin/cargo",
                "1.99.0",
                "rustc 1.99.0 (abc 2026-01-01)",
                "cargo 1.99.0 (def 2026-01-01)",
            ),
            actual,
        )
        self.assertEqual(
            [
                mock.call(
                    ["/trusted/bin/rustup", "which", "--toolchain", "1.99.0", "rustc"],
                    cwd=source,
                ),
                mock.call(
                    ["/trusted/bin/rustup", "which", "--toolchain", "1.99.0", "cargo"],
                    cwd=source,
                ),
                mock.call(["/toolchains/1.99.0/bin/rustc", "--version"], cwd=source),
                mock.call(["/toolchains/1.99.0/bin/cargo", "--version"], cwd=source),
            ],
            run.call_args_list,
        )

    def test_provider_toolchain_rejects_environment_overrides(self) -> None:
        for variable in PREPARER._TOOLCHAIN_OVERRIDE_VARIABLES:
            with self.subTest(variable=variable), tempfile.TemporaryDirectory() as temporary:
                with mock.patch.dict(os.environ, {variable: "override"}), mock.patch.object(
                    PREPARER, "_run"
                ) as run:
                    with self.assertRaisesRegex(
                        ProtoRingExecutableError, "override is forbidden"
                    ):
                        PREPARER._provider_toolchain(Path(temporary))
                run.assert_not_called()

    def test_provider_toolchain_requires_rustup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "rust-toolchain.toml").write_text(
                '[toolchain]\nchannel = "1.99.0"\n'
            )
            with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                PREPARER.shutil, "which", return_value=None
            ):
                with self.assertRaisesRegex(
                    ProtoRingExecutableError, "rustup executable is unavailable"
                ):
                    PREPARER._provider_toolchain(source)

    def test_build_environment_pins_compiler_and_clears_wrappers(self) -> None:
        overrides = {
            variable: "hostile" for variable in PREPARER._TOOLCHAIN_OVERRIDE_VARIABLES
        }
        overrides["CARGO_TARGET_X86_64_APPLE_DARWIN_RUSTFLAGS"] = "--sysroot=/bad"
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, overrides
        ):
            cargo_home = Path(temporary) / "cargo-home"
            environment = PREPARER._build_environment(
                "/exact/bin/rustc", cargo_home
            )
        self.assertEqual("/exact/bin/rustc", environment["RUSTC"])
        self.assertEqual("/exact/bin/rustc", environment["CARGO_BUILD_RUSTC"])
        self.assertEqual(str(cargo_home), environment["CARGO_HOME"])
        self.assertNotIn("CARGO_TARGET_X86_64_APPLE_DARWIN_RUSTFLAGS", environment)
        for variable in (
            "RUSTC_WRAPPER",
            "RUSTC_WORKSPACE_WRAPPER",
            "CARGO_BUILD_RUSTC_WRAPPER",
            "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER",
        ):
            self.assertEqual("", environment[variable])

    def test_git_environment_removes_all_git_selectors(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"GIT_DIR": "/redirected", "GIT_WORK_TREE": "/other"},
        ):
            environment = boundary._git_environment()
        git_keys = {key for key in environment if key.startswith("GIT_")}
        self.assertEqual({"GIT_NO_REPLACE_OBJECTS"}, git_keys)
        self.assertEqual("1", environment["GIT_NO_REPLACE_OBJECTS"])

    def test_dynamic_cargo_configuration_is_rejected(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"CARGO_TARGET_X86_64_APPLE_DARWIN_LINKER": "/hostile/linker"},
        ):
            self.assertIn(
                "CARGO_TARGET_X86_64_APPLE_DARWIN_LINKER",
                PREPARER._external_build_overrides(),
            )

    def test_cargo_driver_rejects_ancestor_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            driver = root / "driver"
            driver.mkdir()
            (root / ".cargo").mkdir()
            (root / ".cargo/config.toml").write_text("[build]\n")
            with self.assertRaisesRegex(
                ProtoRingExecutableError, "must not contain configuration"
            ):
                PREPARER._require_neutral_cargo_driver(driver)

    def test_exact_worktree_rejects_unexpected_empty_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "unexpected").mkdir()
            with mock.patch.object(
                source_realization, "_run_git", side_effect=["sha1", ""]
            ):
                with self.assertRaises(source_realization.SourceRealizationError):
                    source_realization._raw_tree_is_exact(source)

    def test_exact_worktree_rejects_git_metadata_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            metadata = source / ".git"
            metadata.mkdir(parents=True)
            target = Path(temporary) / "objects"
            target.mkdir()
            (metadata / "objects").symlink_to(target, target_is_directory=True)
            with mock.patch.object(
                source_realization, "_run_git", side_effect=["sha1", ""]
            ):
                with self.assertRaises(source_realization.SourceRealizationError):
                    source_realization._raw_tree_is_exact(source)

    def test_build_snapshot_copies_only_tree_bound_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "Cargo.toml").write_bytes(b"[workspace]\n")
            entries = {
                "Cargo.toml": (
                    "100644",
                    source_realization._blob_oid(b"[workspace]\n"),
                )
            }
            with mock.patch.object(source_realization, "source_is_exact"), mock.patch.object(
                source_realization, "_tree_entries", return_value=entries
            ):
                source_realization.copy_exact_source_snapshot(
                    source, root / "snapshot", mock.Mock(commit="a" * 40)
                )
            self.assertEqual(b"[workspace]\n", (root / "snapshot/Cargo.toml").read_bytes())

    def test_build_snapshot_rejects_bytes_outside_bound_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "Cargo.toml").write_bytes(b"substituted")
            entries = {"Cargo.toml": ("100644", "0" * 40)}
            with mock.patch.object(source_realization, "source_is_exact"), mock.patch.object(
                source_realization, "_tree_entries", return_value=entries
            ):
                with self.assertRaises(source_realization.SourceRealizationError):
                    source_realization.copy_exact_source_snapshot(
                        source, root / "snapshot", mock.Mock(commit="a" * 40)
                    )

    def test_provider_process_environment_removes_injection_selectors(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"DYLD_INSERT_LIBRARIES": "/bad", "LD_PRELOAD": "/bad", "PATH": "/bin"},
        ):
            environment = execution_custody.provider_process_environment()
        self.assertEqual("/bin", environment["PATH"])
        self.assertNotIn("DYLD_INSERT_LIBRARIES", environment)
        self.assertNotIn("LD_PRELOAD", environment)

    def test_executable_snapshot_requires_the_manifest_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "provider"
            binary.write_bytes(b"provider")
            with self.assertRaises(execution_custody.ProviderExecutionCustodyError):
                with execution_custody.executable_snapshot(binary, "0" * 64):
                    self.fail("a mismatched executable must not be yielded")

    def test_executable_snapshot_is_private_and_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "provider"
            binary.write_bytes(b"provider")
            digest = hashlib.sha256(b"provider").hexdigest()
            with execution_custody.executable_snapshot(binary, digest) as snapshot:
                binary.write_bytes(b"replacement")
                self.assertEqual(b"provider", snapshot.read_bytes())
                self.assertEqual(0o500, snapshot.stat().st_mode & 0o777)

    def test_provider_realization_must_remain_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repository"
            root.mkdir()
            with self.assertRaisesRegex(ProtoRingExecutableError, "outside Ruu"):
                boundary._require_external_provider_root(root, root / ".cache/provider")
            (root / ".cache").mkdir()
            redirected = Path(temporary) / "redirected-cache"
            redirected.symlink_to(root / ".cache", target_is_directory=True)
            with self.assertRaisesRegex(ProtoRingExecutableError, "outside Ruu"):
                boundary._require_external_provider_root(root, redirected / "provider")
            external = Path(temporary) / "external-provider"
            boundary._require_external_provider_root(root, external)
