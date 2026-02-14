# Story: Phase Group 1-4 Baseline

## Metadata
- Story ID: STORY-2026-02-14-phase-group-1-4-baseline
- Epic: EPIC-2026-02-14-phase-testing
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want a phase 1-4 component baseline, so that
structural-phase hotspots are measured without scheduler overhead.

## Value / MRP Alignment
Phase 1-4 defines the structural compilation spine. Isolating its cost gives us
high-fidelity optimization direction for conjure preparation.

## Requirements (Functional)
- Profile phases 1-4 using direct phase calls only.
- Support grouped chain toggle for full 1-4 execution.
- Emit per-phase and grouped totals in test output.

## Requirements (Non-Functional)
- Single-threaded profile path.
- Reproducible command flow and output format.

## Scope Boundaries
- In scope:
- Phase 1, 2, 3, 4 component profiling.
- Baseline fixture selection and output normalization.
- Out of scope:
- Phases 5+ and runtime execution-plan paths.

## Dependencies / Related Work
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `EPIC-2026-02-14-phase-testing`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-14-discovery-phase-group-1-4-baseline - Define 1-4 direct-call profile sequence and baseline fixture constraints.

## Acceptance Criteria
- 1-4 grouped component profile path is documented and approved.
- Output format captures enough detail to rank 1-4 hotspots.

## Validation / Test Plan
- Validate through component-test discovery artifacts and source-backed mapping.

## UX / API / Data Notes
- Internal test/profiling only.

## Risks / Mitigations
- Risk: mismatch vs structural phase ordering in production.
  Mitigation: pin to `Spell.run_structural_phases` equivalent ordering.

## Open Questions
- Should the default baseline run one spell lineage or full spellbook set?

## Decision Log
- 2026-02-14: Story created from EPIC-2026-02-14-phase-testing.

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: 1-4 baseline now has measured cold/warm totals and per-phase timings from the component harness run.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-6
  IMPACT: Story now contains ranking-ready structural baseline data.
  NEXT: Use measured 1-4 deltas during optimization backlog ranking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: 1-4 discovery contract is complete: default full-spellbook baseline, optional single-spell diagnostic slice, and explicit warm/cold variants with per-phase output fields.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_group_1_4_baseline_task.md:34
  IMPACT: Story is unblocked for implementation once discovery acceptance is confirmed.
  NEXT: Move discovery task to review and request acceptance before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `Spell.run_structural_phases` provides canonical direct order for phases 1-4.
  EVIDENCE: src/melder/spellbook/spell.py:1270, src/melder/spellbook/spell.py:1294
  IMPACT: Gives a production-aligned direct-call sequence for component profiling.
  NEXT: Capture this sequence in discovery task harness contract.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Discovery for 1-4 baseline is documented in the linked task with sequence,
scope policy, warm/cold variants, and output fields. Next action is acceptance
of the discovery task, then harness implementation or move to 5-7 discovery.
