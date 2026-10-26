"""Verify the exact Git source realization of the native Proto-Ring provider."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import subprocess
from typing import Protocol


class SourceBinding(Protocol):
    repository: str
    commit: str


class SourceRealizationError(ValueError):
    """The managed provider source is not the exact bound Git realization."""


def git_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _run_git(source: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(source), *arguments],
        check=False,
        capture_output=True,
        text=True,
        env=git_environment(),
    )
    if completed.returncode != 0:
        raise SourceRealizationError("provider source verification failed")
    return completed.stdout.strip()


def _git_status(source: Path, *arguments: str) -> int:
    return subprocess.run(
        ["git", "-C", str(source), *arguments],
        check=False,
        capture_output=True,
        env=git_environment(),
    ).returncode


def _blob_oid(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _tree_entries(
    source: Path, revision: str = "HEAD"
) -> dict[str, tuple[str, str]]:
    if _run_git(source, "rev-parse", "--show-object-format") != "sha1":
        raise SourceRealizationError("provider source object format is unsupported")
    entries: dict[str, tuple[str, str]] = {}
    listing = _run_git(
        source,
        "ls-tree",
        "-r",
        "--format=%(objectmode) %(objecttype) %(objectname) %(path)",
        revision,
    )
    for line in listing.splitlines():
        mode, kind, oid, path = line.split(" ", 3)
        if kind != "blob" or path in entries:
            raise SourceRealizationError("provider source tree is unsupported")
        entries[path] = (mode, oid)
    return entries


def _raw_tree_is_exact(source: Path, revision: str = "HEAD") -> None:
    entries = _tree_entries(source, revision)

    expected_directories = {
        parent.as_posix()
        for name in entries
        for parent in Path(name).parents
        if parent != Path(".")
    }
    observed: set[str] = set()
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        name = relative.as_posix()
        metadata = path.lstat()
        if relative.parts[0] == ".git":
            if stat.S_ISLNK(metadata.st_mode):
                raise SourceRealizationError(
                    "provider source Git metadata contains a symlink"
                )
            continue
        if stat.S_ISDIR(metadata.st_mode):
            if name not in expected_directories:
                raise SourceRealizationError(
                    "provider source contains unexpected directories"
                )
            continue
        observed.add(name)
        expected = entries.get(name)
        if expected is None:
            raise SourceRealizationError("provider source contains unexpected paths")
        mode, oid = expected
        if stat.S_ISLNK(metadata.st_mode):
            data = os.readlink(path).encode()
            actual_mode = "120000"
        elif stat.S_ISREG(metadata.st_mode):
            data = path.read_bytes()
            actual_mode = "100755" if metadata.st_mode & 0o111 else "100644"
        else:
            raise SourceRealizationError("provider source contains unsupported paths")
        if actual_mode != mode or _blob_oid(data) != oid:
            raise SourceRealizationError("provider source bytes differ from the bound tree")
    if observed != set(entries):
        raise SourceRealizationError("provider source is missing bound tree paths")


def copy_exact_source_snapshot(
    source: Path, destination: Path, binding: SourceBinding
) -> None:
    """Copy only bytes bound by HEAD into a private build input directory."""

    source_is_exact(source, binding)
    entries = _tree_entries(source, binding.commit)
    destination.mkdir(mode=0o700)
    for name, (mode, oid) in sorted(entries.items()):
        source_path = source / name
        destination_path = destination / name
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        metadata = source_path.lstat()
        if mode == "120000" and stat.S_ISLNK(metadata.st_mode):
            data = os.readlink(source_path).encode()
            if _blob_oid(data) != oid:
                raise SourceRealizationError("provider source changed during snapshot")
            destination_path.symlink_to(os.fsdecode(data))
            continue
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(source_path, flags)
        except OSError as error:
            raise SourceRealizationError(
                "provider source changed during snapshot"
            ) from error
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise SourceRealizationError(
                    "provider source changed during snapshot"
                )
            data = bytearray()
            while chunk := os.read(descriptor, 1024 * 1024):
                data.extend(chunk)
        finally:
            os.close(descriptor)
        actual_mode = "100755" if opened.st_mode & 0o111 else "100644"
        if actual_mode != mode or _blob_oid(bytes(data)) != oid:
            raise SourceRealizationError("provider source changed during snapshot")
        destination_path.write_bytes(data)
        destination_path.chmod(0o700 if mode == "100755" else 0o600)
    source_is_exact(source, binding)


def tree_bytes_are_exact(source: Path, revision: str) -> None:
    _raw_tree_is_exact(source, revision)


def source_is_exact(source: Path, binding: SourceBinding) -> None:
    if not source.is_dir() or _run_git(source, "rev-parse", "HEAD") != binding.commit:
        raise SourceRealizationError("provider source HEAD does not match the binding")
    if _run_git(source, "rev-parse", "--show-toplevel") != str(source.resolve()):
        raise SourceRealizationError("provider source worktree root is redirected")
    git_directory = source / ".git"
    if git_directory.is_symlink() or not git_directory.is_dir():
        raise SourceRealizationError("provider source Git directory is redirected")
    if Path(_run_git(source, "rev-parse", "--absolute-git-dir")).resolve() != git_directory.resolve():
        raise SourceRealizationError("provider source Git directory is redirected")
    if _git_status(source, "symbolic-ref", "-q", "HEAD") == 0:
        raise SourceRealizationError("provider source HEAD must be detached")
    if _run_git(source, "remote", "get-url", "origin") != (
        f"https://github.com/{binding.repository}.git"
    ):
        raise SourceRealizationError("provider source origin does not match the binding")
    if _run_git(source, "for-each-ref", "--format=%(refname)", "refs/replace"):
        raise SourceRealizationError("provider source contains replacement refs")
    index_entries = _run_git(source, "ls-files", "-v").splitlines()
    if any(not entry.startswith("H ") for entry in index_entries):
        raise SourceRealizationError(
            "provider source index contains non-ordinary entries"
        )
    _raw_tree_is_exact(source)
    if _git_status(source, "diff", "--quiet") != 0 or _git_status(
        source, "diff", "--cached", "--quiet"
    ) != 0:
        raise SourceRealizationError("provider source tracked bytes are modified")
    if _run_git(
        source, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"
    ):
        raise SourceRealizationError(
            "provider source contains untracked or ignored inputs"
        )
