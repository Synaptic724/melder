#!/bin/bash
# probe_meld_identities_across_a_notch.py on the 0.2.8267 tree, every case, the GIL off and on; and the renamed bare
# staging on the (A)+(B) scratch tree, where the way-in check refuses it (melder_1, scratch only).
cd /tmp/cc_res/probes_now || exit 1
export TMPDIR=/tmp/cc_res/tmp PYTHONDONTWRITEBYTECODE=1
PY=$HOME/v314t/bin/python
run() { tree=$1; gil=$2; shift 2; PYTHONPATH=/tmp/cc_res/$tree/src:/tmp/cc_res/probes_now timeout 120 $PY -X gil=$gil "$@" 2>&1 \
  | grep -v "optimized for Python\|Performance may\|UserWarning: Python 3.14+ detected\|warnings.warn(" | grep -v "^  File \|^    \|^Traceback"; echo "[exit ${PIPESTATUS[0]}]"; }
for gil in 0 1; do
  for c in protocol bare_same_name bare_renamed bare_renamed_a; do
    echo; echo "===== $c on the 0.2.8267 tree (-X gil=$gil)"; run mirror $gil probe_meld_identities_across_a_notch.py $c
  done
  echo; echo "===== bare_renamed on the (A)+(B) tree (-X gil=$gil): the staging is refused"
  run mirror_ab $gil probe_meld_identities_across_a_notch.py bare_renamed
done
