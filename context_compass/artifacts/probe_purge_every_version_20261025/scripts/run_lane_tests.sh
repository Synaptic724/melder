#!/bin/bash
# Run this lane's tests on the mirror of the current tree, the GIL off and on (melder_1).
# Usage: run_lane_tests.sh <label> [extra pytest paths...]; output in ../runs/<label>_gil0.txt and _gil1.txt.
HERE=$(cd "$(dirname "$0")/.." && pwd)
REPO=$HOME/mnt/melder_private
label=$1; shift
timeout 100 rsync -a --delete --exclude '__pycache__' --exclude '__melder_cache__' --exclude '.pytest_cache' \
  "$REPO/src" "$REPO/tests" "$REPO/pyproject.toml" /tmp/cc_res/mirror/ || exit 1
cd /tmp/cc_res/mirror || exit 1
mkdir -p /tmp/cc_res/tmp
export TMPDIR=/tmp/cc_res/tmp PYTHONDONTWRITEBYTECODE=1
PY=$HOME/v314t/bin/python
paths="tests/component/melder/aether/conduit/test_conduit_component_probe_and_purge_reach_every_version.py tests/integration/melder/conduit/test_conduit_integration_probe_and_purge_during_notches.py $*"
for gil in 0 1; do
  out="$HERE/runs/${label}_gil${gil}.txt"
  echo "# $(tail -1 src/melder/__version__.py) -X gil=$gil: $paths" > "$out"
  timeout 170 $PY -X gil=$gil -m pytest -q -rfE -p no:cacheprovider $paths >> "$out" 2>&1
  echo "[exit $?]" >> "$out"
  sed -i "s#$HOME#~#g" "$out"
  tail -3 "$out"
done
