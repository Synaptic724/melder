#!/bin/bash
# usage: run_one.sh <name> <pytest paths...>   (foreground; GIL off; skip/xfail reasons with -rsxX)
cd "$HOME/mnt/melder_private" || exit 1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/cc_pycache TMPDIR=/tmp GIT_OPTIONAL_LOCKS=0
name="$1"; shift
log="/tmp/cc_final/$name.log"
echo "command: python -X gil=0 -m pytest -q -p no:cacheprovider -rsxX $*" > "$log"
echo "started: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$log"
"$HOME/v314t/bin/python" -X gil=0 -m pytest -q -p no:cacheprovider -rsxX --junitxml="/tmp/cc_final/$name.xml" "$@" >> "$log" 2>&1
echo "exit: $? finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$log"
tail -4 "$log" | cut -c1-220
