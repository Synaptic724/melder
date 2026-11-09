#!/usr/bin/env bash
# T1 (TASK-2026-11-07-inventory_class_resolution_of_framed_spells): run the whole suite on the current tree
# twice - class matching as shipped, then with T2's strict rule patched in at runtime by
# strict_class_match_plugin.py (no src edit) - and compare the two runs. Both runs redirect the default conjure
# cache to a temp root, so no bundle replays Phase 3-4 rows across runs.
# Usage: bash run_strict_class_match_suite.sh [gil] [workers]   (defaults: gil 0, 16 workers)
set -u
cd "$(dirname "$0")/../../../.." || exit 1
GIL="${1:-0}"
WORKERS="${2:-16}"
PROBES=context_compass/artifacts/dependency_watchers_20261107/probes
RUNS=context_compass/artifacts/dependency_watchers_20261107/runs
PY=.venv_new/Scripts/python.exe
VERSION=$("$PY" -c "import sys; sys.path.insert(0, 'src'); from melder.__version__ import __version__; print(__version__.replace('.', '_'))")
for MODE in 0 1; do
  NAME="suite_strict_class_match_${VERSION}_strict${MODE}_gil${GIL}"
  echo "=== $NAME start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  PYTHONPATH="$PROBES" MELDER_PROBE_STRICT="$MODE" "$PY" -X "gil=$GIL" -m pytest tests \
    -p strict_class_match_plugin -n "$WORKERS" -q --tb=line -rfE --timeout=600 \
    --junitxml="$RUNS/$NAME.xml" > "$RUNS/$NAME.txt" 2>&1
  echo "=== $NAME exit $? end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  tail -3 "$RUNS/$NAME.txt"
done
"$PY" "$PROBES/compare_strict_class_match_runs.py" \
  "$RUNS/suite_strict_class_match_${VERSION}_strict0_gil${GIL}.xml" \
  "$RUNS/suite_strict_class_match_${VERSION}_strict1_gil${GIL}.xml" \
  > "$RUNS/suite_strict_class_match_${VERSION}_diff_gil${GIL}.txt"
echo "=== diff written: $RUNS/suite_strict_class_match_${VERSION}_diff_gil${GIL}.txt"
head -3 "$RUNS/suite_strict_class_match_${VERSION}_diff_gil${GIL}.txt"
