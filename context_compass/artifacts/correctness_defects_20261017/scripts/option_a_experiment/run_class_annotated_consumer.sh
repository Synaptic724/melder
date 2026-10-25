#!/bin/bash
# diag_class_annotated_consumer_after_notch_back.py on the 0.2.8267 tree, every case, the GIL off and on (melder_1).
cd /tmp/cc_res/probes_now || exit 1
export TMPDIR=/tmp/cc_res/tmp PYTHONDONTWRITEBYTECODE=1
PY=$HOME/v314t/bin/python
for gil in 0 1; do
  for c in framed bare framed_bind_later bare_bind_later; do
    echo; echo "===== $c on the 0.2.8267 tree (-X gil=$gil)"
    PYTHONPATH=/tmp/cc_res/mirror/src:/tmp/cc_res/probes_now timeout 120 $PY -X gil=$gil \
      diag_class_annotated_consumer_after_notch_back.py $c 2>&1 \
      | grep -v "optimized for Python\|Performance may\|UserWarning: Python 3.14+ detected\|warnings.warn("
    echo "[exit ${PIPESTATUS[0]}]"
  done
done
