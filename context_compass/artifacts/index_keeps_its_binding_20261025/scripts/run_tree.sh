#!/bin/bash
# Sync the repository's src, tests, .github and pyproject into /tmp/cc_res/mirror and run pytest there (melder_1).
# Usage: run_tree.sh <gil 0|1> <log file> <pytest args...>
set -u
REPO=$HOME/mnt/melder_private
M=/tmp/cc_res/mirror
mkdir -p "$M"
rsync -a --delete --exclude '__pycache__' --exclude '__melder_cache__' --exclude '*.meldercache' "$REPO/src/" "$M/src/"
rsync -a --delete --exclude '__pycache__' --exclude '__melder_cache__' "$REPO/tests/" "$M/tests/"
rsync -a --delete "$REPO/.github/" "$M/.github/"
cp "$REPO/pyproject.toml" "$M/pyproject.toml"
cd "$M" || exit 2
export TMPDIR=/tmp/cc_res/tmp
mkdir -p "$TMPDIR"
GIL=$1
LOG=$2
shift 2
PYTHONPATH="$M/src" timeout 170 "$HOME/v314t/bin/python" -X gil="$GIL" -m pytest -q -p no:cacheprovider "$@" > "$LOG" 2>&1
STATUS=$?
sed -i "s#$HOME#~#g" "$LOG"
echo "exit $STATUS"
tail -3 "$LOG"
