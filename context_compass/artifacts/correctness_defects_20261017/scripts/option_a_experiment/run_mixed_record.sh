#!/bin/bash
# The mixed-record probe: record on the 0.2.8267 tree, replay in fresh processes on the 0.2.8267 tree and on the
# (A)+(B) tree, the GIL off and on (melder_1, scratch only).
cd /tmp/cc_res/probes_now || exit 1
export TMPDIR=/tmp/cc_res/tmp PYTHONDONTWRITEBYTECODE=1
PY=$HOME/v314t/bin/python
run() { tree=$1; gil=$2; shift 2; PYTHONPATH=/tmp/cc_res/$tree/src:/tmp/cc_res/probes_now timeout 120 $PY -X gil=$gil "$@" 2>&1 \
  | grep -v "optimized for Python\|Performance may\|UserWarning: Python 3.14+ detected\|warnings.warn("; echo "[exit ${PIPESTATUS[0]}]"; }
mkdir -p /tmp/cc_res/state
for gil in 0 1; do
  state=/tmp/cc_res/state/mixed_gil$gil.json
  echo; echo "===== record on the 0.2.8267 tree (-X gil=$gil)"
  run mirror $gil probe_mixed_record_under_option_a.py record $state
  checkpoint=$($PY -c "import json,sys; print(json.load(open(sys.argv[1]))['checkpoint_id'])" $state)
  for tree in mirror mirror_ab; do
    src=$(find /tmp/cc_res/mirror/src/melder/__melder_cache__/__crystallizer_cache__ -name "$checkpoint.json" | head -1)
    rel=${src#/tmp/cc_res/mirror/src/melder/}
    if [ "$tree" != mirror ]; then mkdir -p "$(dirname /tmp/cc_res/$tree/src/melder/$rel)"; cp "$src" "/tmp/cc_res/$tree/src/melder/$rel"; fi
    label=$([ "$tree" = mirror ] && echo "the 0.2.8267 tree" || echo "the (A)+(B) tree")
    echo; echo "===== restore on $label in a fresh process (-X gil=$gil)"
    run $tree $gil probe_mixed_record_under_option_a.py restore $state
    echo; echo "===== graft on $label in a fresh process (-X gil=$gil)"
    run $tree $gil probe_mixed_record_under_option_a.py graft $state
  done
done
