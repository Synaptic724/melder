# Task: Implement JIT/AOT Regression Matrix and Compatibility Validation

- Completed: 2026-02-15
- Summary: Built and validated a focused AOT/JIT regression matrix across config defaults, conjure/bind propagation, transfer owned-only propagation, contracted-map exclusion, and runtime gate lifecycle.
- Summary: Added contracted-map exclusion transfer test and recorded targeted pytest evidence artifacts for compatibility review.

## Metadata
- Task ID: TASK-2026-02-15-implement-jit-aot-regression-matrix-and-compatibility
- Story: STORY-2026-02-15-jit-aot-regression-matrix-and-compatibility
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Build and execute regression coverage for AOT default and JIT opt-in propagation
and runtime lifecycle behavior.

## Scope Boundaries
- In scope:
- Test matrix creation and targeted test execution/reporting.
- Out of scope:
- Feature implementation beyond tests.

## Steps / Checklist
- [x] Build test matrix for AOT default and JIT opt-in across all propagation surfaces.
- [x] Add/extend tests for conjure, late bind, transfer owned-only, and runtime gate lifecycle.
- [x] Run targeted suites and record truthful validation status.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Regression matrix document in task notes.
- Targeted tests and validation results.

## Files / Paths Impacted
- `tests/unit/melder/spellbook/`
- `tests/unit/melder/aether/conduit/`
- `tests/unit/melder/aether/conduit/meld/`

## Validation
- Ran:
  - `python -m pytest tests/unit/melder/spellbook/test_spellbook.py -k "define_conduit_sets_resolution_required_when_jit_enabled or bind_after_conjure_sets_resolution_required_when_jit_enabled or bind_after_conjure_keeps_resolution_required_false_when_aot_enabled" -q`
  - `python -m pytest tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py -k "stamps_resolution_required_from_target_defaults or restores_source_resolution_required_default or transfer_flip_and_rollback_keep_contracted_maps_unchanged" -q`
  - `python -m pytest tests/unit/melder/aether/conduit/meld/test_meld.py -k "ensure_runtime_resolution_ready or meld_runs_deferred_runtime_resolution_before_context_build or meld_skips_context_build_when_deferred_runtime_resolution_fails" -q`
- Artifacts:
  - `context_compass/artifacts/2026-02-15_jit_aot_regression_matrix_targeted_pytests_summary.txt`

## Risks / Rollback Notes
- Risk: missing one propagation surface in the matrix.
- Mitigation: require explicit matrix rows for config, conjure, bind, transfer, and runtime gate.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Regression lane executes after implementation stories and validates both compatibility (AOT default) and new behavior (JIT opt-in propagation lifecycle).
  EVIDENCE: context_compass/stories/2026-02-15_jit_aot_config_flag_and_fluent_api_story.md:1-83, context_compass/stories/2026-02-15_jit_aot_conjure_propagation_story.md:1-82, context_compass/stories/2026-02-15_jit_aot_post_conjure_bind_propagation_story.md:1-79, context_compass/stories/2026-02-15_jit_aot_transfer_ownership_propagation_non_contracted_story.md:1-82, context_compass/stories/2026-02-15_jit_aot_runtime_resolution_gate_lifecycle_story.md:1-84
  IMPACT: Validation scope stays explicit and complete.
  NEXT: Begin once feature tasks are complete and linked tests are ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: All JIT/AOT implementation lanes are now in `review`, so regression matrix execution can proceed without waiting on additional feature code.
  EVIDENCE: context_compass/tasks/2026-02-15_implement_jit_aot_config_flag_and_fluent_api_task.md:6-6, context_compass/tasks/2026-02-15_implement_jit_aot_conjure_propagation_task.md:6-6, context_compass/tasks/2026-02-15_implement_jit_aot_post_conjure_bind_propagation_task.md:6-6, context_compass/tasks/2026-02-15_implement_jit_aot_transfer_ownership_propagation_non_contracted_task.md:6-6, context_compass/tasks/2026-02-15_implement_jit_aot_runtime_resolution_gate_lifecycle_task.md:6-6
  IMPACT: Regression work can focus on coverage completeness and validation evidence rather than waiting for in-flight implementation.
  NEXT: Build an explicit matrix mapping each required propagation surface to existing tests and identify any missing rows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: UNKNOWN
  CLAIM: Transfer propagation tests verify owned-lineage default stamping (`resolution_required`) on flip/rollback, but explicit contracted-map exclusion assertions are not yet evidenced in the same propagation slice.
  EVIDENCE: tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:566-566, tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2313-2342, tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2753-2776
  IMPACT: Regression matrix would leave the "contracted-spell exclusion" acceptance row partially implicit.
  NEXT: Add a transfer regression test that seeds contracted maps and asserts they remain unchanged across ownership flip propagation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Added explicit transfer regression coverage proving owned-lineage flip/rollback propagation does not mutate contracted spell maps.
  EVIDENCE: tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2779-2824
  IMPACT: Regression matrix now has direct evidence for the contracted-exclusion acceptance row.
  NEXT: Run targeted suites for spellbook propagation, transfer ownership propagation, and meld runtime gate lifecycle, then publish matrix + results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Regression matrix is now fully evidenced across config flag defaults, conjure/late-bind propagation, owned-transfer propagation + contracted exclusion, and runtime gate lifecycle.
  EVIDENCE: tests/unit/melder/spellbook/configuration/test_configuration.py:22-30, tests/unit/melder/spellbook/configuration/test_configuration.py:488-504, tests/unit/melder/spellbook/test_spellbook.py:1295-1350, tests/unit/melder/spellbook/test_spellbook.py:1353-1466, tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2313-2342, tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2753-2824, tests/unit/melder/aether/conduit/meld/test_meld.py:1695-1930
  IMPACT: Story acceptance criteria now map to explicit, high-signal unit tests for both AOT default compatibility and JIT opt-in behavior.
  NEXT: Execute the targeted matrix suites and record truthfully in task validation artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Targeted matrix suites pass for spellbook propagation (3), transfer propagation/exclusion (3), and runtime gate lifecycle (7).
  EVIDENCE: context_compass/artifacts/2026-02-15_jit_aot_regression_matrix_targeted_pytests_summary.txt:1-12
  IMPACT: Regression matrix lane is implementation-complete and ready for acceptance review.
  NEXT: Sync attention board status to review and ask user to confirm acceptance criteria for closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

### Regression Matrix
| Surface | AOT Default Coverage | JIT Opt-In Coverage | Contracted Exclusion Coverage | Evidence |
|---|---|---|---|---|
| Config flag + fluent API | `full_ahead_of_time_compilation=True` default | `with_full_ahead_of_time_compilation(False)` | n/a | `tests/unit/melder/spellbook/configuration/test_configuration.py:22-30`, `tests/unit/melder/spellbook/configuration/test_configuration.py:488-504` |
| Conjure propagation | `resolution_required=False` on default lane | `resolution_required=True` when JIT enabled | n/a | `tests/unit/melder/spellbook/test_spellbook.py:1295-1350` |
| Post-conjure bind propagation | Keeps `resolution_required=False` when AOT enabled | Sets `resolution_required=True` when JIT enabled | n/a | `tests/unit/melder/spellbook/test_spellbook.py:1353-1466` |
| Transfer propagation (owned lineages) | Rollback restores source default | Flip stamps target default | Contracted maps unchanged through flip+rollback | `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2313-2342`, `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2753-2824` |
| Runtime resolution gate lifecycle | Fast-path no-op when not required | Deferred run/set/clear/fail-fast and pre-context ordering | n/a | `tests/unit/melder/aether/conduit/meld/test_meld.py:1695-1930` |

## Context / Handoff Summary
Review-ready: matrix rows are documented with evidence, targeted suites pass, and contracted-exclusion coverage is explicit in transfer tests.
