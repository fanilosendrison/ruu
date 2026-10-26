"""Mock exact-source Git observations for native-provider tests."""

from pathlib import Path
from unittest import mock

import proto_ring_source_realization as source_realization


def source_fixture(temporary: str) -> Path:
    source = Path(temporary)
    (source / ".git").mkdir()
    return source


def symlinked_git_source(temporary: str) -> Path:
    root = Path(temporary)
    source = root / "source"
    source.mkdir()
    metadata = root / "redirected-git"
    metadata.mkdir()
    (source / ".git").symlink_to(metadata, target_is_directory=True)
    return source


def source_git(
    expected: str,
    *,
    head: str | None = None,
    detached: bool = True,
    origin: str | None = None,
    dirty: str | None = None,
    status: str = "",
    replacement: str = "",
    index_entries: str = "H Cargo.toml",
    tree_listing: str = "",
):
    observed_head = expected if head is None else head
    observed_origin = origin or "https://github.com/fanilosendrison/proto-ring.git"

    def output(source, *arguments):
        if arguments == ("rev-parse", "HEAD"):
            return observed_head
        if arguments == ("rev-parse", "--show-toplevel"):
            return str(Path(source).resolve())
        if arguments == ("rev-parse", "--absolute-git-dir"):
            return str((Path(source) / ".git").resolve())
        if arguments == ("remote", "get-url", "origin"):
            return observed_origin
        if arguments == ("rev-parse", "--show-object-format"):
            return "sha1"
        if arguments[0] == "ls-tree":
            return tree_listing
        if arguments[0] == "status":
            return status
        if arguments[0] == "for-each-ref":
            return replacement
        if arguments == ("ls-files", "-v"):
            return index_entries
        raise AssertionError(arguments)

    def code(_source, *arguments):
        if arguments[:2] == ("symbolic-ref", "-q"):
            return 1 if detached else 0
        if arguments[:2] == ("diff", "--quiet"):
            return 1 if dirty == "tracked" else 0
        if arguments[:3] == ("diff", "--cached", "--quiet"):
            return 1 if dirty == "cached" else 0
        return 0

    return mock.patch.object(
        source_realization, "_run_git", side_effect=output
    ), mock.patch.object(source_realization, "_git_status", side_effect=code)
