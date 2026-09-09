#!/usr/bin/env bash
set -euo pipefail

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

printf "git version: %s\n" "$(git --version | awk '{print $3}')"

pass() { printf '%s\n' "$1: PASS"; }
fail() { printf '%s\n' "$1: FAIL" >&2; exit 1; }

# Smoke 1: native rename of a branch checked out in a linked worktree.
R1="$ROOT/rename"
git init -q "$R1"
cd "$R1"
git config user.name Test
git config user.email test@example.invalid
printf 'base\n' > f
git add f
git commit -qm base
git branch foo
git worktree add -q "$ROOT/wt-foo" foo
mkdir -p "$ROOT/hooks1"
LOG1="$R1/.git/rt.log"
cat > "$ROOT/hooks1/reference-transaction" <<H
#!/usr/bin/env bash
state="\$1"
echo "STATE:\$state" >> "$LOG1"
cat >> "$LOG1"
H
chmod +x "$ROOT/hooks1/reference-transaction"
git config core.hooksPath "$ROOT/hooks1"
OLD=$(git rev-parse refs/heads/foo)
git branch -m foo bar
[ ! -e "$(git rev-parse --git-path refs/heads/foo)" ] || fail rename_old_ref_removed
[ "$(git rev-parse refs/heads/bar)" = "$OLD" ] || fail rename_new_ref_same_oid
[ "$(git -C "$ROOT/wt-foo" symbolic-ref HEAD)" = "refs/heads/bar" ] || fail rename_worktree_head_rebound
git reflog show --format='%gs' refs/heads/bar | grep -F 'renamed refs/heads/foo to refs/heads/bar' >/dev/null || fail rename_reflog_evidence
grep -F 'refs/heads/foo' "$LOG1" >/dev/null || fail rename_reference_transaction_old_ref_seen
pass native_rename_continuity

# Smoke 2: copy then delete is observably copy+delete, not rename.
R2="$ROOT/copy-delete"
git init -q "$R2"
cd "$R2"
git config user.name Test
git config user.email test@example.invalid
printf 'base\n' > f
git add f
git commit -qm base
git branch --create-reflog foo
OID=$(git rev-parse refs/heads/foo)
git branch -c foo bar
[ "$(git rev-parse refs/heads/bar)" = "$OID" ] || fail copy_same_oid_precondition
git reflog show --format='%gs' refs/heads/bar | grep -F 'copied refs/heads/foo to refs/heads/bar' >/dev/null || fail copy_reflog_evidence
git branch -D foo >/dev/null
if git show-ref --verify --quiet refs/heads/foo; then fail copy_delete_old_ref_gone; fi
[ "$(git rev-parse refs/heads/bar)" = "$OID" ] || fail copy_delete_new_ref_survives
git reflog show --format='%gs' refs/heads/bar | grep -F 'renamed refs/heads/foo to refs/heads/bar' >/dev/null && fail copy_delete_not_rename || true
pass copy_then_delete_not_rename

# Smoke 3: prepared failure aborts removal of the protected ref.
R3="$ROOT/prepared-reject"
git init -q "$R3"
cd "$R3"
git config user.name Test
git config user.email test@example.invalid
printf 'base\n' > f
git add f
git commit -qm base
git branch blocked
mkdir -p "$ROOT/hooks3"
cat > "$ROOT/hooks3/reference-transaction" <<'H'
#!/usr/bin/env bash
state="$1"
input=$(cat)
if [ "$state" = prepared ] && printf '%s\n' "$input" | grep -E ' 0{40,64} refs/heads/blocked$' >/dev/null; then
  exit 1
fi
exit 0
H
chmod +x "$ROOT/hooks3/reference-transaction"
git config core.hooksPath "$ROOT/hooks3"
set +e
git branch -D blocked >/dev/null 2>&1
RC=$?
set -e
[ "$RC" -ne 0 ] || fail prepared_failure_rejects_removal
 git show-ref --verify --quiet refs/heads/blocked || fail prepared_failure_leaves_ref
pass prepared_failure_aborts_removal

# Smoke 4: ancestry overlays/completeness are correctness-relevant current state.
R4="$ROOT/ancestry"
git init -q "$R4"
cd "$R4"
git config user.name Test
git config user.email test@example.invalid
printf 'a\n' > f
git add f
git commit -qm A
A=$(git rev-parse HEAD)
printf 'b\n' >> f
git commit -qam B
B=$(git rev-parse HEAD)
printf 'c\n' >> f
git commit -qam C
C=$(git rev-parse HEAD)
REAL_PARENT=$(GIT_NO_REPLACE_OBJECTS=1 git show -s --format=%P "$C")
[ "$REAL_PARENT" = "$B" ] || fail ancestry_real_parent_precondition
git replace "$C" "$A"
[ "$(git show -s --format=%P "$C")" != "$REAL_PARENT" ] || fail replace_changes_effective_view
[ "$(GIT_NO_REPLACE_OBJECTS=1 git show -s --format=%P "$C")" = "$REAL_PARENT" ] || fail no_replace_recovers_native_view
git replace -d "$C" >/dev/null
printf '%s\n' "$C" > .git/info/grafts
[ -z "$(git show -s --format=%P "$C" 2>/dev/null)" ] || fail graft_changes_parent_view
[ -z "$(GIT_NO_REPLACE_OBJECTS=1 git show -s --format=%P "$C" 2>/dev/null)" ] || fail graft_not_disabled_by_no_replace
rm .git/info/grafts
CLONE="$ROOT/shallow"
git clone -q --depth 1 "file://$R4" "$CLONE"
[ -s "$CLONE/.git/shallow" ] || fail shallow_boundary_detectable
pass ancestry_environment_detectable

# Smoke 5: a branch-specific empty reflog baseline is enough for later native rename evidence,
# even when repository-wide automatic reflog creation is disabled.
R5="$ROOT/reflog-baseline"
git init -q "$R5"
cd "$R5"
git config user.name Test
git config user.email test@example.invalid
git config core.logAllRefUpdates false
printf 'base\n' > f
git add f
git commit -qm base
git branch foo
LF=$(git rev-parse --git-path logs/refs/heads/foo)
[ ! -e "$LF" ] || rm -f "$LF"
mkdir -p "$(dirname "$LF")"
: > "$LF"
git branch -m foo bar
LB=$(git rev-parse --git-path logs/refs/heads/bar)
[ -s "$LB" ] || fail reflog_baseline_rename_log_created
git reflog show --format='%gs' refs/heads/bar | grep -F 'renamed refs/heads/foo to refs/heads/bar' >/dev/null || fail reflog_baseline_rename_evidence
pass reflog_baseline_supports_future_rename_evidence

printf 'git-native observation smoke v2: PASS\n'
