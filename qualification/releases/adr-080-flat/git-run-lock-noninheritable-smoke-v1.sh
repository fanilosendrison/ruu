#!/usr/bin/env bash
set -euo pipefail

TMP="$(mktemp -d)"
trap 'set +e; [[ -n "${PARENT_PID:-}" ]] && kill "$PARENT_PID" 2>/dev/null; [[ -n "${CHILD_PID:-}" ]] && kill "$CHILD_PID" 2>/dev/null; rm -rf "$TMP"' EXIT
LOCK="$TMP/run.lock"
INFO="$TMP/info"

python3 - "$LOCK" "$INFO" <<'PY' &
import fcntl, os, subprocess, sys, time
lock_path, info_path = sys.argv[1:]
fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
os.set_inheritable(fd, False)
fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], close_fds=False)
with open(info_path, 'w') as f:
    f.write(f"{os.getpid()} {child.pid}\n")
    f.flush(); os.fsync(f.fileno())
while True:
    time.sleep(1)
PY
PARENT_PID=$!

for _ in $(seq 1 100); do
  [[ -s "$INFO" ]] && break
  sleep 0.02
done
[[ -s "$INFO" ]]
read -r RECORDED_PARENT CHILD_PID < "$INFO"
[[ "$RECORDED_PARENT" = "$PARENT_PID" ]]
kill -0 "$CHILD_PID"

kill -KILL "$PARENT_PID"
wait "$PARENT_PID" 2>/dev/null || true
kill -0 "$CHILD_PID"

python3 - "$LOCK" <<'PY'
import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDWR | os.O_CREAT, 0o600)
fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
print('successor acquisition with surviving child: PASS')
PY

kill "$CHILD_PID" 2>/dev/null || true
wait "$CHILD_PID" 2>/dev/null || true
CHILD_PID=""
echo "run-lock non-inheritance smoke: PASS"
