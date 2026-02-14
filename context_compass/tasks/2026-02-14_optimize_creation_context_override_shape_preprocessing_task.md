# Task: Optimize CreationContext Override Shape Preprocessing

## Metadata
- Task ID: TASK-2026-02-14-optimize-creation-context-override-shape-preprocessing
- Story: STORY-2026-02-13-optimize-creation-context-codegen
- Status: in_progress
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
- [ ] Confirm current shape-key and grouped-target contracts for cache key stability.
- [ ] Implement preprocessing reduction that avoids duplicate map work on miss paths.
- [ ] Preserve one/two-socket fast paths and deterministic ordering.
- [ ] Add/adjust tests for cache-hit/miss behavior parity and shape-key stability.
- [ ] Validate with focused unit tests plus component harness comparison.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Lower preprocessing overhead in override-bearing CreationContext calls.
- Evidence-backed confirmation that specialization cache behavior remains stable.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -k "override or shape or creation_context"`
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Risks / Rollback Notes
- Risk: shape-key drift could fragment specialization cache entries.
- Rollback: restore current dual-collector flow and preserve deterministic sorting.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
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
  CLAIM: Canonical CreationContext override/shape tests for this change are in `meld_runtime/test_meld_runtime.py`, including `_execute_with_overrides` and shape/grouping assertions.
  EVIDENCE: tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:165-202, tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:273-462
  IMPACT: Validation path is resolved, so implementation can proceed with existing focused unit coverage.
  NEXT: Implement preprocessing reduction in `_execute_with_overrides` while preserving existing shape/grouped contract outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: UNKNOWN
  CLAIM: The task-declared CreationContext unit-test path may be stale and needs verification before validation runs.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_creation_context_override_shape_preprocessing_task.md:38-47
  IMPACT: Validation command planning is blocked until the canonical test path is confirmed.
  NEXT: Locate the actual CreationContext unit-test module path and update this task before implementation validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current override calls compute `socket_shape` before cache lookup, and cache misses with non-empty overrides perform a second map walk to build grouped targets.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:570-589, src/melder/aether/conduit/meld/creation_context/creation_context.py:653-720, src/melder/aether/conduit/meld/creation_context/creation_context.py:722-839
  IMPACT: Preprocessing overhead is duplicated on miss paths and is a direct optimization target.
  NEXT: Start implementation with contract checks for shape-key parity and grouped-target ordering.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task is active and currently confirming validation paths before implementation.
Primary objective remains reducing duplicate override preprocessing on miss paths
without changing shape-key or specialization-cache behavior.

