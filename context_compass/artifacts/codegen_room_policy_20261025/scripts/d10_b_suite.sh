#!/usr/bin/env bash
# D-10 option B: one chunk of the whole suite on the /tmp copy, the GIL off (melder_0, 2026-10-25).
# usage: d10_b_suite.sh <copy dir> <label> <describe> <pytest targets...>
set -u
copy="${1:?copy}"; label="${2:?label}"; describe="${3:?describe}"; shift 3
runs="$HOME/mnt/melder_private/context_compass/artifacts/codegen_room_policy_20261025/runs"
cd "$copy"
out="$runs/d10_${label}_gil0.txt"
{ echo "command: python -X gil=0 -m pytest -p no:cacheprovider -q -rfEx $describe (cwd: $copy, a /tmp copy of the working tree; Python 3.14.7t)"
  echo "ran_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  TMPDIR=/tmp/m0s2/tmp PYTHONDONTWRITEBYTECODE=1 timeout 172 /tmp/m0_venv/bin/python -X gil=0 -m pytest -p no:cacheprovider -q -rfEx "$@" 2>&1 | sed "s#$HOME#~#g" | grep -v "^\.\+ *\[" | tail -30
  echo "exit: ${PIPESTATUS[0]}"; } > "$out"
tail -3 "$out" | cut -c1-220
