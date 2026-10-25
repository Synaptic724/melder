#!/bin/bash
# Run pytest paths on the mirror of the current tree in one GIL mode (melder_1).
# Usage: run_tree.sh <label> <gil 0|1> <pytest paths...>; output in ../runs/<label>_gil<gil>.txt.
HERE=$(cd "$(dirname "$0")/.." && pwd)
REPO=$HOME/mnt/melder_private
label=$1; gil=$2; shift 2
timeout 60 rsync -a --delete --exclude '__pycache__' --exclude '__melder_cache__' --exclude '.pytest_cache' \
  "$REPO/src" "$REPO/tests" "$REPO/.github" "$REPO/pyproject.toml" /tmp/cc_res/mirror/ || exit 1
cd /tmp/cc_res/mirror || exit 1
mkdir -p /tmp/cc_res/tmp
export TMPDIR=/tmp/cc_res/tmp PYTHONDONTWRITEBYTECODE=1
PY=$HOME/v314t/bin/python
out="$HERE/runs/${label}_gil${gil}.txt"
echo "# $(grep -m1 '__version__ =' src/melder/__version__.py) -X gil=$gil: $*" > "$out"
start=$(date +%s)
timeout 160 $PY -X gil=$gil -m pytest -q -rfE -p no:cacheprovider "$@" >> "$out" 2>&1
echo "[exit $?] [$(( $(date +%s) - start )) s]" >> "$out"
sed -i "s#$HOME#~#g" "$out"
tail -4 "$out"
