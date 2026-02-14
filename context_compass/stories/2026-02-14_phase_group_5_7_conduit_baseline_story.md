# Story: Phase Group 5-7 Conduit Baseline

## Metadata
- Story ID: STORY-2026-02-14-phase-group-5-7-conduit-baseline
- Epic: EPIC-2026-02-14-phase-testing
- Status: review
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
- [x] Task: TASK-2026-02-14-discovery-phase-group-5-7-conduit-baseline - Define conduit-wide 5-7 direct-call baseline and fixture/ordering requirements.

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
  TYPE: MEASURE
  CLAIM: Conduit-wide 5-7 baseline now has measured cold/warm totals and phase-level timing breakdowns.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:7-8
  IMPACT: Story now provides evidence-backed foundational resolution baseline data for ranking.
  NEXT: Compare 5-7 conduit costs against local 5-7 costs in backlog ranking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Conduit-wide 5-7 discovery is complete with lead-spell direct-call contract, deterministic fixture policy, and ranking output schema including conduit error-state flagging.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md:34
  IMPACT: Story is ready for implementation after discovery acceptance.
  NEXT: Move discovery task to review and continue with local 5-7 discovery ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

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
Discovery for conduit-wide 5-7 baseline is documented in the linked task with
sequence, fixture, and output contracts. Next action is acceptance for task
closeout while continuing discovery on the next phase track.
