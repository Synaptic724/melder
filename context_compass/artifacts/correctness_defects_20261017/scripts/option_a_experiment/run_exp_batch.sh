#!/bin/bash
# One resumable slice of the option (A) experiment for one scratch tree (melder_1, scratch only).
# Usage: run_exp_batch.sh <tree> <time limit in s> [gil: 0|1, default 0]
tree=$1; limit=$2; gil=${3:-0}
suffix=$tree; if [ "$gil" = "1" ]; then suffix=${tree}_gil1; fi
export TMPDIR=/tmp/cc_res/tmp PYTHONDONTWRITEBYTECODE=1
export EXP_LOG=/tmp/cc_res/exp2_$suffix.tsv EXP_STARTED=/tmp/cc_res/exp2_$suffix.started
cd /tmp/cc_res/$tree || exit 1
PYTHONPATH=/tmp/cc_res/exp_plugin:/tmp/cc_res/$tree/src:/tmp/cc_res/$tree timeout $limit $HOME/v314t/bin/python -X gil=$gil \
  -m pytest $(cat /tmp/cc_res/a_test_files.txt) -q -p exp_log_plugin --tb=no -p no:cacheprovider -o addopts="" \
  > /tmp/cc_res/exp2_$suffix.out 2>&1
echo "exit=$?" >> /tmp/cc_res/exp2_$suffix.out
