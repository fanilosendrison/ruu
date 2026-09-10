#!/usr/bin/env bash
set -euo pipefail

root="$(mktemp -d "${TMPDIR:-/tmp}/ruu-authoring-dependency.XXXXXX")"
trap 'rm -rf "$root"' EXIT

exercise_format() {
  local label="$1"
  local requested_format="$2"
  local repo="$root/repo-$label"

  if [[ "$requested_format" = "default" ]]; then
    git init -q "$repo"
  else
    git init -q --object-format="$requested_format" "$repo"
  fi

  cd "$repo"
  git config user.name "Ruu Qualification"
  git config user.email "ruu-qualification@example.invalid"

  echo "base" > base.txt
  git add base.txt
  git commit -qm "base"
  local base_oid
  base_oid="$(git rev-parse HEAD)"

  git switch -qc source
  echo "exact-source-version" > source.txt
  git add source.txt
  git commit -qm "source exact A"
  local consumed_oid
  consumed_oid="$(git rev-parse HEAD)"

  echo "producer-dirty-secret" > producer-dirty-secret.txt

  local object_format
  object_format="$(git rev-parse --show-object-format 2>/dev/null || echo sha1)"
  local oid_width
  case "$object_format" in
    sha1) oid_width=40 ;;
    sha256) oid_width=64 ;;
    *) echo "unsupported object format: $object_format" >&2; exit 1 ;;
  esac
  local zero_oid
  zero_oid="$(printf '%*s' "$oid_width" '' | tr ' ' 0)"

  local anchor_ref="refs/ruu/recovery/authoring-dependencies/qualification-$label"
  git update-ref "$anchor_ref" "$consumed_oid" "$zero_oid"
  test "$(git rev-parse "$anchor_ref")" = "$consumed_oid"

  if git ls-tree -r --name-only "$consumed_oid" | grep -q '^producer-dirty-secret.txt$'; then
    echo "dirty producer state entered the consumed commit" >&2
    exit 1
  fi

  git reset -q --hard "$base_oid"
  test "$(git rev-parse source)" = "$base_oid"

  git reflog expire --expire=now --expire-unreachable=now --all
  git gc --prune=now --quiet

  git cat-file -e "$consumed_oid^{commit}"
  test "$(git rev-parse "$anchor_ref")" = "$consumed_oid"
  test "$(git show "$consumed_oid:source.txt")" = "exact-source-version"
  test -f producer-dirty-secret.txt
}

exercise_format "default" "default"

sha256_probe="$root/sha256-probe"
if git init -q --object-format=sha256 "$sha256_probe" >/dev/null 2>&1; then
  rm -rf "$sha256_probe"
  exercise_format "sha256" "sha256"
fi

echo "ADR-081 dependency anchor retention smoke: PASS"
