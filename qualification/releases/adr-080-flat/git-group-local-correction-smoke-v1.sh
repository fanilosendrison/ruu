#!/usr/bin/env bash
set -euo pipefail

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

git init -q -b main
git config user.name Audit
git config user.email audit@example.invalid

echo base > base.txt
git add base.txt
git commit -q -m base
M="$(git rev-parse HEAD)"

# G1 exact state A.
git switch -q -c g1 "$M"
echo g1 > g1.txt
git add g1.txt
git commit -q -m g1
A="$(git rev-parse HEAD)"

# Later ordinary work G2 owns the effect A -> B.
git switch -q -c g2 "$A"
echo g2 > g2.txt
git add g2.txt
git commit -q -m g2
B="$(git rev-parse HEAD)"

# Correction for G1 is authored from G1's exact state A, not from live B.
git switch -q -c g1-correction "$A"
echo corrected > correction.txt
git add correction.txt
git commit -q -m g1-correction
Aprime="$(git rev-parse HEAD)"

# Exact ADR-050-style transplant of the child owned effect A->B onto A'.
T="$(git merge-tree --write-tree --merge-base="$A" "$Aprime" "$B" | head -n1)"
idx="$tmp/index"
GIT_INDEX_FILE="$idx" git read-tree "$T"
files="$(GIT_INDEX_FILE="$idx" git ls-files)"
grep -qx 'base.txt' <<<"$files"
grep -qx 'g1.txt' <<<"$files"
grep -qx 'correction.txt' <<<"$files"
grep -qx 'g2.txt' <<<"$files"

# The original child owned anchor B remains unchanged/auditable.
test "$(git show "$B:g2.txt")" = "g2"
test "$(git show "$A:g1.txt")" = "g1"
# G1 correction branch does not silently contain G2-owned work.
if git cat-file -e "$Aprime:g2.txt" 2>/dev/null; then
  echo 'group-local correction incorrectly absorbed later G2 work' >&2
  exit 1
fi

echo 'group-local correction + descendant restack smoke: PASS'
