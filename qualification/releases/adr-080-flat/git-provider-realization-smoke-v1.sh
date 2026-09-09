#!/usr/bin/env bash
# HISTORICAL SMOKE: validates old ADR-065 C→R rewrite shape only; v2 is normative for C→H→R→O.
set -euo pipefail
TD="$(mktemp -d)"
trap 'rm -rf "$TD"' EXIT
cd "$TD"
git init -q -b main
git config user.name Audit
git config user.email audit@example.invalid
printf 'base\n' > base.txt
git add -A && git commit -q -m B
B="$(git rev-parse HEAD)"

git switch -q -c candidate
printf 'one\n' > a.txt
git add -A && git commit -q -m c1
printf 'two\n' > b.txt
git add -A && git commit -q -m c2
C="$(git rev-parse HEAD)"
CTREE="$(git rev-parse "$C^{tree}")"

# Provider-like squash result: same final tree, different commit identity/history.
R="$(printf 'provider squash result\n' | GIT_AUTHOR_NAME=provider GIT_AUTHOR_EMAIL=provider@example.invalid GIT_AUTHOR_DATE='2001-01-01T00:00:00+0000' GIT_COMMITTER_NAME=provider GIT_COMMITTER_EMAIL=provider@example.invalid GIT_COMMITTER_DATE='2001-01-01T00:00:00+0000' git commit-tree "$CTREE" -p "$B")"
[[ "$R" != "$C" ]]
! git merge-base --is-ancestor "$C" "$R"
[[ "$(git rev-parse "$R^{tree}")" == "$CTREE" ]]

# Provider says exact C -> exact R; authoritative target first lands on R.
git update-ref refs/heads/main "$R" "$B"
[[ "$(git rev-parse refs/heads/main)" == "$R" ]]

# Target advances again before Ruu adoption; R remains provable by ancestry.
git switch -q main
printf 'later\n' > later.txt
git add -A && git commit -q -m later
O="$(git rev-parse HEAD)"
git merge-base --is-ancestor "$R" "$O"
! git merge-base --is-ancestor "$C" "$O"

echo "provider-result realization smoke: PASS"
echo "candidate=$C"
echo "provider_result=$R"
echo "observed_target=$O"
