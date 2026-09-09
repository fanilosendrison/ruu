#!/usr/bin/env bash
set -euo pipefail

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

git init -q repo
cd repo
git config user.name 'Ruu smoke'
git config user.email 'Ruu@example.invalid'

echo B > f
git add f
git commit -q -m B
B="$(git rev-parse HEAD)"

git switch -q -c candidate
echo C >> f
git commit -qam C
C="$(git rev-parse HEAD)"
echo D >> f
git commit -qam D
D="$(git rev-parse HEAD)"

git switch -q --detach "$B"
echo E > sibling
git add sibling
git commit -q -m E
E="$(git rev-parse HEAD)"

# unrelated root candidate (same tree is enough; ancestry must fail)
tree="$(git rev-parse "$B^{tree}")"
F="$(printf 'unrelated\n' | git commit-tree "$tree")"

# target and recovery anchor
TARGET=refs/heads/main
ANCHOR=refs/Ruu/operations/op1/attempt1/candidate
git update-ref "$TARGET" "$B"
git update-ref "$ANCHOR" "$C"
[[ "$(git rev-parse "$ANCHOR")" == "$C" ]]

advance_target_ff() {
  local expected="$1" new="$2"
  local current
  current="$(git rev-parse "$TARGET")"
  [[ "$current" == "$expected" ]] || return 10
  git merge-base --is-ancestor "$expected" "$new" || return 11
  git update-ref "$TARGET" "$new" "$expected"
}

realized() {
  local candidate="$1" current
  current="$(git rev-parse "$TARGET")"
  [[ "$current" == "$candidate" ]] && return 0
  git merge-base --is-ancestor "$candidate" "$current"
}

# Exact-old descendant succeeds.
advance_target_ff "$B" "$C"
[[ "$(git rev-parse "$TARGET")" == "$C" ]]
realized "$C"

# Later advancement still proves C was realized.
git update-ref "$TARGET" "$D" "$C"
realized "$C"

# Stale expected-old must not mutate even though C is an ancestor of current D.
before="$(git rev-parse "$TARGET")"
if advance_target_ff "$B" "$C"; then
  echo 'stale expected-old unexpectedly succeeded' >&2
  exit 1
fi
[[ "$(git rev-parse "$TARGET")" == "$before" ]]

# Divergent sibling does not prove realization.
git update-ref "$TARGET" "$E" "$D"
if realized "$C"; then
  echo 'divergent target unexpectedly adopted C' >&2
  exit 1
fi

# Non-descendant candidate is rejected before ref mutation.
git update-ref "$TARGET" "$B" "$E"
before="$(git rev-parse "$TARGET")"
if advance_target_ff "$B" "$F"; then
  echo 'non-FF candidate unexpectedly succeeded' >&2
  exit 1
fi
[[ "$(git rev-parse "$TARGET")" == "$before" ]]

# git update-ref exact expected-old guard itself rejects stale CAS.
git update-ref "$TARGET" "$D" "$B"
if git update-ref "$TARGET" "$C" "$B" 2>/dev/null; then
  echo 'git update-ref stale CAS unexpectedly succeeded' >&2
  exit 1
fi
[[ "$(git rev-parse "$TARGET")" == "$D" ]]

# Anchor may be deleted only after recovery/adoption sufficiency in this smoke scenario.
realized "$C"
git update-ref -d "$ANCHOR" "$C"
if git show-ref --verify --quiet "$ANCHOR"; then
  echo 'recovery anchor cleanup failed' >&2
  exit 1
fi

echo 'Ruu DIRECT_TARGET_ADVANCE smoke v1: PASS'
echo "B=$B"
echo "C=$C"
echo "D=$D"
