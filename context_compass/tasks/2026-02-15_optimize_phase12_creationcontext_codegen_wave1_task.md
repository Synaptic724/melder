# Task: Optimize Phase12 and CreationContext Codegen Wave 1

## Metadata
- Task ID: TASK-2026-02-15-optimize-phase12-creationcontext-codegen-wave1
- Story: STORY-2026-02-15-phase12-codegen-runtime-tightening
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Implement the first hotspot-led codegen runtime optimization patch for
Phase12/CreationContext and validate with targeted profiler suites.

## Scope Boundaries
- In scope:
- Hotpath edits in `phase12_no_overrides_executor.py`,
  `phase12_overrides_executor.py`, and `creation_context.py` only if required.
- Targeted reruns of fast-graph and override cprofile suites.
- Out of scope:
- Public API changes.
- Broad refactors outside measured hotspot callpaths.

## Steps / Checklist
- [ ] Confirm top hotspot helper targets from `.summary.txt` + call-chain artifacts.
- [ ] Apply minimal optimization patch on selected helper path(s).
- [ ] Re-run targeted cprofile pytest suites and compare key lanes.
- [ ] Record measured deltas and behavior observations.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Wave-1 runtime optimization code patch.
- Updated profiler artifacts for fast and overrides lanes.
- Notes entry documenting before/after observations.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py` (only if needed)
- `context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`

## Risks / Rollback Notes
- Risk: speed change in one lane regresses another lane.
  Rollback: keep patch isolated, then compare both suites before finalizing.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Wave-1 patch now prebinds registration metadata (`spell_id`, `has_disposal_methods`, `disposal_methods`) into generated step lanes and routes hot-path registration calls through `_register_spell_instance_prebound(...)` for both no-overrides and overrides executors.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:489-499, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:538-726, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1098-1167, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:379-398, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:657-1116
  IMPACT: Runtime registration no longer re-reads spell registration attributes on each helper invocation in generated lanes.
  NEXT: Run targeted profiler suites to verify behavior and measure lane-level impact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The no-overrides hotspot helper `_register_spell_instance` performs repeated per-call spell attribute extraction (`spell_id`, `has_disposal_methods`, `disposal_method_names`) while generated step source invokes this helper across many hotpath callsites in both no-overrides and overrides executors.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1038-1097, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:575-706, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:700-1062, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:10-20
  IMPACT: Replacing spell-attribute lookups with prebound step constants should reduce helper overhead on the hottest no-overrides lane and improve shared helper usage for overrides lanes.
  NEXT: Add a prebound registration helper and switch emitted no-overrides/overrides source to call it with per-step constants.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Timings-lane summaries identify runtime helper hotspots in Phase12 execution paths for both no-overrides and overrides lanes (`_construct_spell_instance*`, `_register_spell_instance`, and creation-context overrides dispatcher path).
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:6-29, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:5-29
  IMPACT: The first patch should target helper-call overhead in these runtime helpers instead of compile/build-once paths.
  NEXT: Inspect helper implementations and select the smallest high-frequency optimization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Wave-1 task is active and ready for code-level hotspot optimization and
targeted profiler validation.
