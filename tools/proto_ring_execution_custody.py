"""Preserve native provider executable custody during one invocation."""

from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path
import shutil
import stat
import tempfile
from typing import Iterator


class ProviderExecutionCustodyError(RuntimeError):
    """The realized executable could not be snapshotted safely."""


def provider_process_environment() -> dict[str, str]:
    forbidden_prefixes = ("CARGO_", "DYLD_", "GIT_", "LD_", "RUST")
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(forbidden_prefixes)
    }


@contextlib.contextmanager
def captured_executable(binary: Path) -> Iterator[tuple[Path, str]]:
    """Yield one private executable copy and the digest of exactly those bytes."""

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        source = os.open(binary, flags)
    except OSError as error:
        raise ProviderExecutionCustodyError("provider binary cannot be opened") from error
    try:
        metadata = os.fstat(source)
        if not stat.S_ISREG(metadata.st_mode):
            raise ProviderExecutionCustodyError("provider binary is not a regular file")
        with tempfile.TemporaryDirectory(prefix="ruu-proto-ring-execution-") as temporary:
            snapshot = Path(temporary) / "proto-ring-compat"
            digest = hashlib.sha256()
            with snapshot.open("xb") as target:
                while chunk := os.read(source, 1024 * 1024):
                    digest.update(chunk)
                    target.write(chunk)
                target.flush()
                os.fsync(target.fileno())
            snapshot.chmod(0o500)
            yield snapshot, digest.hexdigest()
    finally:
        os.close(source)


def verify_executable_snapshot(path: Path, expected_sha256: str) -> None:
    """Verify exact bytes and mode through one no-follow file descriptor."""

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise ProviderExecutionCustodyError(
                    "private provider snapshot is not a regular file"
                )
            if stat.S_IMODE(metadata.st_mode) != 0o500:
                raise ProviderExecutionCustodyError(
                    "private provider snapshot mode is not 0500"
                )
            digest = hashlib.sha256()
            while chunk := os.read(descriptor, 1024 * 1024):
                digest.update(chunk)
            if digest.hexdigest() != expected_sha256:
                raise ProviderExecutionCustodyError(
                    "private provider snapshot digest changed"
                )
        finally:
            os.close(descriptor)
    except ProviderExecutionCustodyError:
        raise
    except OSError as error:
        raise ProviderExecutionCustodyError(
            "private provider snapshot cannot be verified"
        ) from error


@contextlib.contextmanager
def execution_snapshot_from_private_master(
    master: Path, expected_sha256: str
) -> Iterator[Path]:
    """Capture one execution file from one opened private-master descriptor."""

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        source = os.open(master, flags)
    except OSError as error:
        raise ProviderExecutionCustodyError(
            "private provider master cannot be opened"
        ) from error
    try:
        metadata = os.fstat(source)
        if not stat.S_ISREG(metadata.st_mode):
            raise ProviderExecutionCustodyError(
                "private provider master is not a regular file"
            )
        if stat.S_IMODE(metadata.st_mode) != 0o500:
            raise ProviderExecutionCustodyError(
                "private provider master mode is not 0500"
            )
        with tempfile.TemporaryDirectory(
            prefix="ruu-proto-ring-call-execution-"
        ) as temporary:
            execution = Path(temporary) / "proto-ring-compat"
            digest = hashlib.sha256()
            target_descriptor = os.open(
                execution, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
            try:
                with os.fdopen(target_descriptor, "wb") as target:
                    while chunk := os.read(source, 1024 * 1024):
                        digest.update(chunk)
                        target.write(chunk)
                    target.flush()
                    os.fsync(target.fileno())
            except BaseException:
                execution.unlink(missing_ok=True)
                raise
            if digest.hexdigest() != expected_sha256:
                raise ProviderExecutionCustodyError(
                    "private provider master digest changed"
                )
            execution.chmod(0o500)
            verify_executable_snapshot(execution, expected_sha256)
            yield execution
    except ProviderExecutionCustodyError:
        raise
    except OSError as error:
        raise ProviderExecutionCustodyError(
            "private provider master cannot be captured"
        ) from error
    finally:
        os.close(source)


class _OwnedExecutableSnapshot(contextlib.AbstractContextManager[Path]):
    """Own one private snapshot without child-process cleanup authority."""

    def __init__(self, binary: Path, expected_sha256: str) -> None:
        self._binary = binary
        self._expected_sha256 = expected_sha256
        self._owner_pid = os.getpid()
        self._directory: Path | None = None

    def __enter__(self) -> Path:
        directory = Path(tempfile.mkdtemp(prefix="ruu-proto-ring-execution-"))
        self._directory = directory
        snapshot = directory / "proto-ring-compat"
        try:
            with captured_executable(self._binary) as (captured, digest):
                if digest != self._expected_sha256:
                    raise ProviderExecutionCustodyError(
                        "provider binary digest differs from the realization manifest"
                    )
                captured.replace(snapshot)
            verify_executable_snapshot(snapshot, self._expected_sha256)
            return snapshot
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *exc_info: object) -> None:
        if self._directory is not None and os.getpid() == self._owner_pid:
            shutil.rmtree(self._directory, ignore_errors=True)
        self._directory = None


def executable_snapshot(
    binary: Path, expected_sha256: str
) -> contextlib.AbstractContextManager[Path]:
    """Return an owner-safe private executable snapshot lifetime."""

    return _OwnedExecutableSnapshot(binary, expected_sha256)
