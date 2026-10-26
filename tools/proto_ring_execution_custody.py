"""Preserve native provider executable custody during one invocation."""

from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path
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


@contextlib.contextmanager
def executable_snapshot(binary: Path, expected_sha256: str) -> Iterator[Path]:
    """Yield a private executable copy whose bytes match the realization digest."""

    with captured_executable(binary) as (snapshot, digest):
        if digest != expected_sha256:
            raise ProviderExecutionCustodyError(
                "provider binary digest differs from the realization manifest"
            )
        yield snapshot
