- Completed: 2026-01-20
- Summary: Delivered post-conjure bind/scan safety via structural phases, targeted revalidation, and change-control scaffolding.
- Summary: All story tasks and acceptance criteria are satisfied.

# Story: Support post-conjure binds with targeted revalidation

## Metadata
- Story ID: STORY-2026-01-18-melder-post-conjure-binding
- Epic: EPIC-2026-01-18-melder-post-conjure-revalidation
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-20

## User Narrative
As a maintainer, I want post-conjure bind/scan to remain safe and deterministic, so dynamic binding does not break validation or resolution behavior.

## Value / MRP Alignment
This ensures Melder remains reliable when bindings are added after conjure, without requiring full system reruns or manual cleanup of resolution state.

## Requirements (Functional)
- Persist frame-key metadata for sockets that resolve by frame or collection.
- Run Phases 1-4 for newly bound spells when a Spellbook is conjured.
- Mark affected spells dirty when a new binding appears for a referenced frame.
- Ensure Phase 5-7 execution fails fast on upstream phase errors.

## Requirements (Non-Functional)
- Preserve existing public APIs and docstring conventions.
- Maintain deterministic behavior under single-worker scheduler.

## Scope Boundaries
- In scope: spell topology metadata, bind/scan hooks, dirty propagation, scheduler behavior.
- Out of scope: new DI features, ACL changes, or existence policy revisions.

## Dependencies / Related Work
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/utilities/synchronization/phase_scheduler.py`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-18-melder-frame-dependency-metadata - Add frame-key metadata to topology.
- [x] Task: TASK-2026-01-18-melder-post-conjure-structural-phases - Run Phases 1-4 for new post-conjure bindings.
- [x] Task: TASK-2026-01-18-melder-binding-transaction-gating - Require binding transactions for bind/scan.
- [x] Task: TASK-2026-01-18-melder-targeted-revalidation - Mark affected spells dirty on new bindings.
- [x] Task: TASK-2026-01-18-melder-phase-scheduler-fail-fast - Fail fast on phase exceptions.
- [x] Task: TASK-2026-01-18-melder-change-control-transaction-investigation - Assess cross-conduit change coordination.
- [x] Task: TASK-2026-01-18-melder-system-coordination-mrp-research - Consolidate research and draft MRP plan.
- [x] Task: TASK-2026-01-18-melder-contract-binding-overlap-investigation - Analyze contract overlap collisions.
- [x] Task: TASK-2026-01-18-melder-agent-change-control-research - Compile agent usage flows and change-control impacts.
- [x] Task: TASK-2026-01-18-melder-change-control-transaction-request-model - Define transaction request model + begin_* APIs.
- [x] Task: TASK-2026-01-18-melder-change-control-transaction-manager - Implement change-control transaction manager facade.
- [x] Task: TASK-2026-01-18-melder-change-control-conflict-manager - Implement transaction conflict manager.
- [x] Task: TASK-2026-01-18-melder-change-control-embargo-manager - Implement embargo manager for scoped blocking.
- [x] Task: TASK-2026-01-18-melder-change-control-orchestrator - Implement staged change orchestrator.

## Acceptance Criteria
- Post-conjure bind/scan runs Phases 1-4 for new spells without global reruns.
- Frame/collection sockets can be identified and targeted for revalidation.
- New bindings trigger dirty propagation only for affected spells.
- Scheduler aborts quickly on exceptions without full timeout waits.

## Validation / Test Plan
- Integration tests for post-conjure bind/scan flows and targeted revalidation.
- Unit tests for topology metadata and scheduler error handling.

## UX / API / Data Notes
- No public API changes required; behavior is internal.

## Risks / Mitigations
- Risk: Overly broad dirty propagation. Mitigation: store precise frame/binding keys.
- Risk: Scheduler changes alter existing timing assumptions. Mitigation: add explicit fail-fast tests.

## Open Questions
- Should targeted revalidation include binding_name granularity or frame-only matching?

## Decision Log
- 2026-01-18: Treat frame-based sockets as revalidation triggers when new providers appear.

## Context / Handoff Summary
- All story tasks completed, including binding transaction gating, targeted
  revalidation, scheduler fail-fast behavior, and change-control scaffolding.
