#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

printf 'git version: %s\n' "$(git --version | awk '{print $3}')"
pass() { printf '%s\n' "$1: PASS"; }
fail() { printf '%s\n' "$1: FAIL" >&2; exit 1; }

bash "$DIR/git-native-observation-smoke-v3.sh" >/dev/null
pass retained_v3_regressions

make_repo() {
  local dst="$1"
  git init -q --ref-format=files "$dst"
  git -C "$dst" config user.name Test
  git -C "$dst" config user.email test@example.invalid
  printf 'base\n' > "$dst/f"
  git -C "$dst" add f
  git -C "$dst" commit -qm base
}

# 1. Traditional hook resolution is repository-common across linked worktrees.
R1="$ROOT/common-hooks"
W1="$ROOT/linked"
make_repo "$R1"
git -C "$R1" worktree add -q -b linked "$W1" HEAD
git -C "$R1" branch managed-probe
COMMON1="$(git -C "$W1" rev-parse --git-common-dir)"
case "$COMMON1" in /*) ;; *) COMMON1="$W1/$COMMON1" ;; esac
COMMON1="$(cd "$COMMON1" && pwd)"
H1="$COMMON1/hooks/reference-transaction"
L1="$ROOT/common-hook.log"
mkdir -p "$(dirname "$H1")"; : > "$L1"
cat > "$H1" <<H
#!/usr/bin/env bash
state="\$1"
while read old new ref; do
  printf '%s %s %s %s common=%s\n' "\$state" "\$old" "\$new" "\$ref" "\$(git rev-parse --git-common-dir)" >> "$L1"
done
H
chmod +x "$H1"
git -C "$W1" branch -D managed-probe >/dev/null
grep -F 'refs/heads/managed-probe' "$L1" >/dev/null || fail linked_worktree_common_hook_visible
pass linked_worktree_common_hook_visible

# 2. Functional attestation: observer is reached and a prepared veto prevents probe ref linearization.
R2="$ROOT/veto-attest"
make_repo "$R2"
H2="$R2/.git/hooks/reference-transaction"
L2="$ROOT/veto-attest.log"; : > "$L2"
cat > "$H2" <<H
#!/usr/bin/env bash
state="\$1"
seen=0
while read old new ref; do
  printf '%s %s %s %s\n' "\$state" "\$old" "\$new" "\$ref" >> "$L2"
  if [ "\$state" = prepared ] && [ "\$ref" = refs/heads/Ruu-probe-veto ]; then seen=1; fi
done
[ "\$seen" -eq 1 ] && exit 1
exit 0
H
chmod +x "$H2"
set +e
git -C "$R2" update-ref refs/heads/Ruu-probe-veto HEAD >/dev/null 2>&1
rc=$?
set -e
[ "$rc" -ne 0 ] || fail functional_attestation_veto_returned_failure
git -C "$R2" show-ref --verify --quiet refs/heads/Ruu-probe-veto && fail functional_attestation_veto_prevented_ref
# Git 2.47 has prepared rather than 2.54's earlier preparing veto path; this still proves the retained ADR-075 candidate profile.
grep -F 'prepared ' "$L2" | grep -F 'refs/heads/Ruu-probe-veto' >/dev/null || fail functional_attestation_observer_reached
pass functional_attestation_veto_effective

# 3. A foreign core.hooksPath changes the effective observer surface; the common traditional hook must not be assumed active.
R3="$ROOT/foreign-hooks-path"
make_repo "$R3"
COMMON_HOOK="$R3/.git/hooks/reference-transaction"
COMMON_LOG="$ROOT/common-default.log"; : > "$COMMON_LOG"
cat > "$COMMON_HOOK" <<H
#!/usr/bin/env bash
cat >/dev/null
printf 'default-called %s\n' "\$1" >> "$COMMON_LOG"
H
chmod +x "$COMMON_HOOK"
FOREIGN="$ROOT/foreign-hooks"; mkdir -p "$FOREIGN"
FOREIGN_LOG="$ROOT/foreign.log"; : > "$FOREIGN_LOG"
cat > "$FOREIGN/reference-transaction" <<H
#!/usr/bin/env bash
cat >/dev/null
printf 'foreign-called %s\n' "\$1" >> "$FOREIGN_LOG"
H
chmod +x "$FOREIGN/reference-transaction"
git -C "$R3" config core.hooksPath "$FOREIGN"
git -C "$R3" update-ref refs/heads/foreign-path-probe HEAD
[ -s "$FOREIGN_LOG" ] || fail foreign_core_hookspath_effective
[ ! -s "$COMMON_LOG" ] || fail foreign_core_hookspath_bypasses_default
[ "$(git -C "$R3" config --path core.hooksPath)" = "$FOREIGN" ] || fail foreign_core_hookspath_preserved
pass foreign_core_hookspath_detected_without_takeover

printf 'git-native observation smoke v4: PASS\n'
