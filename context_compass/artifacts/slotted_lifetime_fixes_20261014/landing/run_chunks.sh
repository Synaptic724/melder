#!/usr/bin/env bash
# usage: SUMMARY=<name> [TREE=<dir>] run_chunks.sh <gil> <label>...   (EPIC-2026-10-14-slotted_lifetime_ownership_fixes)
# Runs each chunk of the test tree on TREE (default: the scratch tree /tmp/cc_res/fixes/tree) with a 170 s cap per chunk
# (the device shell allows 180 s per call). Full logs go to /tmp/cc_res/fixes/suites; one summary line per chunk is
# appended to runs/<SUMMARY>_gil<g>.txt in this lane's artifact folder. PYTHONPYCACHEPREFIX keeps Python off the tree's
# __pycache__ folders (the owner's Windows runs left code objects with C:\ paths there).
g=$1; shift
A=$HOME/mnt/melder_private/context_compass/artifacts/slotted_lifetime_fixes_20261014/runs
OUT=/tmp/cc_res/fixes/suites; mkdir -p $OUT
S=$A/${SUMMARY:-full_tree_summary}_gil$g.txt
declare -A P=(
 [unit_arch]="tests/unit/architecture_and_design" [unit_gh]="tests/unit/github_workflows" [unit_llm]="tests/unit/llm_support"
 [unit_build]="tests/unit/melder/build_assets"
 [unit_top]="tests/unit/melder/test_annotation_integrity.py tests/unit/melder/test_melder_registration_guard.py tests/unit/melder/test_package_author_metadata.py tests/unit/melder/test_package_description_metadata.py tests/unit/melder/test_package_license_metadata.py tests/unit/melder/test_package_public_surface.py tests/unit/melder/test_package_version_metadata.py tests/unit/melder/test_system_document_view.py tests/unit/melder/test_system_documents.py"
 [unit_aether]="tests/unit/melder/aether" [unit_sb]="tests/unit/melder/spellbook" [unit_util]="tests/unit/melder/utilities"
 [unit_mr]="tests/unit/melder/mutation_research" [unit_cryst]="tests/unit/melder/crystallizer"
 [comp_aether]="tests/component/melder/aether" [comp_sb]="tests/component/melder/spellbook" [comp_util]="tests/component/melder/utilities"
 [comp_mr]="tests/component/melder/mutation_research" [comp_cryst]="tests/component/melder/crystallizer"
 [int_aether]="tests/integration/melder/aether" [int_conduit]="tests/integration/melder/conduit" [int_sb]="tests/integration/melder/spellbook"
 [int_mr]="tests/integration/melder/mutation_research" [int_cryst]="tests/integration/melder/crystallizer"
 [int_mt]="tests/integration/melder/multithreading" [int_live]="tests/integration/melder/live_sim" [exper]="tests/experimentation" )
export TMPDIR=/tmp/cc_res/tmp
mkdir -p $TMPDIR
TREE=${TREE:-/tmp/cc_res/fixes/tree}
cd $TREE || exit 1
tag=$(basename $TREE)
for label in "$@"; do
  paths=${P[$label]:-$label}
  name=$(echo "$label" | tr '/' '_')
  start=$(date +%s)
  PYTHONPATH=src:. PYTHONPYCACHEPREFIX=/tmp/cc_res/fixes/pycache PYTHONDONTWRITEBYTECODE=1 timeout 170 $HOME/v314t/bin/python -X gil=$g -W ignore::UserWarning -m pytest $paths -p no:cacheprovider -q -rfE > $OUT/${tag}_${name}__gil$g.log 2>&1
  rc=$?; secs=$(( $(date +%s) - start ))
  line="$tag | $label | rc=$rc | secs=$secs | $(grep -E '[0-9]+ (passed|failed|error)' $OUT/${tag}_${name}__gil$g.log | tail -1)"
  echo "$line" >> $S
  echo "$line"
done
