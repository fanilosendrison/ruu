#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

printf "git version: %s\n" "$(git --version | awk '{print $3}')"
pass() { printf '%s\n' "$1: PASS"; }
fail() { printf '%s\n' "$1: FAIL" >&2; exit 1; }

# Retain all ADR-074 regressions first.
bash "$DIR/git-native-observation-smoke-v2.sh" >/dev/null
pass retained_v2_regressions

make_repo() {
  local fmt="$1" dst="$2"
  git init -q --ref-format="$fmt" "$dst"
  git -C "$dst" config user.name Test
  git -C "$dst" config user.email test@example.invalid
  printf 'base\n' > "$dst/f"
  git -C "$dst" add f
  git -C "$dst" commit -qm base
}

install_files_classifier_hook() {
  local repo="$1" log="$2"
  local hooks="$ROOT/hooks-$(basename "$repo")"
  mkdir -p "$hooks"
  cat > "$hooks/reference-transaction" <<H
#!/usr/bin/env bash
set -eu
state="\$1"
common="\$(git rev-parse --git-common-dir)"
zero='0000000000000000000000000000000000000000'
while read old new ref; do
  [ "\$state" = prepared ] || continue
  case "\$ref" in refs/heads/*) ;; *) continue ;; esac
  short="\${ref#refs/heads/}"
  ownlog="\$common/logs/refs/heads/\$short"
  tmplog="\$common/logs/refs/.tmp-renamed-log"
  actual="\$old"
  if [ "\$actual" = "\$zero" ]; then
    actual="\$(git rev-parse "\$ref" 2>/dev/null || true)"
  fi
  own=no; tmp=no
  [ -e "\$ownlog" ] && own=yes
  [ -e "\$tmplog" ] && tmp=yes
  if [ "\$own" = yes ]; then rel=TERMINAL_REMOVAL_PREPARED
  elif [ "\$tmp" = yes ]; then rel=RENAME_CARRY_PREPARED
  else rel=UNKNOWN
  fi
  printf '%s ref=%s actual=%s own=%s tmp=%s\n' "\$rel" "\$ref" "\$actual" "\$own" "\$tmp" >> "$log"
done
H
  chmod +x "$hooks/reference-transaction"
  git -C "$repo" config core.hooksPath "$hooks"
}

# Smoke 1: files backend native rename produces rename-carry preparation and exact preimage.
R1="$ROOT/files-rename"
make_repo files "$R1"
git -C "$R1" branch foo
OID1="$(git -C "$R1" rev-parse refs/heads/foo)"
L1="$ROOT/files-rename.log"; : > "$L1"
install_files_classifier_hook "$R1" "$L1"
git -C "$R1" branch -m foo bar
grep -F "RENAME_CARRY_PREPARED ref=refs/heads/foo actual=$OID1" "$L1" >/dev/null || fail files_rename_carry_prepared
pass files_rename_carry_prepared

# Smoke 2: files backend terminal delete stays attached to old reflog and can recover true preimage even with zero-old force semantics.
R2="$ROOT/files-delete"
make_repo files "$R2"
git -C "$R2" branch foo
OID2="$(git -C "$R2" rev-parse refs/heads/foo)"
L2="$ROOT/files-delete.log"; : > "$L2"
install_files_classifier_hook "$R2" "$L2"
git -C "$R2" branch -D foo >/dev/null
grep -F "TERMINAL_REMOVAL_PREPARED ref=refs/heads/foo actual=$OID2" "$L2" >/dev/null || fail files_terminal_removal_prepared
pass files_terminal_removal_prepared

# Smoke 3: files forced rename over an existing destination yields source rename-carry + destination terminal-removal preparation.
R3="$ROOT/files-force-rename"
make_repo files "$R3"
git -C "$R3" branch foo
git -C "$R3" branch bar
F3="$(git -C "$R3" rev-parse refs/heads/foo)"
B3="$(git -C "$R3" rev-parse refs/heads/bar)"
L3="$ROOT/files-force.log"; : > "$L3"
install_files_classifier_hook "$R3" "$L3"
git -C "$R3" branch -M foo bar
grep -F "RENAME_CARRY_PREPARED ref=refs/heads/foo actual=$F3" "$L3" >/dev/null || fail files_force_rename_source
# destination force-delete often presents old=zero; actual preimage must still be recovered from the live ref
# (same OID in this simple repo is fine; the semantic distinction comes from the destination's own reflog remaining attached).
grep -F "TERMINAL_REMOVAL_PREPARED ref=refs/heads/bar actual=$B3" "$L3" >/dev/null || fail files_force_rename_destination
pass files_force_rename_two_bindings

# Smoke 4: pre-linearization persistence/veto failure keeps managed ref intact.
R4="$ROOT/veto"
make_repo files "$R4"
git -C "$R4" branch blocked
H4="$ROOT/hooks-veto"; mkdir -p "$H4"
cat > "$H4/reference-transaction" <<'H'
#!/usr/bin/env bash
state="$1"
cat >/dev/null
[ "$state" = prepared ] && exit 1
exit 0
H
chmod +x "$H4/reference-transaction"
git -C "$R4" config core.hooksPath "$H4"
set +e
git -C "$R4" branch -D blocked >/dev/null 2>&1
rc=$?
set -e
[ "$rc" -ne 0 ] || fail prelinearization_veto_effective
git -C "$R4" show-ref --verify --quiet refs/heads/blocked || fail prelinearization_veto_preserves_ref
pass prelinearization_veto_effective

# Smoke 5: stock reftable terminal delete is callback-visible, but rename is not in tested Git.
R5="$ROOT/reftable"
make_repo reftable "$R5"
H5="$ROOT/hooks-reftable"; mkdir -p "$H5"
L5="$ROOT/reftable.log"; : > "$L5"
cat > "$H5/reference-transaction" <<H
#!/usr/bin/env bash
state="\$1"
while read old new ref; do printf '%s %s %s %s\n' "\$state" "\$old" "\$new" "\$ref" >> "$L5"; done
H
chmod +x "$H5/reference-transaction"
git -C "$R5" config core.hooksPath "$H5"
git -C "$R5" branch foo
: > "$L5"
git -C "$R5" branch -D foo >/dev/null
grep -F 'refs/heads/foo' "$L5" >/dev/null || fail reftable_delete_callback_visible
pass reftable_delete_callback_visible

git -C "$R5" branch foo
: > "$L5"
git -C "$R5" branch -m foo baz
[ ! -s "$L5" ] || fail reftable_rename_bypass_detected
pass reftable_rename_bypass_detected

# Smoke 6: stock reftable forced rename can replace an existing destination with zero callback coverage.
git -C "$R5" branch foo
git -C "$R5" branch bar
: > "$L5"
git -C "$R5" branch -M foo bar
[ ! -s "$L5" ] || fail reftable_force_rename_bypass_detected
[ "$(git -C "$R5" rev-parse refs/heads/bar)" = "$(git -C "$R5" rev-parse HEAD)" ] || fail reftable_force_rename_result
pass reftable_force_rename_bypass_detected

printf 'git-native observation smoke v3: PASS\n'
