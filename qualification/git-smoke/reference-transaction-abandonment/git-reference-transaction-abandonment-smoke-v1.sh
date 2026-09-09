#!/usr/bin/env bash
set -euo pipefail
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q repo
cd repo
git config user.name smoke
git config user.email smoke@example.invalid
echo base > f
git add f
git commit -qm base
mkdir -p .githooks
cat > .githooks/reference-transaction <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
phase="$1"
input="$(cat)"
printf '%s|%s\n' "$phase" "$input" >> "${REF_TXN_LOG:?}"
if [[ "$phase" == prepared && "${FAIL_PREPARED:-0}" == 1 ]]; then
  exit 73
fi
HOOK
chmod +x .githooks/reference-transaction
git config core.hooksPath .githooks
export REF_TXN_LOG="$PWD/.git/ref-txn.log"

git branch topic
old="$(git rev-parse refs/heads/topic)"
git branch -D topic >/dev/null
zero="$(printf '%040d' 0)"
grep -E "^prepared\|[0-9a-f]{40} $zero refs/heads/topic$" .git/ref-txn.log >/dev/null
grep -E "^committed\|[0-9a-f]{40} $zero refs/heads/topic$" .git/ref-txn.log >/dev/null
! git show-ref --verify --quiet refs/heads/topic

git branch blocked
set +e
FAIL_PREPARED=1 git branch -D blocked >/dev/null 2>&1
rc=$?
set -e
[[ $rc -ne 0 ]]
git show-ref --verify --quiet refs/heads/blocked

echo "reference-transaction managed deletion commit: PASS"
echo "reference-transaction prepared failure aborts deletion: PASS"
