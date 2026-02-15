- Completed: 2026-01-20
- Summary: Epic milestones and story delivered for post-conjure revalidation.
- Summary: Targeted revalidation, binding gating, and scheduler fail-fast are complete.

# Epic: Post-conjure revalidation and frame-aware dependency tracking

## Metadata
- Epic ID: EPIC-2026-01-18-melder-post-conjure-revalidation
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-20
- Target Window: 2026-Q1
- Related Program/Initiative: Melder Core

## Problem / Opportunity
Post-conjure bind/scan can register spells that never ran Phases 1-4. When Phases 5-7 run, Phase 6 fails with missing Phase 4 validation and the scheduler times out. Frame- and collection-based DI sockets are snapshot-based (Phase 3), so new bindings do not update existing spell dependencies unless phases are rerun. There is no durable metadata linking a socket to its frame key, so the system cannot target revalidation when new frame members are added.

## MRP Alignment (Most Reasonable Product)
We need deterministic post-conjure behavior and reliable, targeted revalidation so the core DI graph remains correct without a full rerun. This strengthens the validation system and keeps Melder safe in dynamic binding scenarios.

## Goals (Outcomes)
- New bindings after conjure are structurally validated without full system reruns.
- Frame-based sockets can be targeted for revalidation when new providers appear.
- Phase 5-7 execution fails fast on upstream phase errors instead of timing out.
- Tests cover post-conjure bind/scan behavior and targeted revalidation.

## Non-Goals (Explicit Exclusions)
- New resolution modes or spell types.
- Changes to Existence policy or permissions.
- ACL or cross-conduit contract redesign.

## Scope Boundaries
- In scope: SpellLocalTopology metadata, SpellSystemStates dirty propagation, bind/scan hooks, phase scheduler behavior, integration tests.
- Out of scope: runtime execution engine changes and new DI semantics.

## Success Metrics
- Post-conjure binds do not trigger missing Phase 4 errors during Phase 5-7 runs.
- Targeted revalidation updates list/frame dependencies without full revalidation.
- Phase scheduler fails fast on exceptions or cancellation.

## Requirements (Functional + Non-Functional)
- Preserve existing docstring/comment standards.
- Maintain deterministic behavior under single-worker scheduler.
- Provide integration tests that reproduce and prevent regressions.

## Constraints / Assumptions
- Structural phases (1-4) remain per-spell; system phases (5-7) remain system-wide.
- No automatic revalidation unless explicitly triggered or marked dirty.

## Dependencies / External References
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/topology/spell_local_topology.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/utilities/synchronization/phase_scheduler.py`

## Milestones (Track Progress)
- [x] Milestone 1: Frame metadata captured in topology and persisted.
- [x] Milestone 2: Post-conjure structural phases for new bindings.
- [x] Milestone 3: Targeted revalidation and dirty propagation.
- [x] Milestone 4: Phase scheduler fail-fast behavior.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-18-melder-post-conjure-binding - Support post-conjure binds with targeted revalidation.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-18-melder-post-conjure-binding

## Acceptance Criteria (Epic Done)
- New bindings after conjure are validated without full system rerun.
- Frame/collection sockets are tracked for targeted revalidation.
- Scheduler does not hang on missing phase errors.
- Integration tests pass for post-conjure bind/scan workflows.

## Risks / Mitigations
- Risk: Over-marking dirty lineages causes excessive revalidation. Mitigation: store frame-key metadata and only target affected sockets.
- Risk: Concurrency issues in scheduler changes. Mitigation: add fail-fast tests under single-worker config.

## Validation / Test Approach
- Add integration tests for post-conjure bind/scan and targeted revalidation.
- Add unit tests for topology metadata and scheduler fail-fast behavior.

## Rollout / Adoption Plan
- Land metadata changes first, then revalidation hooks, then scheduler adjustments.

## Open Questions
- Should revalidation be automatic on bind or opt-in per conduit?
- Should dirty propagation be by frame key only, or include binding_name granularity?

## Decision Log
- 2026-01-18: Track and target frame-based sockets to avoid full reruns.

## Context / Handoff Summary
- Story tasks complete; epic ready for acceptance and closure.
