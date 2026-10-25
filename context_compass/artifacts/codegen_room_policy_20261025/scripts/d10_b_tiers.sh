#!/usr/bin/env bash
# D-10 option B: the codegen tiers on the /tmp copy, one GIL mode per call (melder_0, 2026-10-25).
# usage: d10_b_tiers.sh <copy dir> <gil 0|1> <label>
set -u
copy="${1:?copy}"; g="${2:?gil}"; label="${3:?label}"
runs="$HOME/mnt/melder_private/context_compass/artifacts/codegen_room_policy_20261025/runs"
cd "$copy"
unit=$(find tests/unit/melder/aether -maxdepth 1 \( -name "test_*codegen*.py" -o -name "test_frame_acl*.py" \) | sort | tr "\n" " ")
n=$(echo $unit | wc -w)
out="$runs/d10_${label}_tiers_gil$g.txt"
{ echo "command: python -X gil=$g -m pytest -p no:cacheprovider -q -rfEx <$n codegen/ACL unit files in tests/unit/melder/aether> tests/component/melder/aether tests/integration/melder/aether (cwd: $copy, a /tmp copy of the working tree; Python 3.14.7t)"
  echo "ran_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  TMPDIR=/tmp/m0s2/tmp PYTHONDONTWRITEBYTECODE=1 timeout 170 /tmp/m0_venv/bin/python -X gil=$g -m pytest -p no:cacheprovider -q -rfEx $unit tests/component/melder/aether tests/integration/melder/aether 2>&1 | sed "s#$HOME#~#g" | tail -14
  echo "exit: ${PIPESTATUS[0]}"; } > "$out"
tail -4 "$out" | cut -c1-200
