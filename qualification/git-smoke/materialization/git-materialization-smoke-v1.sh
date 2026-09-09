#!/usr/bin/env bash
set -euo pipefail

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT
cd "$ROOT"

git init -q
git config user.name 'Test'
git config user.email 'test@example.invalid'

printf 'alpha\nbeta\ngamma\n' > old.txt
git add old.txt
git commit -q -m base
BASE=$(git rev-parse HEAD)

git checkout -q -b x "$BASE"
git mv old.txt new.txt
printf 'alpha-x\nbeta\ngamma\n' > new.txt
git add -A
git commit -q -m x
X=$(git rev-parse HEAD)

git checkout -q -b y "$BASE"
printf 'alpha\nbeta\ngamma-y\n' > old.txt
git add old.txt
git commit -q -m y
Y=$(git rev-parse HEAD)

git checkout -q -B main "$BASE"
printf 'target\n' > target.txt
git add target.txt
git commit -q -m target
B=$(git rev-parse HEAD)

T1=$(git merge-tree --write-tree "$B" "$X")
export GIT_AUTHOR_NAME='Ruu'
export GIT_AUTHOR_EMAIL='Ruu@example.invalid'
export GIT_COMMITTER_NAME='Ruu'
export GIT_COMMITTER_EMAIL='Ruu@example.invalid'
export GIT_AUTHOR_DATE='@1000000000 +0000'
export GIT_COMMITTER_DATE='@1000000000 +0000'
I1=$(printf 'transient-v1\n' | git commit-tree "$T1" -p "$B" -p "$X")
T2=$(git merge-tree --write-tree "$I1" "$Y")
C1=$(printf 'materialization-v1\n' | git commit-tree "$T2" -p "$B" -p "$X" -p "$Y")
C2=$(printf 'materialization-v1\n' | git commit-tree "$T2" -p "$B" -p "$X" -p "$Y")

[[ "$C1" == "$C2" ]]
git merge-base --is-ancestor "$B" "$C1"
git merge-base --is-ancestor "$X" "$C1"
git merge-base --is-ancestor "$Y" "$C1"
[[ "$(git show "$C1:new.txt")" == $'alpha-x\nbeta\ngamma-y' ]]
[[ "$(git show "$C1:target.txt")" == 'target' ]]

# Demonstrate that the native multi-head default (octopus) is less general for this case.
git checkout -q -B octo "$B"
set +e
OCTOPUS_OUT=$(git merge --no-commit x y 2>&1)
OCTOPUS_RC=$?
set -e
git merge --abort >/dev/null 2>&1 || true
[[ "$OCTOPUS_RC" -ne 0 ]]

printf 'Ruu ADR-048 materialization smoke: PASS\n'
printf 'git_version=%s\n' "$(git --version)"
printf 'pairwise_merge_tree=PASS\n'
printf 'rename_plus_modify=PASS\n'
printf 'multi_parent_commit=PASS\n'
printf 'base_and_all_source_ancestry=PASS\n'
printf 'deterministic_oid_recreation=PASS\n'
printf 'native_octopus_rejected_complex_case=PASS\n'
printf 'candidate_oid=%s\n' "$C1"
