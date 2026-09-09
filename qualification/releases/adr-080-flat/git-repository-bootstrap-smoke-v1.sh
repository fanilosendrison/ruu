#!/usr/bin/env bash
set -euo pipefail

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

# Start with a genuinely new repository: no target ref/OID exists yet.
git init -q repo
cd repo
git config user.name 'Ruu bootstrap smoke'
git config user.email 'Ruu@example.invalid'

if git rev-parse --verify refs/heads/main >/dev/null 2>&1; then
  echo 'new repository unexpectedly already has main' >&2
  exit 1
fi

# External Repository Provisioner bootstrap: establish a real B0 first.
empty_tree="$(git hash-object -t tree /dev/null)"
B0="$(printf 'Repository bootstrap\n' | git commit-tree "$empty_tree")"
git update-ref refs/heads/main "$B0"

[[ -n "$B0" ]]
[[ "$(git rev-parse refs/heads/main)" == "$B0" ]]
git cat-file -e "$B0^{commit}"

# Only after B0 exists does ordinary managed topology begin.
CONV=refs/heads/Ruu/convergence/X
CU=refs/heads/Ruu/contributions/C1
git update-ref "$CONV" "$B0"
git update-ref "$CU" "$B0"

[[ "$(git rev-parse "$CONV")" == "$B0" ]]
[[ "$(git rev-parse "$CU")" == "$B0" ]]
git merge-base --is-ancestor "$B0" "$(git rev-parse "$CONV")"
git merge-base --is-ancestor "$B0" "$(git rev-parse "$CU")"

# First managed authoring can now produce an ordinary descendant exact state.
git switch -q --detach "$B0"
echo 'first managed content' > README.md
git add README.md
git commit -q -m 'first managed change'
C1="$(git rev-parse HEAD)"
git merge-base --is-ancestor "$B0" "$C1"

# A name/path collision is not identity: smoke the fail-closed expectation at the
# mechanism level by proving a second unrelated root cannot be mistaken for B0.
B0_OTHER="$(printf 'unrelated bootstrap\n' | git commit-tree "$empty_tree")"
[[ "$B0_OTHER" != "$B0" ]]

# Provider creation is deliberately not part of this Git smoke; ADR-056 makes it
# an optional/later external binding, not a prerequisite to local B0 authoring.

echo 'Ruu repository bootstrap smoke v1: PASS'
echo "B0=$B0"
echo "C1=$C1"
