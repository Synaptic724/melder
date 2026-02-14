# Task: Optimize Conjure Scheduler Lifecycle Reduction

## Metadata
- Task ID: TASK-2026-02-14-conjure-scheduler-lifecycle-reduction
- Story: STORY-2026-02-13-optimize-conjure-paths
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce per-conjure scheduler lifecycle overhead while preserving phase ordering,
error propagation, and cleanup contracts.

## Scope Boundaries
- In scope:
- `SpellbookCreationSystem` scheduler orchestration in conjure path.
- Structural vs resolution pass scheduling boundaries.
- Contract-preserving validation tests.
- Out of scope:
- Semantic changes to phase behavior.
- Meld runtime path changes.

## Steps / Checklist
- [x] Baseline current scheduler lifecycle count and costs on conjure path.
- [x] Design a lower-overhead scheduler orchestration that preserves contracts.
- [x] Implement minimal safe changes in `SpellbookCreationSystem`.
- [x] Validate via targeted conjure-path tests/profile hooks.

## Deliverables
- Reduced scheduler lifecycle overhead in conjure path.
- Tests proving preserved conjure phase semantics and failure behavior.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/utilities/synchronization/phase_scheduler.py` (if needed)
- `tests/unit/melder/spellbook/` (targeted updates as needed)
- `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md`

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py` -> `2 passed`.
- `python -m pytest -q tests/unit/melder/spellbook/spellbook/test_conjure_phase_invocation_counts.py` -> `3 passed`.
- Artifacts:
  - `context_compass/artifacts/2026-02-14_conjure_scheduler_lifecycle_single_run_fastpath_pytests.txt`
  - `context_compass/artifacts/2026-02-14_conjure_scheduler_lifecycle_phase_invocation_counts_pytests.txt`

## Risks / Rollback Notes
- Risk: phase-order or error-gating drift.
- Rollback: restore current multi-pass scheduler lifecycle path.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Targeted regression suites pass after single-lifecycle conduit-resolution fastpath implementation (`2 passed` focused lifecycle tests, `3 passed` conjure phase-invocation coverage).
  EVIDENCE: context_compass/artifacts/2026-02-14_conjure_scheduler_lifecycle_single_run_fastpath_pytests.txt:1-12, context_compass/artifacts/2026-02-14_conjure_scheduler_lifecycle_phase_invocation_counts_pytests.txt:1-12
  IMPACT: New scheduling path is validated for lifecycle-count and phase-routing invariants with no observed regression in covered conjure behavior.
  NEXT: Walk this task outcome with user for acceptance and closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Added focused conduit-resolution regression tests that assert one scheduler lifecycle per conduit run and preserved foundational-error gating (plan factories skipped and plan-phase keys omitted when foundational errors exist).
  EVIDENCE: tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:141-223, tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:226-308
  IMPACT: Scheduler-lifecycle reduction now has direct guardrails on the new orchestration contract.
  NEXT: Run targeted pytest and persist artifacts for ticket evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented conduit-resolution single-lifecycle scheduling in `run_resolution_phases_for_conduit` by registering 5-11 once and snapshotting the foundational error gate at plan boundary; plan keys are removed when the snapshot indicates foundational errors to preserve previous return-shape semantics.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:740-759, src/melder/spellbook/spellbook_creation_system.py:852-933
  IMPACT: Conjure conduit-resolution path now avoids one scheduler startup/cleanup cycle while maintaining phase-order and error-gating contracts.
  NEXT: Add focused unit tests for lifecycle count and foundational-error gating behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: PhaseScheduler worker loop was catching a custom `Empty` exception instead of the queue's `Empty` exception, allowing idle workers to terminate on sparse/long phases.
  EVIDENCE: src/melder/utilities/synchronization/phase_scheduler.py:5, src/melder/utilities/synchronization/phase_scheduler.py:399
  IMPACT: Multi-worker phase execution can collapse toward single-worker behavior after an early long sparse phase.
  NEXT: Keep scheduler lifecycle semantics unchanged and stabilize worker survival; then continue with lower-risk conjure overhead work.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Added a regression test that verifies worker threads remain alive before phase-2 after a long sparse phase.
  EVIDENCE: tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:185
  IMPACT: Prevents reintroduction of worker-loss behavior during scheduler maintenance.
  NEXT: Use this test as a guard while exploring further `UnitOfWork`/phase overhead improvements.

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Targeted scheduler unit suite passes after the exception-type fix and new regression test.
  EVIDENCE: tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:1
  IMPACT: Confirms fix correctness against current scheduler contracts.
  NEXT: Continue discovery for additional safe optimizations in this task scope.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Context / Handoff Summary
Single-lifecycle conduit-resolution scheduling is implemented and in review.
Conjure conduit runs now register phases 5-11 in one scheduler lifecycle while
preserving foundational-first gating semantics via a plan-boundary snapshot.
Focused regression tests and conjure phase-invocation coverage pass, and
artifacts are linked for handoff.
