# Story: Phase Group 5-7 Local Baseline

## Metadata
- Story ID: STORY-2026-02-14-phase-group-5-7-local-baseline
- Epic: EPIC-2026-02-14-phase-testing
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want a target-local 5-7 component baseline, so that
we can measure single-spell revalidation costs independently from conduit-wide flow.

## Value / MRP Alignment
Local 5-7 revalidation is a distinct operational mode and should be profiled as
its own bounded track before optimization decisions.

## Requirements (Functional)
- Profile local root_blueprints/system_validation/change_control sequence.
- Keep target-spell scope explicit in harness fixture setup.
- Emit per-phase and grouped profile output.

## Requirements (Non-Functional)
- No scheduler/worker/unit-of-work on measured path.
- Maintain deterministic local-scope baseline behavior.

## Scope Boundaries
- In scope:
- Target-local 5, 6, 7 direct-call profiling track.
- Local scope fixture selection and explicit target spell routing.
- Out of scope:
- Conduit-wide 5-7 behavior.
- Phase 8+ local plan phases.

## Dependencies / Related Work
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/spellbook/spell.py`
- `EPIC-2026-02-14-phase-testing`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-14-discovery-phase-group-5-7-local-baseline - Define target-local 5-7 direct-call baseline and target-scope setup.

## Acceptance Criteria
- Local 5-7 baseline path is documented and approved.
- Output allows separate analysis vs conduit-wide 5-7.

## Validation / Test Plan
- Validate by mapping to source-backed local 5-7 call flow.

## UX / API / Data Notes
- Internal component profiling only.

## Risks / Mitigations
- Risk: conflating local and conduit-wide semantics.
  Mitigation: explicit separate track and fixture setup for local-only path.

## Open Questions
- Which target spell shape should be canonical for local 5-7 baseline?

## Decision Log
- 2026-02-14: Story created from EPIC-2026-02-14-phase-testing.

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Local 5-7 baseline now has measured totals, per-phase timings, and scoped-size metrics.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:9-9
  IMPACT: Story now supports local-vs-conduit foundational cost comparisons with real data.
  NEXT: Apply scoped-size context while ranking local 5-7 optimization leads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Local 5-7 discovery is complete with explicit target-scoped direct-call chain, deterministic target policy, and scoped-size output reporting.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md:34
  IMPACT: Story can proceed to implementation once discovery acceptance is confirmed.
  NEXT: Move local 5-7 discovery task to review and continue with 8-11 discovery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Target-local 5-7 phases are registered as single local-scope phases in current orchestration.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1206, src/melder/spellbook/spellbook_creation_system.py:1231, src/melder/spellbook/spellbook_creation_system.py:1245
  IMPACT: Local 5-7 is a distinct, bounded profiling target and should be measured separately.
  NEXT: Define direct-call local sequence and fixture in discovery task.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Discovery for local 5-7 baseline is documented in the linked task with target
policy, scoped-work semantics, and output contracts. Next action is acceptance
for task closeout while discovery proceeds to 8-11.
