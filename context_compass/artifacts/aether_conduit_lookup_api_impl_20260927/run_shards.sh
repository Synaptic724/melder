#!/bin/bash
# usage: run_shards.sh <tree> <label> <python> <gil 0|1|-> <outfile> <path-group> [<path-group> ...]
# Each path-group is one pytest invocation (space-separated paths inside one argument).
tree="$1"; label="$2"; py="$3"; gil="$4"; out="$5"; shift 5
cd "$tree" || exit 2
export PYTHONDONTWRITEBYTECODE=1
for group in "$@"; do
  start=$(date +%s)
  if [ "$gil" = "-" ]; then
    res=$(timeout 175 "$py" -m pytest -q -p no:cacheprovider -rfE $group 2>&1)
  else
    res=$(PYTHON_GIL=$gil timeout 175 "$py" -m pytest -q -p no:cacheprovider -rfE $group 2>&1)
  fi
  rc=$?
  end=$(date +%s)
  summary=$(printf '%s\n' "$res" | grep -E "^(=+ )?[0-9]+ (passed|failed|error)|no tests ran|passed|failed" | tail -1)
  echo "$label gil=$gil $group :: rc=$rc :: $summary ($((end-start))s)" | tee -a "$out"
  if [ $rc -ne 0 ]; then
    printf '%s\n' "$res" | grep -E "^(FAILED|ERROR) " | head -40 | sed "s/^/  $label: /" | tee -a "$out"
  fi
done
echo "$label DONE $(date -u +%H:%M:%SZ)" | tee -a "$out"
