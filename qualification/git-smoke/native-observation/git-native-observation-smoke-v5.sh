#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(mktemp -d)"
cleanup() {
  set +e
  jobs -p | xargs -r kill >/dev/null 2>&1
  rm -rf "$ROOT"
}
trap cleanup EXIT

printf 'git version: %s\n' "$(git --version | awk '{print $3}')"
pass() { printf '%s\n' "$1: PASS"; }
fail() { printf '%s\n' "$1: FAIL" >&2; exit 1; }

bash "$DIR/git-native-observation-smoke-v4.sh" >/dev/null
pass retained_v4_regressions

make_repo() {
  local dst="$1"
  git init -q --ref-format=files "$dst"
  git -C "$dst" config user.name Test
  git -C "$dst" config user.email test@example.invalid
  printf 'base\n' > "$dst/f"
  git -C "$dst" add f
  git -C "$dst" commit -qm base
}

wait_for() {
  local pattern="$1" file="$2"
  local i
  for i in $(seq 1 100); do
    grep -F "$pattern" "$file" >/dev/null 2>&1 && return 0
    sleep 0.02
  done
  return 1
}

# 1. Existing-ref exact no-op prepared transaction holds native exclusion and is semantically no-op.
R1="$ROOT/existing-barrier"
W1="$ROOT/existing-wt"
make_repo "$R1"
BASE1="$(git -C "$R1" rev-parse HEAD)"
printf 'next\n' >> "$R1/f"
git -C "$R1" commit -qam next
OTHER1="$(git -C "$R1" rev-parse HEAD)"
git -C "$R1" branch candidate "$BASE1"
git -C "$R1" worktree add -q "$W1" candidate
COMMON1="$(git -C "$R1" rev-parse --git-common-dir)"; case "$COMMON1" in /*) ;; *) COMMON1="$R1/$COMMON1";; esac
H1="$COMMON1/hooks/reference-transaction"; L1="$ROOT/existing.log"; : > "$L1"
mkdir -p "$(dirname "$H1")"
cat > "$H1" <<H
#!/usr/bin/env bash
state="\$1"
while read old new ref; do printf '%s %s %s %s\n' "\$state" "\$old" "\$new" "\$ref" >> "$L1"; done
H
chmod +x "$H1"
FIFO1="$ROOT/fifo1"; mkfifo "$FIFO1"
git -C "$R1" update-ref --stdin < "$FIFO1" >"$ROOT/u1.out" 2>"$ROOT/u1.err" &
P1=$!
exec 31>"$FIFO1"
printf 'start\nupdate refs/heads/candidate %s %s\nprepare\n' "$BASE1" "$BASE1" >&31
wait_for "prepared $BASE1 $BASE1 refs/heads/candidate" "$L1" || fail existing_barrier_prepared_visible
set +e
git -C "$R1" update-ref refs/heads/candidate "$OTHER1" "$BASE1" >"$ROOT/concurrent1.out" 2>"$ROOT/concurrent1.err"
RC1=$?
set -e
[ "$RC1" -ne 0 ] || fail existing_barrier_blocks_concurrent_ref_mutation
printf 'abort\n' >&31
exec 31>&-
wait "$P1"
[ "$(git -C "$R1" rev-parse refs/heads/candidate)" = "$BASE1" ] || fail existing_barrier_preserves_oid
grep -F "aborted $BASE1 $BASE1 refs/heads/candidate" "$L1" >/dev/null || fail existing_barrier_aborted_noop_visible
pass existing_ref_noop_admission_barrier

# 2. Exact absence verify + prepare locks a future ref and exposes zero->zero, not deletion semantics.
R2="$ROOT/absent-barrier"
make_repo "$R2"
ZERO="$(printf '%040d' 0)"
COMMON2="$(git -C "$R2" rev-parse --git-common-dir)"; case "$COMMON2" in /*) ;; *) COMMON2="$R2/$COMMON2";; esac
H2="$COMMON2/hooks/reference-transaction"; L2="$ROOT/absent.log"; : > "$L2"
mkdir -p "$(dirname "$H2")"
cat > "$H2" <<H
#!/usr/bin/env bash
state="\$1"
while read old new ref; do printf '%s %s %s %s\n' "\$state" "\$old" "\$new" "\$ref" >> "$L2"; done
H
chmod +x "$H2"
FIFO2="$ROOT/fifo2"; mkfifo "$FIFO2"
git -C "$R2" update-ref --stdin < "$FIFO2" >"$ROOT/u2.out" 2>"$ROOT/u2.err" &
P2=$!
exec 32>"$FIFO2"
printf 'start\nverify refs/heads/future %s\nprepare\n' "$ZERO" >&32
wait_for "prepared $ZERO $ZERO refs/heads/future" "$L2" || fail absent_barrier_zero_zero_visible
set +e
git -C "$R2" update-ref refs/heads/future HEAD >"$ROOT/concurrent2.out" 2>"$ROOT/concurrent2.err"
RC2=$?
set -e
[ "$RC2" -ne 0 ] || fail absent_barrier_blocks_concurrent_creation
printf 'abort\n' >&32
exec 32>&-
wait "$P2"
git -C "$R2" show-ref --verify --quiet refs/heads/future && fail absent_barrier_keeps_ref_absent
pass absent_ref_admission_barrier

# 3. A worktree lock does not freeze HEAD; correctness must come from authority + exact handoff revalidation.
R3="$ROOT/worktree-lock"
W3="$ROOT/worktree-locked"
make_repo "$R3"
git -C "$R3" worktree add -q --lock -b candidate "$W3" HEAD
BEFORE3="$(git -C "$W3" symbolic-ref -q HEAD)"
[ "$BEFORE3" = refs/heads/candidate ] || fail worktree_lock_initial_symbolic_head
# Detach while the worktree remains administratively locked.
git -C "$W3" switch --detach -q HEAD
git -C "$W3" symbolic-ref -q HEAD >/dev/null 2>&1 && fail worktree_lock_unexpectedly_froze_head
LOCKED3="$(git -C "$R3" worktree list --porcelain | awk -v p="$W3" 'BEGIN{found=0} $1=="worktree" && $2==p{found=1} found && $1=="locked"{print "yes"; exit}')"
[ "$LOCKED3" = yes ] || fail worktree_remains_locked_after_detach
pass worktree_lock_is_not_authoring_topology_fence

printf 'git-native observation smoke v5: PASS\n'
