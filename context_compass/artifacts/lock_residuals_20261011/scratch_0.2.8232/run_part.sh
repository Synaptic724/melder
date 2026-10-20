#!/usr/bin/env bash
# usage: run_part.sh <tree> <gil> <label>... ; chunks as in the 0.2.8231 full-tree run; appends to the summary.
t=$1; g=$2; shift 2; OUT=/tmp/cc_res/suites; mkdir -p $OUT; S=$OUT/summary_${t}_gil$g.txt
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
cd /tmp/cc_res/$t || exit 1
for label in "$@"; do
  start=$(date +%s)
  PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 timeout 170 $HOME/v314t/bin/python -X gil=$g -W ignore::UserWarning -m pytest ${P[$label]} -p no:cacheprovider -q -rfE > $OUT/${label}__${t}_gil$g.log 2>&1
  rc=$?; secs=$(( $(date +%s) - start ))
  echo "$t | $label | rc=$rc | secs=$secs | $(grep -E '[0-9]+ (passed|failed|error)' $OUT/${label}__${t}_gil$g.log | tail -1)" >> $S
done
