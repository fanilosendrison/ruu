#!/usr/bin/env bash
set -euo pipefail

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"

git init -q repo
cd repo
git config user.email smoke@example.invalid
git config user.name smoke
printf 'ignored.tmp\n' > .gitignore
printf 'base\n' > tracked.txt
git add .gitignore tracked.txt
git commit -q -m base
P="$(git rev-parse HEAD)"
PTREE="$(git rev-parse HEAD^{tree})"

# Real index contains an intermediate staged version; worktree contains the final version.
printf 'staged-v1\n' > tracked.txt
git add tracked.txt
printf 'worktree-v2\n' > tracked.txt
printf 'new-file\n' > new.txt
printf 'ignore-me\n' > ignored.tmp

REAL_INDEX_BLOB="$(git show :tracked.txt)"
[ "$REAL_INDEX_BLOB" = "staged-v1" ]

TMP_INDEX="$PWD/.git/Ruu-smoke-index"
rm -f "$TMP_INDEX"
GIT_INDEX_FILE="$TMP_INDEX" git read-tree "$P"
GIT_INDEX_FILE="$TMP_INDEX" git add -A -- .
T="$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)"

[ "$(git show "$T:tracked.txt")" = "worktree-v2" ]
[ "$(git show "$T:new.txt")" = "new-file" ]
if git cat-file -e "$T:ignored.tmp" 2>/dev/null; then
  echo "ignored untracked path unexpectedly entered candidate tree" >&2
  exit 1
fi
[ "$T" != "$PTREE" ]
# Canonical construction must not have consumed/rewritten caller staging.
[ "$(git show :tracked.txt)" = "staged-v1" ]

# Rebuild from the same P + same worktree and require exact tree identity.
rm -f "$TMP_INDEX"
GIT_INDEX_FILE="$TMP_INDEX" git read-tree "$P"
GIT_INDEX_FILE="$TMP_INDEX" git add -A -- .
T2="$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)"
[ "$T2" = "$T" ]

# A worktree exactly equal to P is a no-op candidate tree.
git reset -q --hard "$P"
rm -f new.txt ignored.tmp "$TMP_INDEX"
GIT_INDEX_FILE="$TMP_INDEX" git read-tree "$P"
GIT_INDEX_FILE="$TMP_INDEX" git add -A -- .
T_NOOP="$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)"
[ "$T_NOOP" = "$PTREE" ]

# Native structural conflict state is mechanically observable and must not be treated as an ordinary checkpoint.
git checkout -q -b side
printf 'side\n' > tracked.txt
git commit -qam side
git checkout -q master
printf 'main\n' > tracked.txt
git commit -qam main
set +e
git merge side >/dev/null 2>&1
MERGE_RC=$?
set -e
[ "$MERGE_RC" -ne 0 ]
[ -n "$(git ls-files -u)" ]
[ -f .git/MERGE_HEAD ]
git merge --abort

printf 'Ruu canonical checkpoint smoke v1: PASS\n'
