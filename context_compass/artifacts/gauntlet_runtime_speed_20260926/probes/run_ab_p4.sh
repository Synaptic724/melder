#!/bin/bash
# interleaved A/B: device tree (copy_base) vs device tree + P4 (copy); probe_deferred.py in base mode (no deferral), fresh worker thread per lane
for i in $(seq 1 $1); do
  MELDER_ROOT=$HOME/work/copy_base ./venv314t/bin/python -X gil=0 probe_deferred.py base $2 2>&1 | tail -1 | sed 's/^base/tree/'
  MELDER_ROOT=$HOME/work/copy ./venv314t/bin/python -X gil=0 probe_deferred.py base $2 2>&1 | tail -1 | sed "s/^base/p4/"
done
