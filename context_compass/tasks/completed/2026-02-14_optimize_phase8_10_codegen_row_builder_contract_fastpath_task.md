Completed: 2026-02-14
Summary: Removed defensive attribute probing in phase8-10 row builders,
enforced contract-fast fail behavior, and validated with focused unit tests plus
two component harness reruns.

# Task: Optimize Phase8-10 Codegen Row Builders Contract Fastpath

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase8-10-codegen-row-builders-contract-fastpath
- Story: STORY-2026-02-13-optimize-spellcrafter-phases
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce phase8-10 IR row-builder overhead by replacing defensive probing with
contract-strict access on known spell-crafter artifact types.

## Scope Boundaries
- In scope:
- `_build_injection_instance_rows`, `_build_override_target_rows`,
  `_build_mutation_target_rows` fastpath cleanup.
- Contract-backed fail-fast behavior for invalid cleaned/malformed artifacts.
- Out of scope:
- Changing Phase8/9/10 artifact schemas.
- Runtime behavior outside codegen export row building.

## Steps / Checklist
- [x] Confirm and document contract guarantees for injection and patch-map artifact types.
- [x] Replace hot-path defensive `try/except AttributeError` probes with direct access where contract-backed.
- [x] Keep deterministic sorting and payload schema unchanged.
- [x] Add/adjust tests to prove behavior and error semantics remain correct.
- [x] Validate with focused unit tests and component harness cProfile.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Contract-strict row builders with lower warm-path overhead.
- Evidence-backed validation for unchanged schema outputs.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/injection_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "phase8 or phase9 or phase10 or phase11 or injection_instance_rows or override_target_rows or mutation_target_rows"` -> `9 passed, 142 deselected`
  - `context_compass/artifacts/2026-02-14_phase8_10_contract_fastpath_unit_tests.txt`
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed, 3 warnings` (run1)
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output.txt`
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed, 3 warnings` (run2)
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output_run2.txt`

## Risks / Rollback Notes
- Risk: tighter contract enforcement could expose latent invalid-state paths.
- Rollback: restore previous defensive probe behavior while documenting failing contracts.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User accepted rank-3 outcome (mixed warm wall-time with improved profile shape) and directed continuation.
  EVIDENCE: user instruction in session (2026-02-14): "ok thats fine continue accepted"
  IMPACT: Task is approved for completion move; next execution should route to the next phase-discovery ticket.
  NEXT: Move this task to `tasks/completed/` and update story/board links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-3 row-builder contract-fastpath validation completed across two harness reruns; warm `group_8_11_total_ms` measured `11.047` then `10.266` with warm cProfile sample stable at `0.034s`/`122060` calls, while pre-rank3 rank-2 warm baselines were `10.552` and `10.833` at `0.036s`/`123618` calls.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output_run2.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run6.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-38
  IMPACT: Phase8-10 contract-fastpath is validated with unchanged behavior and a slightly improved warm-profile shape (lower call volume and cProfile sample), with expected run-to-run wall-time variance.
  NEXT: Present rank-3 evidence to user for keep-vs-iterate and acceptance direction; if accepted, move this task to completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented contract-fastpath row builders by removing probe-based attribute handling in `_build_injection_instance_rows`, `_build_override_target_rows`, and `_build_mutation_target_rows`; malformed artifacts now fail fast via direct contract access, and tests were added for these fail-fast paths.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1414-1595, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4469-4739
  IMPACT: Hot-path export avoids defensive branch overhead while making invalid artifact leaks explicit instead of silently tolerated.
  NEXT: Run focused SpellCrafter phase8-10/phase11 signature unit coverage and component harness to confirm no schema regression and measure warm-path impact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current Phase8-10 row builders still tolerate malformed artifacts with many `try/except AttributeError` probes, while upstream artifacts expose strict contracts (`InjectionPlan.instance_injections -> InjectionSpec`, `OverridePatchMap._targets_by_spec/_specificity_by_spec`, `MutationPatchMap._targets_by_spec`).
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1414-1652, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:128-239, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:321-427, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:75-151, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:253-324
  IMPACT: We can remove defensive probes from hot paths and enforce fail-fast semantics when malformed/cleaned artifacts leak into export.
  NEXT: Replace probe-based access with direct attribute reads and add explicit tests that malformed artifact rows now fail fast.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current row builders spend hot-path time in methods that still use defensive attribute probing, while upstream builders construct contract-defined `InjectionPlan`/`InjectionSpec` and `OverridePatchMap` artifacts.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:23-23, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:43-43, src/melder/spellbook/spell_crafter/spell_crafter.py:1419-1478, src/melder/spellbook/spell_crafter/spell_crafter.py:1523-1562, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:321-427, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:516-655, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:75-151, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:660-696
  IMPACT: Contract-fastpath cleanup is a practical third-ranked optimization with correctness hardening benefits.
  NEXT: Verify cleaned-state call contracts and define explicit fail-fast points before edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation and validation are complete for rank-3 row-builder contract
fastpath. Two harness reruns and focused unit tests are captured in artifacts;
warm wall time is mixed but profile shape improved versus pre-rank3 baseline.
Next step is user keep-vs-iterate/acceptance direction, then close or iterate.
