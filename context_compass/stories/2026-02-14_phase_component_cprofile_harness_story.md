# Story: Phase Component CProfile Harness

## Metadata
- Story ID: STORY-2026-02-14-phase-component-cprofile-harness
- Epic: EPIC-2026-02-14-phase-testing
- Status: ready
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
- [ ] Task: TASK-2026-02-14-discovery-phase-component-cprofile-harness - Define direct-call harness contract, fixture strategy, and toggle matrix.

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
  CLAIM: Spell facade methods allow direct phase invocation without the scheduler.
  EVIDENCE: src/melder/spellbook/spell.py:1270, src/melder/spellbook/spell.py:1011, src/melder/spellbook/spell.py:1160
  IMPACT: Confirms component profiling can isolate phase logic directly.
  NEXT: Specify direct-call sequence design in discovery task.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story prepared for discovery-first harness design. Next step is to define exact
direct-call sequencing and toggle schema before implementation.
