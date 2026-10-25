#!/bin/bash
# probe_parked_doors_today.py on the mirror of the current tree, every case, the GIL off and on (melder_1).
# The mirror (/tmp/cc_res/mirror) is an rsync of the repository's src and tests, so nothing is written into the repo.
HERE=$(cd "$(dirname "$0")/.." && pwd)
cd /tmp/cc_res/mirror || exit 1
mkdir -p /tmp/cc_res/tmp
export TMPDIR=/tmp/cc_res/tmp PYTHONDONTWRITEBYTECODE=1
PY=$HOME/v314t/bin/python
run() { gil=$1; shift; PYTHONPATH=/tmp/cc_res/mirror/src:/tmp/cc_res/mirror timeout 120 $PY -X gil=$gil "$@" 2>&1 \
  | grep -v "optimized for Python\|Performance may\|UserWarning: Python 3.14+ detected\|warnings.warn(" \
  | grep -v "^  File \|^    \|^Traceback"; echo "[exit ${PIPESTATUS[0]}]"; }
for gil in 0 1; do
  for c in instance spell_object existing active_existing unstamped split transfer borrowers; do
    echo; echo "===== $c on $(tail -1 src/melder/__version__.py) (-X gil=$gil)"
    run $gil "$HERE/probes/probe_parked_doors_today.py" $c
  done
done
