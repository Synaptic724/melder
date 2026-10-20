#!/usr/bin/env bash
# usage: run_chunk.sh <tree> <label> <pytest args...> -> /tmp/cc_lookup/suites_r5/<label>__<tree>.log + summary line
export PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/cc_pycache TMPDIR=/tmp
t=$1; label=$2; shift 2
OUT=/tmp/cc_lookup/suites_r5; mkdir -p $OUT
cd /tmp/cc_lookup/$t
start=$(date +%s)
timeout 165 $HOME/v314t/bin/python -X gil=0 -W ignore::UserWarning -m pytest "$@" -p no:cacheprovider -q -rfE \
  > $OUT/${label}__$t.log 2>&1
rc=$?
echo "$t | $label | rc=$rc | secs=$(( $(date +%s) - start )) | $(tail -1 $OUT/${label}__$t.log)" | tee -a $OUT/summary.txt
