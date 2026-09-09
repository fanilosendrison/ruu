#!/usr/bin/env bash
set -euo pipefail

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT
cd "$ROOT"
git init -q
git config user.name 'Ruu-smoke'
git config user.email 'Ruu-smoke@example.invalid'

echo 'shared=base' > shared.txt
git add shared.txt
git commit -qm 'M'

# Old predecessor/base A.
echo 'predecessor=v1' > parent.txt
echo 'child=false' > child.txt
git add parent.txt child.txt
git commit -qm 'A'
A=$(git rev-parse HEAD)

# Child-owned exact candidate B over old base A.
git checkout -q -b child "$A"
echo 'child=true' > child.txt
git add child.txt
git commit -qm 'B child work'
B=$(git rev-parse HEAD)

# New predecessor/base A' advances from A without containing child work.
git checkout -q -b parent-revised "$A"
echo 'predecessor=v2' > parent.txt
git add parent.txt
git commit -qm "A' predecessor revision"
AP=$(git rev-parse HEAD)

# Exact state-transplant: merge-base=A, ours=A', theirs=B.
OUT1=$(git merge-tree --write-tree --merge-base="$A" "$AP" "$B")
T1=${OUT1%%$'\n'*}
OUT2=$(git merge-tree --write-tree --merge-base="$A" "$AP" "$B")
T2=${OUT2%%$'\n'*}
test "$T1" = "$T2"
test "$(git show "$T1:parent.txt")" = 'predecessor=v2'
test "$(git show "$T1:child.txt")" = 'child=true'
test "$(git show "$T1:shared.txt")" = 'shared=base'

# Create a deterministic provider-facing head over the new base.
export GIT_AUTHOR_NAME='Ruu'
export GIT_AUTHOR_EMAIL='Ruu@example.invalid'
export GIT_COMMITTER_NAME='Ruu'
export GIT_COMMITTER_EMAIL='Ruu@example.invalid'
export GIT_AUTHOR_DATE='2000-01-01T00:00:00+0000'
export GIT_COMMITTER_DATE='2000-01-01T00:00:00+0000'
H1=$(printf '%s\n' 'Ruu restack v1' | git commit-tree "$T1" -p "$AP")
H2=$(printf '%s\n' 'Ruu restack v1' | git commit-tree "$T1" -p "$AP")
test "$H1" = "$H2"
test "$(git rev-parse "$H1^{tree}")" = "$T1"
test "$(git rev-parse "$H1^")" = "$AP"

# Conflict case: both predecessor and child change the same base line differently.
git checkout -q -b conflict-child "$A"
echo 'shared=child' > shared.txt
git add shared.txt
git commit -qm 'child conflicting change'
BC=$(git rev-parse HEAD)

git checkout -q -b conflict-parent "$A"
echo 'shared=parent' > shared.txt
git add shared.txt
git commit -qm 'parent conflicting change'
APC=$(git rev-parse HEAD)

set +e
git merge-tree --write-tree --merge-base="$A" "$APC" "$BC" > conflict.out 2>&1
rc=$?
set -e
test "$rc" -ne 0

echo 'Ruu ADR-050 restack smoke: PASS'
echo 'exact_three_way_transplant=PASS'
echo 'predecessor_evolution_preserved=PASS'
echo 'child_owned_effect_preserved=PASS'
echo 'deterministic_tree=PASS'
echo 'deterministic_submission_head=PASS'
echo 'new_head_parent_is_new_base=PASS'
echo 'semantic_conflict_blocks=PASS'
