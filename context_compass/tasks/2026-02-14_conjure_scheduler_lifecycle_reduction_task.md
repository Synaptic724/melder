# Task: Optimize Conjure Scheduler Lifecycle Reduction

## Metadata
- Task ID: TASK-2026-02-14-conjure-scheduler-lifecycle-reduction
- Story: STORY-2026-02-13-optimize-conjure-paths
- Status: in_progress
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
- [ ] Baseline current scheduler lifecycle count and costs on conjure path.
- [ ] Design a lower-overhead scheduler orchestration that preserves contracts.
- [ ] Implement minimal safe changes in `SpellbookCreationSystem`.
- [ ] Validate via targeted conjure-path tests/profile hooks.

## Deliverables
- Reduced scheduler lifecycle overhead in conjure path.
- Tests proving preserved conjure phase semantics and failure behavior.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/utilities/synchronization/phase_scheduler.py` (if needed)
- `tests/unit/melder/spellbook/` (targeted updates as needed)
- `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md`

## Validation
- `python -m pytest -q tests/unit/melder/utilities/synchronization/test_phase_scheduler.py` -> `10 passed`.

## Risks / Rollback Notes
- Risk: phase-order or error-gating drift.
- Rollback: restore current multi-pass scheduler lifecycle path.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
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
Task created from conjure discovery hotspot #1.
Next step is to quantify exact scheduler lifecycle overhead and choose the
smallest safe reduction strategy.
