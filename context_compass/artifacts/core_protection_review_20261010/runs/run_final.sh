#!/bin/bash
# Final verification set for the core-protection review and scan_bind lanes (melder_1, 2026-10-10).
cd "$HOME/mnt/melder_private" || exit 1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/cc_pycache TMPDIR=/tmp GIT_OPTIONAL_LOCKS=0
PY="$HOME/v314t/bin/python"
run() {
  local name="$1"; shift
  echo "command: python -X gil=0 -m pytest -q -p no:cacheprovider -rsxX $*" > "/tmp/cc_final/$name.log"
  echo "started: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "/tmp/cc_final/$name.log"
  "$PY" -X gil=0 -m pytest -q -p no:cacheprovider -rsxX --junitxml="/tmp/cc_final/$name.xml" "$@" >> "/tmp/cc_final/$name.log" 2>&1
  echo "exit: $? finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "/tmp/cc_final/$name.log"
}
run v1_scan_focused \
  tests/unit/melder/spellbook/test_scan_bind.py \
  tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py \
  tests/component/melder/spellbook/test_bind_lifecycle_hooks.py \
  tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py \
  tests/unit/melder/spellbook/bind/test_bind.py \
  tests/unit/melder/spellbook/test_scan_bind_option_parity.py \
  tests/component/melder/spellbook/test_scan_bind_parity_component.py
run v2_review_suite \
  tests/unit/melder/crystallizer/crystal_analysis/test_custody_boundary_characterization.py \
  tests/unit/melder/spellbook/bind/test_internal_registration_identity.py \
  tests/integration/melder/crystallizer/test_recorded_leaf_source_read_integration.py \
  tests/integration/melder/mutation_research/test_research_lane_runtime_isolation_integration.py \
  tests/integration/melder/aether/test_codegen_core_boundary_integration.py
run v3_unit_tier tests/unit
run v4_component_spellbook tests/component/melder/spellbook
run v5_integration_spellbook tests/integration/melder/spellbook
run v6_integration_crystallizer tests/integration/melder/crystallizer
run v7_integration_mutation_research tests/integration/melder/mutation_research
run v8_integration_aether tests/integration/melder/aether
echo "ALL DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/cc_final/DONE
