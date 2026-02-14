# Story: Phase Group 5-7 Conduit Baseline

## Metadata
- Story ID: STORY-2026-02-14-phase-group-5-7-conduit-baseline
- Epic: EPIC-2026-02-14-phase-testing
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want a conduit-wide 5-7 component baseline, so that
we can isolate foundational resolution costs used in conjure.

## Value / MRP Alignment
Conduit-wide 5-7 phases are foundational and frame-scoped in conjure. Measuring
them directly gives clean optimization signal without scheduler noise.

## Requirements (Functional)
- Profile root_blueprints/system_validation/change_control as a grouped 5-7 track.
- Mirror conduit-scoped calling semantics via `conduit_id`.
- Emit per-phase and grouped profile output.

## Requirements (Non-Functional)
- No `PhaseScheduler` execution on the measured path.
- Deterministic, reproducible single-thread profile runs.

## Scope Boundaries
- In scope:
- Conduit-wide 5, 6, 7 direct-call profiling.
- Lead-spell frame-scoped invocation semantics.
- Out of scope:
- Target-local 5-7 path.
- Phase 8+ plan compilation.

## Dependencies / Related Work
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/spellbook/spell.py`
- `EPIC-2026-02-14-phase-testing`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-14-discovery-phase-group-5-7-conduit-baseline - Define conduit-wide 5-7 direct-call baseline and fixture/ordering requirements.

## Acceptance Criteria
- Conduit-wide 5-7 baseline path and ordering are documented and approved.
- Output format supports hotspot ranking across 5, 6, 7.

## Validation / Test Plan
- Validate against source-backed conduit-wide 5-7 flow mapping.

## UX / API / Data Notes
- Internal profiling/test coverage only.

## Risks / Mitigations
- Risk: missing frame-scoped behavior when bypassing scheduler.
  Mitigation: explicitly model lead-spell frame-scoped semantics in harness design.

## Open Questions
- Should we profile full spellbook vs minimal frame fixture for 5-7 baseline?

## Decision Log
- 2026-02-14: Story created from EPIC-2026-02-14-phase-testing.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide 5-7 is run as foundational phases from SpellbookCreationSystem.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1063, src/melder/spellbook/spellbook_creation_system.py:1084
  IMPACT: Baseline should preserve this grouped foundational sequence.
  NEXT: Encode equivalent direct-call flow in discovery output.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story is ready with a discovery task to define and lock conduit-wide 5-7
component profiling behavior.
