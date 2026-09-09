#!/usr/bin/env bash
set -euo pipefail
ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT
pass(){ printf '%s\n' "$1: PASS"; }
fail(){ printf '%s\n' "$1: FAIL" >&2; exit 1; }
printf 'git version: %s\n' "$(git --version | awk '{print $3}')"

REMOTE="$ROOT/remote.git"
A="$ROOT/a"
B="$ROOT/b"
git init -q --bare "$REMOTE"
git clone -q "$REMOTE" "$A"
git -C "$A" config user.name A
git -C "$A" config user.email a@example.invalid
printf 'base\n' > "$A/f"
git -C "$A" add f
git -C "$A" commit -qm base
git -C "$A" branch -M main
git -C "$A" push -q -u origin main
OLD="$(git -C "$A" rev-parse HEAD)"
git clone -q "$REMOTE" "$B"
git -C "$B" config user.name B
git -C "$B" config user.email b@example.invalid
git -C "$B" checkout -q main

# B advances the authoritative remote while A's tracking ref stays stale.
printf 'b\n' >> "$B/f"
git -C "$B" commit -qam b
BNEW="$(git -C "$B" rev-parse HEAD)"
git -C "$B" push -q origin main
TRACKING_A="$(git -C "$A" rev-parse refs/remotes/origin/main)"
DIRECT_A="$(git -C "$A" ls-remote origin refs/heads/main | awk '{print $1}')"
[ "$TRACKING_A" = "$OLD" ] || fail remote_tracking_expected_stale
[ "$DIRECT_A" = "$BNEW" ] || fail direct_remote_observation_current
pass remote_tracking_is_stale_cache
pass direct_remote_observation_current

# A prepares a candidate but stale expected-old must reject.
git -C "$A" checkout -q -B candidate "$OLD"
printf 'a\n' >> "$A/f"
git -C "$A" commit -qam a
CAND="$(git -C "$A" rev-parse HEAD)"
set +e
git -C "$A" push --porcelain --force-with-lease=refs/heads/main:"$OLD" origin "$CAND":refs/heads/main >"$ROOT/stale.out" 2>"$ROOT/stale.err"
RC=$?
set -e
[ "$RC" -ne 0 ] || fail exact_old_remote_cas_rejects_stale
[ "$(git -C "$A" ls-remote origin refs/heads/main | awk '{print $1}')" = "$BNEW" ] || fail stale_cas_preserves_remote
pass exact_old_remote_cas_rejects_stale

# Re-observe, build a descendant, and exact current expected-old succeeds.
git -C "$A" fetch -q origin main
git -C "$A" checkout -q -B candidate2 "$BNEW"
printf 'a2\n' >> "$A/f"
git -C "$A" commit -qam a2
CAND2="$(git -C "$A" rev-parse HEAD)"
git -C "$A" push -q --force-with-lease=refs/heads/main:"$BNEW" origin "$CAND2":refs/heads/main
[ "$(git -C "$A" ls-remote origin refs/heads/main | awk '{print $1}')" = "$CAND2" ] || fail exact_old_remote_cas_success
pass exact_old_remote_cas_success

# Remote deletion is current remotely even if a local tracking ref remains stale.
git -C "$B" fetch -q origin
git -C "$B" branch -f temp "$CAND2"
git -C "$B" push -q origin temp
git -C "$A" fetch -q origin temp:refs/remotes/origin/temp
TRACK_TEMP="$(git -C "$A" rev-parse refs/remotes/origin/temp)"
[ "$TRACK_TEMP" = "$CAND2" ] || fail tracking_temp_created
git -C "$B" push -q origin :refs/heads/temp
# A's tracking ref intentionally remains until another fetch/prune.
[ "$(git -C "$A" rev-parse refs/remotes/origin/temp)" = "$CAND2" ] || fail tracking_temp_expected_stale_after_remote_delete
set +e
git -C "$A" ls-remote --exit-code origin refs/heads/temp >"$ROOT/temp.out" 2>"$ROOT/temp.err"
RC2=$?
set -e
[ "$RC2" -eq 2 ] || fail direct_remote_deletion_observed
pass remote_deletion_not_equal_tracking_cache
pass provider_free_bare_remote_progression
printf 'git-remote observation smoke v1: PASS\n'
