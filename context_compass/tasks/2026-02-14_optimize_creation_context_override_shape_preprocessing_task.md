# Task: Optimize CreationContext Override Shape Preprocessing

## Metadata
- Task ID: TASK-2026-02-14-optimize-creation-context-override-shape-preprocessing
- Story: STORY-2026-02-13-optimize-creation-context-codegen
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce per-call override-lane preprocessing in `CreationContext` by minimizing
duplicate override-map traversal before specialization-cache resolution.

## Scope Boundaries
- In scope:
- `_execute_with_overrides` shape-key build path.
- `_collect_override_socket_shape` and miss-path handoff to grouped targets.
- Deterministic ordering and shape-key contract preservation.
- Out of scope:
- Phase11/Phase12 schema changes.
- Changes to override semantic rules (existing-instance override rejection, etc.).

## Steps / Checklist
- [x] Confirm current shape-key and grouped-target contracts for cache key stability.
- [x] Implement preprocessing reduction that avoids duplicate map work on miss paths.
- [x] Preserve one/two-socket fast paths and deterministic ordering.
- [x] Add/adjust tests for cache-hit/miss behavior parity and shape-key stability.
- [x] Validate with focused unit tests plus component harness comparison.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Lower preprocessing overhead in override-bearing CreationContext calls.
- Evidence-backed confirmation that specialization cache behavior remains stable.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- `python -m pytest -q tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -k "override or shape or creation_context"` -> `14 passed, 3 warnings`
  - `context_compass/artifacts/2026-02-14_creation_context_override_shape_preprocessing_unit_tests.txt`
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed, 3 warnings` (run1)
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_shape_preprocessing_output.txt`
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed, 3 warnings` (run2)
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_shape_preprocessing_output_run2.txt`

## Risks / Rollback Notes
- Risk: shape-key drift could fragment specialization cache entries.
- Rollback: restore current dual-collector flow and preserve deterministic sorting.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-1 validation passed (`14` focused unit tests; two harness reruns passed), with warm `group_8_11_total_ms` at `10.704` and `10.934` versus prior spellcrafter anchor runs `11.047` and `10.266`; cProfile shape stayed stable (`122060` calls, `0.035s`, `_pickle.dumps=724`).
  EVIDENCE: context_compass/artifacts/2026-02-14_creation_context_override_shape_preprocessing_unit_tests.txt:12-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_shape_preprocessing_output.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_shape_preprocessing_output_run2.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output_run2.txt:7-38
  IMPACT: Change is behavior-safe with neutral-to-noisy wall-time movement and stable warm profile shape; ready for user keep-vs-iterate decision.
  NEXT: Sync story/board state and ask user acceptance for rank-1 closure or further iteration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented miss-path preprocessing reduction in `_execute_with_overrides` by deriving grouped override targets from precomputed `socket_shape` via `_collect_override_targets_from_socket_shape`, and added coverage for the new helper plus a guard that legacy grouped collector is not used in this execution path.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:587-602, src/melder/aether/conduit/meld/creation_context/creation_context.py:723-772, tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:208-226, tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:345-399
  IMPACT: Cache-hit behavior stays shape-only while cache-miss grouping now reuses shape order without the legacy grouped-helper call in this path.
  NEXT: Run focused CreationContext unit tests and component harness to confirm parity and measure impact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Test-path rename is applied: override/shape coverage now lives at `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`, and the old `meld_runtime` test folder has been removed.
  EVIDENCE: tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:1-120, context_compass/tasks/2026-02-14_optimize_creation_context_override_shape_preprocessing_task.md:38-47
  IMPACT: Active validation and ticket pointers align with current CreationContext naming.
  NEXT: Proceed with rank-1 preprocessing optimization in `creation_context.py` and validate against the renamed test module.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User directed that remaining `meld_runtime` naming should be renamed to `creation_context` because the runtime responsibility has moved.
  EVIDENCE: user instruction in session (2026-02-14): "meld runtime should be renamed too because we don't have that anymore most of those moved to creation context"
  IMPACT: Validation and ticket references for this task should use `creation_context` test paths, not `meld_runtime`.
  NEXT: Move the test module path and update references before running rank-1 implementation validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Canonical CreationContext override/shape tests for this change are in `creation_context/test_creation_context.py`, including `_execute_with_overrides` and shape/grouping assertions.
  EVIDENCE: tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:165-202, tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:273-462
  IMPACT: Validation path is resolved, so implementation can proceed with existing focused unit coverage.
  NEXT: Implement preprocessing reduction in `_execute_with_overrides` while preserving existing shape/grouped contract outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: The earlier test-path uncertainty is resolved; task validation now points to the existing `creation_context/test_creation_context.py` module.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_creation_context_override_shape_preprocessing_task.md:38-47
  IMPACT: No remaining validation-path blocker for this task.
  NEXT: Continue implementation and run focused unit/component validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current override calls compute `socket_shape` before cache lookup, and cache misses with non-empty overrides perform a second map walk to build grouped targets.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:570-589, src/melder/aether/conduit/meld/creation_context/creation_context.py:653-720, src/melder/aether/conduit/meld/creation_context/creation_context.py:722-839
  IMPACT: Preprocessing overhead is duplicated on miss paths and is a direct optimization target.
  NEXT: Start implementation with contract checks for shape-key parity and grouped-target ordering.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation and validation are complete for rank-1. Unit tests passed and
two harness reruns were captured; warm runtime movement is mixed/noisy while
profile shape remains stable. Next step is user keep-vs-iterate acceptance.

