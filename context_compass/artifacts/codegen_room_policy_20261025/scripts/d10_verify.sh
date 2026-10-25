#!/usr/bin/env bash
# Rerun the D-10 verification tiers on a fresh /tmp copy of the checkout (melder_0, 2026-10-25).
# usage: d10_verify.sh <label>   (writes runs/d10_<label>_tiers_gil0.txt and _gil1.txt)
set -u
label="${1:?label}"
repo="$HOME/mnt/melder_private"; copy=/tmp/m0_mq/d10_$label
runs="$repo/context_compass/artifacts/codegen_room_policy_20261025/runs"
rm -rf "$copy"; mkdir -p "$copy"
rsync -a --exclude __pycache__ --exclude __melder_cache__ --exclude "*.pyc" "$repo/src" "$repo/tests" "$repo/pyproject.toml" "$copy/"
. ~/.melder_env; export TMPDIR=/tmp/m0_mq/tmp PYTHONDONTWRITEBYTECODE=1; cd "$copy"
unit=$(find tests/unit/melder/aether -maxdepth 1 \( -name "test_*codegen*.py" -o -name "test_frame_acl*.py" \) | sort | tr "\n" " ")
for g in 0 1; do out="$runs/d10_${label}_tiers_gil$g.txt"
  { echo "command: python -X gil=$g -m pytest -p no:cacheprovider -q -rfEx <codegen/ACL unit files> tests/integration/melder/aether (cwd: $copy)"; echo "ran_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)";
    timeout 170 $HOME/.venv314t/bin/python -X gil=$g -m pytest -p no:cacheprovider -q -rfEx $unit tests/integration/melder/aether 2>&1 | sed "s#$HOME#~#g" | tail -40; echo "exit: ${PIPESTATUS[0]}"; } > "$out"
  tail -2 "$out"; done
