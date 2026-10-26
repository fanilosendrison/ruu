#!/usr/bin/env python3
"""Explicitly realize the bound native proto-ring compatibility provider outside Ruu."""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
from typing import Iterator

from proto_ring_executable_binding import (
    PROTO_RING_TRANSPORT_VERSION,
    ExecutableProviderBinding,
    ProtoRingExecutableError,
    _binary_path,
    _canonical_json,
    _git_environment,
    _invoke_binary,
    _require_external_provider_path,
    _require_external_provider_root,
    _source_is_exact,
    _validate_identity,
    cache_base,
    load_executable_provider_binding,
    managed_provider_root,
)
from proto_ring_execution_custody import (
    ProviderExecutionCustodyError,
    captured_executable,
)
from proto_ring_source_realization import (
    copy_exact_source_snapshot,
    tree_bytes_are_exact,
)

ROOT = Path(__file__).resolve().parents[1]
_TOOLCHAIN_OVERRIDE_VARIABLES = {
    "RUSTUP_HOME",
    "RUSTUP_TOOLCHAIN",
    "RUSTC",
    "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER",
    "CARGO_BUILD_RUSTC",
    "CARGO_BUILD_RUSTC_WRAPPER",
    "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER",
    "CARGO_BUILD_RUSTFLAGS",
    "CARGO_BUILD_RUSTDOCFLAGS",
    "CARGO_BUILD_TARGET",
    "CARGO_ENCODED_RUSTFLAGS",
    "CARGO_ENCODED_RUSTDOCFLAGS",
    "CARGO_HOME",
    "CARGO_TARGET_DIR",
    "RUSTFLAGS",
    "RUSTDOCFLAGS",
}


def _run(
    arguments: list[str],
    *,
    cwd: Path | None = None,
    environment: dict[str, str] | None = None,
) -> str:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "command failed"
        raise ProtoRingExecutableError(message)
    return completed.stdout.strip()


@contextlib.contextmanager
def _exclusive_lock(binding: ExecutableProviderBinding) -> Iterator[None]:
    lock = cache_base() / "ruu" / "proto-ring" / ".prepare.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _reset_source(source: Path, binding: ExecutableProviderBinding) -> None:
    """Construct a managed, detached checkout exactly at the immutable binding."""

    if source.exists():
        shutil.rmtree(source)
    source.parent.mkdir(parents=True, exist_ok=True)
    git_environment = _git_environment()
    _run(["git", "init", "--quiet", str(source)], environment=git_environment)
    _run(
        [
            "git",
            "-C",
            str(source),
            "remote",
            "add",
            "origin",
            f"https://github.com/{binding.repository}.git",
        ],
        environment=git_environment,
    )
    _run(
        ["git", "-C", str(source), "fetch", "--depth=1", "origin", binding.commit],
        environment=git_environment,
    )
    _run(
        ["git", "-C", str(source), "checkout", "--detach", "FETCH_HEAD"],
        environment=git_environment,
    )
    _source_is_exact(source, binding)


def _cached_source_is_valid(source: Path, binding: ExecutableProviderBinding) -> bool:
    try:
        _source_is_exact(source, binding)
    except ProtoRingExecutableError:
        return False
    return True


def _external_build_overrides() -> list[str]:
    return sorted(
        key
        for key in os.environ
        if key in _TOOLCHAIN_OVERRIDE_VARIABLES
        or key.startswith("CARGO_")
        or key.startswith("RUSTC")
        or key.startswith("RUSTUP_")
        or key in {"RUSTFLAGS", "RUSTDOCFLAGS"}
    )


def _provider_toolchain(source: Path) -> tuple[str, str, str, str, str]:
    overrides = _external_build_overrides()
    if overrides:
        raise ProtoRingExecutableError(
            f"provider toolchain override is forbidden: {', '.join(overrides)}"
        )
    try:
        declaration = tomllib.loads((source / "rust-toolchain.toml").read_text())
        channel = declaration["toolchain"]["channel"]
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError) as error:
        raise ProtoRingExecutableError(
            "provider Rust toolchain declaration is invalid"
        ) from error
    if not isinstance(channel, str) or not channel:
        raise ProtoRingExecutableError("provider Rust toolchain channel is invalid")
    rustup = shutil.which("rustup")
    if rustup is None or not Path(rustup).is_absolute():
        raise ProtoRingExecutableError("rustup executable is unavailable")
    rustc = _run(
        [rustup, "which", "--toolchain", channel, "rustc"], cwd=source
    )
    cargo = _run(
        [rustup, "which", "--toolchain", channel, "cargo"], cwd=source
    )
    rustc_version = _run([rustc, "--version"], cwd=source)
    cargo_version = _run([cargo, "--version"], cwd=source)
    if not rustc_version.startswith(f"rustc {channel} "):
        raise ProtoRingExecutableError("rustc does not match the provider toolchain")
    return rustc, cargo, channel, rustc_version, cargo_version


def _build_environment(rustc: str, cargo_home: Path) -> dict[str, str]:
    admitted = {
        "ALL_PROXY",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "NO_PROXY",
        "PATH",
        "SSL_CERT_DIR",
        "SSL_CERT_FILE",
        "SYSTEMROOT",
        "WINDIR",
        "all_proxy",
        "https_proxy",
        "http_proxy",
        "no_proxy",
    }
    environment = {
        key: value for key, value in os.environ.items() if key in admitted
    }
    environment.update(
        {
            "RUSTC": rustc,
            "RUSTC_WRAPPER": "",
            "RUSTC_WORKSPACE_WRAPPER": "",
            "CARGO_BUILD_RUSTC": rustc,
            "CARGO_BUILD_RUSTC_WRAPPER": "",
            "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER": "",
            "CARGO_HOME": str(cargo_home),
        }
    )
    return environment


def _require_neutral_cargo_driver(driver: Path) -> None:
    for directory in (driver, *driver.parents):
        for name in ("config", "config.toml"):
            if (directory / ".cargo" / name).exists():
                raise ProtoRingExecutableError(
                    "Cargo build-driver ancestors must not contain configuration"
                )


def _initialize_snapshot_git(
    source: Path, snapshot: Path, binding: ExecutableProviderBinding
) -> None:
    environment = _git_environment()
    _run(["git", "init", "--quiet", str(snapshot)], environment=environment)
    _run(
        [
            "git",
            "-C",
            str(snapshot),
            "fetch",
            "--quiet",
            "--depth=1",
            "--no-tags",
            str(source),
            binding.commit,
        ],
        environment=environment,
    )
    _run(
        [
            "git",
            "-C",
            str(snapshot),
            "update-ref",
            "--no-deref",
            "HEAD",
            binding.commit,
        ],
        environment=environment,
    )
    _run(
        ["git", "-C", str(snapshot), "reset", "--quiet", "--mixed", "HEAD"],
        environment=environment,
    )
    if _run(
        ["git", "-C", str(snapshot), "rev-parse", "HEAD"], environment=environment
    ) != binding.commit:
        raise ProtoRingExecutableError("private build snapshot identity is invalid")


def _seal_snapshot(snapshot: Path) -> None:
    for path in sorted(snapshot.rglob("*"), reverse=True):
        if path.is_symlink():
            continue
        mode = path.stat().st_mode
        path.chmod(0o500 if path.is_dir() or mode & 0o111 else 0o400)
    snapshot.chmod(0o500)


def _build(
    provider_root: Path, source: Path, binding: ExecutableProviderBinding
) -> dict[str, object]:
    build = provider_root / "build"
    cargo_home = provider_root / "cargo-home"
    for generated in (build, cargo_home):
        if generated.exists():
            shutil.rmtree(generated)
    cargo_home.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="ruu-proto-ring-build-") as temporary:
        driver = Path(temporary).resolve()
        _require_neutral_cargo_driver(driver)
        snapshot = driver / "source"
        copy_exact_source_snapshot(source, snapshot, binding)
        _initialize_snapshot_git(source, snapshot, binding)
        tree_bytes_are_exact(snapshot, binding.commit)
        _source_is_exact(source, binding)
        rustc, cargo, _channel, rustc_version, cargo_version = _provider_toolchain(
            snapshot
        )
        _seal_snapshot(snapshot)
        private_target = driver / "target"
        _run(
            [
                cargo,
                "build",
                "--release",
                "--locked",
                "--target-dir",
                str(private_target),
                "--manifest-path",
                str(snapshot / "Cargo.toml"),
                "-p",
                "proto-ring-compat",
            ],
            cwd=driver,
            environment=_build_environment(rustc, cargo_home),
        )
        private_binary = private_target / "release" / _binary_path(provider_root).name
        if not private_binary.is_file():
            raise ProtoRingExecutableError(
                "proto-ring build did not produce proto-ring-compat"
            )
        try:
            with captured_executable(private_binary) as (verified_binary, digest):
                response = _invoke_binary(
                    verified_binary, "engine.identity", {}, binding=None
                )
                _validate_identity(response, binding)
                binary = _binary_path(provider_root)
                binary.parent.mkdir(parents=True)
                staging = binary.with_name(f"{binary.name}.tmp")
                shutil.copyfile(verified_binary, staging)
                staging.chmod(0o500)
                os.replace(staging, binary)
        except ProviderExecutionCustodyError as error:
            raise ProtoRingExecutableError(str(error)) from error
    _source_is_exact(source, binding)
    return {
        "repository": binding.repository,
        "commit": binding.commit,
        "transport_version": PROTO_RING_TRANSPORT_VERSION,
        "binary_sha256": digest,
        "rustc_version": rustc_version,
        "cargo_version": cargo_version,
    }


def prepare(root: Path = ROOT) -> dict[str, object]:
    binding = load_executable_provider_binding(root)
    provider_root = managed_provider_root(binding)
    _require_external_provider_root(root, provider_root)
    source = provider_root / "source"
    guarded_paths = (
        source,
        provider_root / "build",
        provider_root / "cargo-home",
        provider_root / "realization.json",
        provider_root / "realization.json.tmp",
    )
    for candidate in guarded_paths:
        _require_external_provider_path(root, provider_root, candidate)
    with _exclusive_lock(binding):
        if not _cached_source_is_valid(source, binding):
            _reset_source(source, binding)
        manifest = _build(provider_root, source, binding)
        provider_root.mkdir(parents=True, exist_ok=True)
        temporary = provider_root / "realization.json.tmp"
        temporary.write_bytes(_canonical_json(manifest))
        os.replace(temporary, provider_root / "realization.json")
    return manifest


def main(arguments: list[str] | None = None) -> int:
    argv = sys.argv[1:] if arguments is None else arguments
    if argv:
        print("usage: prepare-proto-ring-provider.py", file=sys.stderr)
        return 1
    try:
        manifest = prepare()
    except ProtoRingExecutableError as error:
        print(f"ERROR: native proto-ring preparation: {error}", file=sys.stderr)
        return 1
    print(
        "native proto-ring provider: READY "
        f"({manifest['repository']}@{manifest['commit']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
