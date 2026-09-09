#!/usr/bin/env bash
set -euo pipefail
TD="$(mktemp -d)"
trap 'rm -rf "$TD"' EXIT
cd "$TD"
git init -q -b main
git config user.name Audit
git config user.email audit@example.invalid
printf 'base\n' > base.txt
git add -A && git commit -q -m B0
B0="$(git rev-parse HEAD)"

# Immutable internal candidate C over B0.
git switch -q -c candidate "$B0"
printf 'child\n' > child.txt
git add -A && git commit -q -m C
C="$(git rev-parse HEAD)"

# Predecessor/base moves to B1 without containing C.
git switch -q -c newbase "$B0"
printf 'pred\n' > pred.txt
git add -A && git commit -q -m B1
B1="$(git rev-parse HEAD)"

# ADR-050 exact state transplant: (B0,C) onto B1 => provider-facing H.
HTREE="$(git merge-tree --write-tree --merge-base="$B0" "$B1" "$C" | head -n1)"
H="$(printf 'restacked submission H\n' | \
  GIT_AUTHOR_NAME=gc GIT_AUTHOR_EMAIL=gc@example.invalid GIT_AUTHOR_DATE='2000-01-01T00:00:00+0000' \
  GIT_COMMITTER_NAME=gc GIT_COMMITTER_EMAIL=gc@example.invalid GIT_COMMITTER_DATE='2000-01-01T00:00:00+0000' \
  git commit-tree "$HTREE" -p "$B1")"
[[ "$C" != "$H" ]]
! git merge-base --is-ancestor "$C" "$H"
git ls-tree -r --name-only "$H" | grep -qx child.txt
git ls-tree -r --name-only "$H" | grep -qx pred.txt

# Provider-like squash/finalization: exact submitted H -> exact result R.
R="$(printf 'provider final result R\n' | \
  GIT_AUTHOR_NAME=provider GIT_AUTHOR_EMAIL=provider@example.invalid GIT_AUTHOR_DATE='2001-01-01T00:00:00+0000' \
  GIT_COMMITTER_NAME=provider GIT_COMMITTER_EMAIL=provider@example.invalid GIT_COMMITTER_DATE='2001-01-01T00:00:00+0000' \
  git commit-tree "$HTREE" -p "$B1")"
[[ "$H" != "$R" ]]
! git merge-base --is-ancestor "$H" "$R"
[[ "$(git rev-parse "$H^{tree}")" == "$(git rev-parse "$R^{tree}")" ]]

# Authoritative target is at B1, provider realizes exact R.
git update-ref refs/heads/main "$B1" "$B0"
git update-ref refs/heads/main "$R" "$B1"
[[ "$(git rev-parse refs/heads/main)" == "$R" ]]

# Target advances again before adoption.
git switch -q main
printf 'later\n' > later.txt
git add -A && git commit -q -m O
O="$(git rev-parse HEAD)"
git merge-base --is-ancestor "$R" "$O"
! git merge-base --is-ancestor "$H" "$O"
! git merge-base --is-ancestor "$C" "$O"

echo "provider-route C-H-R-O realization smoke: PASS"
echo "candidate=$C"
echo "submitted_revision=$H"
echo "provider_result=$R"
echo "observed_target=$O"
