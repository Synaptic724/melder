#!/bin/bash
# interleaved A/B: device tree (base) vs device tree + P3, probe_deferred.py without manual deferral
for i in $(seq 1 $1); do
  MELDER_ROOT=$HOME/work/copy_base ./venv314t/bin/python -X gil=0 probe_deferred.py base $2 2>&1 | tail -1 | sed 's/^base/tree/'
  MELDER_ROOT=$HOME/work/copy ./venv314t/bin/python -X gil=0 probe_deferred.py base $2 2>&1 | tail -1 | sed 's/^base/p3/'
done
