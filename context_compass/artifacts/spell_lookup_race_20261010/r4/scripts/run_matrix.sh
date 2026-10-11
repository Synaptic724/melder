#!/usr/bin/env bash
# usage: run_matrix.sh <rep> <tree...> -> r4/runs/matrix/<tree>_gil<g>_rep<rep>.log (both GIL modes)
export PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/cc_pycache TMPDIR=/tmp
OUT=$HOME/mnt/melder_private/context_compass/artifacts/spell_lookup_race_20261010/r4/runs/matrix
mkdir -p $OUT
rep=$1; shift
for t in "$@"; do
  for g in 0 1; do
    cd /tmp/cc_lookup/$t
    timeout 80 $HOME/v314t/bin/python -X gil=$g -m pytest -p no:cacheprovider -q -rA --tb=line \
      diag/test_lookup_fair_matrix.py > $OUT/${t}_gil${g}_rep${rep}.log 2>&1
    echo "$t gil=$g rep=$rep rc=$? $(tail -1 $OUT/${t}_gil${g}_rep${rep}.log)"
  done
done
