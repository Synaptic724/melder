# Story: Phase Group 8-11 Baseline

## Metadata
- Story ID: STORY-2026-02-14-phase-group-8-11-baseline
- Epic: EPIC-2026-02-14-phase-testing
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want a phase 8-11 component baseline, so that
plan-compilation hotspots are measured without scheduler overhead.

## Value / MRP Alignment
Phases 8-11 feed execution-plan artifacts that heavily shape runtime cost.
Direct-call baseline profiling keeps optimization work evidence-first and safe.

## Requirements (Functional)
- Profile phases 8-11 using direct phase calls only.
- Support grouped chain toggle for full 8-11 execution.
- Emit per-phase and grouped profile output.

## Requirements (Non-Functional)
- Single-threaded profile path.
- Reproducible command flow and output format.
- Preserve phase order from current production orchestration.

## Scope Boundaries
- In scope:
- Phase 8 (`occurrence_plan`), 9 (`injection_plan`), 10 (`patch_maps`), and 11 (`execution_plan`) component profiling.
- Baseline fixture selection and output normalization.
- Out of scope:
- Local target 8-11 track.
- Runtime optimization implementation.

## Dependencies / Related Work
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/spellbook/spell.py`
- `EPIC-2026-02-14-phase-testing`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-14-discovery-phase-group-8-11-baseline - Define 8-11 direct-call profile sequence and baseline fixture constraints.

## Acceptance Criteria
- 8-11 grouped component profile path is documented and approved.
- Output format captures enough detail to rank 8-11 hotspots.

## Validation / Test Plan
- Validate through component-test discovery artifacts and source-backed mapping.

## UX / API / Data Notes
- Internal test/profiling only.

## Risks / Mitigations
- Risk: mismatch vs conduit plan-phase ordering in production.
  Mitigation: pin the baseline chain to
  `_run_conduit_plan_resolution_phases` registration order.

## Open Questions
- Should local target 8-11 profiling be a separate follow-up story?

## Decision Log
- 2026-02-14: Story created from EPIC-2026-02-14-phase-testing to complete
  all-phase discovery coverage.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit plan-phase registration is an explicit 8-11 chain (occurrence, injection, patch maps, execution plan).
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1111, src/melder/spellbook/spellbook_creation_system.py:1121, src/melder/spellbook/spell.py:1067, src/melder/spellbook/spell.py:1140
  IMPACT: 8-11 should be profiled as its own grouped baseline track.
  NEXT: Define fixture and grouped output schema in discovery task.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story is ready with one discovery task to lock direct-call baseline behavior for
phases 8-11 and define stable output for optimization follow-up.
