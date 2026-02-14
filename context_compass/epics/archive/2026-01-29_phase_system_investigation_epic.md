# Epic: Make Phase System Produce Plans for All Spells (Investigation First)

## Metadata
- Epic ID: EPIC-2026-01-29-phase-system-investigation
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29
- Target Window: 2026-Q1
- Related Program/Initiative:

## Problem / Opportunity
Currently, Phase 5+ artifacts (occurrence/injection/patch/execution plans) are built only for structural roots, so non-root spells can lack Phase 11 execution plans and fail when meld requires a plan. This blocks meld for non-root spells even when they are valid targets.

## MRP Alignment (Most Reasonable Product)
Ensure the phase system is coherent and complete: every spell that can be melded should have deterministic phase artifacts without runtime planning duplication. This strengthens correctness and predictability, and provides a stable base for later optimizations.

## Goals (Outcomes)
- A documented, evidence-backed understanding of Phase 1-11 inputs/outputs.
- A clear resolution plan to make all spells executable with Phase 11 artifacts.
- Phase-system ownership of planning logic (no runtime planning duplication).

## Non-Goals (Explicit Exclusions)
- Implementing fixes before the investigation is complete.
- Performance tuning or optimization work.

## Scope Boundaries
- In scope:
  - Deep investigation of all phases and their artifacts.
  - Root selection semantics and their impact on artifacts.
  - Runtime/engine consumption of phase artifacts.
  - A plan to make every spell meldable via the phase system.
- Out of scope:
  - Code changes beyond investigation artifacts and tickets.

## Success Metrics
- Investigation artifacts cover Phases 1-11 with evidence-based findings.
- Clear decision on how to enable Phase 11 for all spells.

## Requirements (Functional + Non-Functional)
- Functional: Every spell that can be melded should have a Phase 11 execution plan available after conjure.
- Non-Functional: No runtime planning duplication in MeldRuntime/MeldEngine.

## Constraints / Assumptions
- Conjure time may increase to ensure all spells are planned.
- Root semantics may need adjustment or expansion.

## Dependencies / External References
- `context_compass/artifacts/README.md`

## Milestones (Track Progress)
- [x] Milestone 1: Complete phase-by-phase investigation (Phases 1-11)
- [ ] Milestone 2: Produce and review implementation plan

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-29-phase-system-investigation - Deep investigation and plan
- [ ] Story: STORY-2026-01-29-phase11-fast-path-implementation - Implement Phase 11 fast path for constructed spells
- [x] Story: STORY-2026-01-29-phase11-execution-plan-precompute - Precompute overrides/contracts/mutations in Phase 11

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-29-phase-system-investigation
- [ ] Task: Complete story STORY-2026-01-29-phase11-fast-path-implementation
- [x] Task: Complete story STORY-2026-01-29-phase11-execution-plan-precompute

## Acceptance Criteria (Epic Done)
- Investigation artifacts exist for Phases 1-11 with evidence.
- A recommended resolution plan is documented with risks and tradeoffs.
- User confirms readiness to implement.

## Risks / Mitigations
- Risk: Expanded planning increases conjure time.
  - Mitigation: Accept cost for correctness; optimize later.
- Risk: Changes ripple through validation and change-control.
  - Mitigation: Validate dependencies and update docs after implementation.

## Validation / Test Approach
- Not run (investigation only).

## Rollout / Adoption Plan
- Investigation -> review -> implementation plan -> code changes.

## Open Questions
- Should every spell be treated as a root for Phase 5+ artifacts, or should root selection change to include all spells while preserving dependency ordering?

## Decision Log
- None yet.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
- Phase investigation artifacts for Phases 1-11 are populated.
- Implementation plan is still required before code changes.
