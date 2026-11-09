#!/usr/bin/env bash
# Runner (melder_0, 2026-11-07; STORY-2026-10-25-map_dependency_watchers_and_announcers): every cell of
# probe_watcher_announcer_matrix.py, the GIL off then on, one process per cell, run in parallel from a temporary
# working directory (no cache files land in the repository) and collated in cell order into
# runs/probe_watcher_announcer_matrix_<version>.txt beside this folder.
#
#   bash run_probe_watcher_announcer_matrix.sh [python] [jobs]
#
# python defaults to the repository's .venv_new interpreter (3.14 free-threaded build); jobs defaults to 12.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
PY="${1:-$REPO/.venv_new/Scripts/python.exe}"
JOBS="${2:-12}"
PROBE="$HERE/probe_watcher_announcer_matrix.py"
RUNS="$HERE/../runs"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

VERSION="$(cd "$WORK" && "$PY" -W ignore -c "import melder; print(melder.__version__)")"
OUT="$RUNS/probe_watcher_announcer_matrix_${VERSION//./_}.txt"
CELLS="$(cd "$WORK" && "$PY" -W ignore "$PROBE" --list)"
mkdir -p "$RUNS"

run_one() {
    local gil="$1" cell="$2"
    (cd "$WORK" && "$PY" -X "gil=$gil" -W ignore "$PROBE" "$cell" > "$WORK/out.$gil.$cell" 2>&1
     echo "[exit $?]" >> "$WORK/out.$gil.$cell")
}
export -f run_one
export PY PROBE WORK

for gil in 0 1; do for cell in $CELLS; do echo "$gil $cell"; done; done |
    xargs -P "$JOBS" -n 2 bash -c 'run_one "$0" "$1"'

{
    echo "probe_watcher_announcer_matrix.py on $VERSION, every cell, the GIL off then on (melder_0,"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ); STORY-2026-10-25-map_dependency_watchers_and_announcers); interpreter:"
    echo "$("$PY" -c 'import sys, sysconfig; print(sys.version.split()[0], "free-threaded build:", sysconfig.get_config_var("Py_GIL_DISABLED"))')."
    for gil in 0 1; do
        for cell in $CELLS; do
            echo "===== $cell (-X gil=$gil)"
            sed 's/\r$//' "$WORK/out.$gil.$cell"
            echo
        done
    done
} > "$OUT"
echo "$OUT"
