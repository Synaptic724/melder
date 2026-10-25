#!/bin/bash
# GAP-1 measurement (melder_1): fresh checkpoints evicted by retention when a profile folder holds earlier worlds'
# checkpoints with higher checkpoint numbers. Read-only on the repository: works on a /tmp copy of src and UX.
set -u
REPO=$HOME/mnt/melder_private
M=/tmp/cc_res/gap1mirror
PY=$HOME/v314t/bin/python
export TMPDIR=/tmp/cc_res/tmp
mkdir -p "$M" "$TMPDIR"
rsync -a --delete --exclude '__pycache__' --exclude '__melder_cache__' --exclude '*.meldercache' "$REPO/src/" "$M/src/"
rsync -a --delete --exclude '__pycache__' --exclude '__melder_cache__' --exclude '*.meldercache' \
  "$REPO/UX_and_AIX_experiences/" "$M/UX_and_AIX_experiences/"
CACHE=src/melder/__melder_cache__/__crystallizer_cache__
census() {
  "$PY" - "$1" <<'PYEOF'
import collections, json, pathlib, sys
nums, vers = collections.Counter(), collections.Counter()
for p in pathlib.Path(sys.argv[1]).glob("*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    nums[d.get("checkpoint_number")] += 1
    vers[d.get("record_version")] += 1
print("  files:", sum(nums.values()), "| checkpoint_number:", dict(sorted(nums.items())), "| record_version:", dict(sorted(vers.items())))
PYEOF
}
run4() {
  (cd "$M" && PYTHONPATH="$M/src" timeout 100 "$PY" -X gil=0 -m pytest -q -p no:cacheprovider \
    UX_and_AIX_experiences/pytest_examples/test_expert_examples.py \
    -k "02_persistence or 09_getting or 24_loading or 27_a_world" --tb=line 2>&1 | grep -E "Error|passed|failed" | sed "s#$HOME#~#g")
}
echo "# GAP-1: checkpoint retention against a profile folder of earlier worlds; melder version $(sed -n 's/^__version__ = "\(.*\)"$/\1/p' "$REPO/src/melder/__version__.py")"
echo "# run at $(date -u +%Y-%m-%dT%H:%M:%SZ) by melder_1 on a /tmp copy (src + UX_and_AIX_experiences), the GIL off"
echo
echo "== the device tree's own folder, src/melder/__melder_cache__/__crystallizer_cache__/default (read only)"
census "$REPO/$CACHE/default"
echo
echo "== A: the copy without a crystallizer cache folder - expert examples 02, 09, 24, 27"
rm -rf "$M/$CACHE"
run4
census "$M/$CACHE/default"
echo
echo "== B: the copy with the device folder copied in - the same four examples"
rm -rf "$M/$CACHE"; mkdir -p "$M/src/melder/__melder_cache__"; cp -r "$REPO/$CACHE" "$M/$CACHE"
run4
census "$M/$CACHE/default"
echo
echo "== C: twenty runs of the four examples from an empty folder (their own checkpoints only)"
rm -rf "$M/$CACHE"
for i in $(seq 1 20); do r=$(run4 | tail -1); done
echo "  after 20 runs: $r"
census "$M/$CACHE/default"
r=$(run4 | tail -1); echo "  run 21, at the cap: $r"
census "$M/$CACHE/default"
