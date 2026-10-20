#!/usr/bin/env bash
# usage: [TREE=<dir>] run_part.sh <gil> <label>... ; runs each chunk of the full tree (TASK-2026-10-14-fix_many_child_follows_holder)
# on the working tree, or on the scratch copy TREE (a copy of the working tree's src, tests and support files under /tmp).
# Use a scratch copy for chunks that write into the tree: the connected folder refuses deletes, so tests that clean their
# own temp folders inside tests/ fail there and leave files behind.
# with a 170 s cap per chunk (the device shell allows 180 s per call); logs go to /tmp, one summary line per chunk to the artifact folder.
# PYTHONPYCACHEPREFIX keeps Python and pytest off the __pycache__ folders the owner's Windows runs left in the tree: their
# code objects carry C:\ paths, so source inspection in test_method_inspector.py fails on the VM (3 tests, unrelated).
g=$1; shift
OUT=/tmp/cc_res/many_child_probe/suites; mkdir -p $OUT
S=$HOME/mnt/melder_private/context_compass/artifacts/many_child_registration_20261014/runs/full_tree_summary_gil$g.txt
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
export TMPDIR=/tmp/cc_res/many_child_probe/tmp
mkdir -p $TMPDIR
TREE=${TREE:-$HOME/mnt/melder_private}
cd $TREE || exit 1
tag=$(basename $TREE)
for label in "$@"; do
  paths=${P[$label]:-$label}
  name=$(echo "$label" | tr '/' '_')
  start=$(date +%s)
  PYTHONPATH=src:. PYTHONPYCACHEPREFIX=/tmp/cc_res/many_child_probe/pycache PYTHONDONTWRITEBYTECODE=1 timeout 170 $HOME/v314t/bin/python -X gil=$g -W ignore::UserWarning -m pytest $paths -p no:cacheprovider -q -rfE > $OUT/${tag}_${name}__gil$g.log 2>&1
  rc=$?; secs=$(( $(date +%s) - start ))
  echo "$tag | $label | rc=$rc | secs=$secs | $(grep -E '[0-9]+ (passed|failed|error)' $OUT/${tag}_${name}__gil$g.log | tail -1)" >> $S
  echo "$tag | $label | rc=$rc | secs=$secs | $(grep -E '[0-9]+ (passed|failed|error)' $OUT/${tag}_${name}__gil$g.log | tail -1)"
done
