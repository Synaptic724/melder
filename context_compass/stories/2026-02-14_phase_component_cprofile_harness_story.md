# Story: Phase Component CProfile Harness

## Metadata
- Story ID: STORY-2026-02-14-phase-component-cprofile-harness
- Epic: EPIC-2026-02-14-phase-testing
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want a direct-call phase component harness, so that
we can profile phase logic without scheduler/worker overhead noise.

## Value / MRP Alignment
This story creates the profiling foundation for trustworthy phase optimization.
Without this harness, phase-level timing is mixed with orchestration overhead.

## Requirements (Functional)
- Provide a component test harness that invokes phase methods directly.
- Add explicit boolean toggles to run selected phase groups/chains.
- Print profile/timing output per enabled group.

## Requirements (Non-Functional)
- Must avoid `PhaseScheduler`, worker threads, and `UnitOfWork`.
- Must be deterministic and compatible with `cProfile`.
- Must keep phase-order contracts explicit in code/comments.

## Scope Boundaries
- In scope:
- Component profiling harness code and supporting component tests.
- Chain toggles for grouped execution paths.
- Out of scope:
- Runtime production path replacement.
- Integration-style conjure orchestration benchmarking.

## Dependencies / Related Work
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spellbook_creation_system.py`
- `EPIC-2026-02-14-phase-testing`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-14-discovery-phase-component-cprofile-harness - Define direct-call harness contract, fixture strategy, and toggle matrix.
- [x] Task: TASK-2026-02-14-implement-phase-component-cprofile-harness - Implement component harness module and profile output contract.

## Acceptance Criteria
- Harness contract is documented and approved with explicit no-scheduler constraint.
- Toggle matrix includes at least 1-4, 5-7 conduit-wide, and 5-7 local tracks.

## Validation / Test Plan
- Validate via component test skeleton and source-backed call-path mapping.
- Record command and output once implementation begins.

## UX / API / Data Notes
- Internal testing utility only; no public API changes.

## Risks / Mitigations
- Risk: accidental scheduler usage in harness implementation.
  Mitigation: add explicit assertions/guards and code-review checklist.

## Open Questions
- Which default fixture depth should be the primary profile baseline?

## Decision Log
- 2026-02-14: Story created from EPIC-2026-02-14-phase-testing.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Harness implementation executed successfully and emitted standardized profile output for all four groups.
  EVIDENCE: context_compass/tasks/2026-02-14_implement_phase_component_cprofile_harness_task.md:3-3, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-13
  IMPACT: Story has implementation evidence and can support downstream baseline measurement/ranking tasks.
  NEXT: Confirm acceptance for the implementation task and close this story when directed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Discovery locked the harness contract to four direct-call groups (`1-4`, `5-7 conduit`, `5-7 local`, `8-11 conduit`) with no scheduler path and production-order gating.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_component_cprofile_harness_task.md:34, src/melder/spellbook/spellbook_creation_system.py:748, src/melder/spellbook/spellbook_creation_system.py:753
  IMPACT: Harness implementation can proceed with explicit scope and deterministic execution geometry.
  NEXT: Move discovery task to review and ask for acceptance before implementing harness code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Spell facade methods allow direct phase invocation without the scheduler.
  EVIDENCE: src/melder/spellbook/spell.py:1270, src/melder/spellbook/spell.py:1011, src/melder/spellbook/spell.py:1160
  IMPACT: Confirms component profiling can isolate phase logic directly.
  NEXT: Specify direct-call sequence design in discovery task.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Discovery phase is complete for harness contract design. Next action is user
acceptance on the discovery task, then implementation of the component harness
under this story.
