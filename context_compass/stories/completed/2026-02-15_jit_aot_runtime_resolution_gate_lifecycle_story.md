# Story: JIT/AOT Runtime Resolution Gate Lifecycle

Completed: 2026-02-15
Summary: Closed after user acceptance; linked discovery/implementation tasks are complete and validated for this story scope.


## Metadata
- Story ID: STORY-2026-02-15-jit-aot-runtime-resolution-gate-lifecycle
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## User Narrative
As a runtime maintainer, I want `resolution_required` to gate deferred phases
before context build so JIT mode remains safe and deterministic.

## Value / MRP Alignment
This preserves strict builder/factory contracts while enabling deferred runtime
resolution through orchestration.

## Requirements (Functional)
- At runtime, when `resolution_required=true`, run deferred resolution gate before context build.
- Set `resolution_required=false` only after gate success.
- Fail fast on unresolved invalid states and do not build context.
- Re-gate (`true`) on events that invalidate resolution readiness.

## Requirements (Non-Functional)
- Preserve full AOT behavior.
- Keep runtime entrypoint changes scoped.

## Scope Boundaries
- In scope:
- Meld runtime gate path and spell flag lifecycle transitions.
- Out of scope:
- Config API and transfer behavior.

## Dependencies / Related Work
- `TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces`
- `TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract`
- `TASK-2026-02-14-discovery-jit-aot-resolution-required-spell-contract`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-15-implement-jit-aot-runtime-resolution-gate-lifecycle - implement runtime gate and flag transitions.
- [ ] Task: TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces - confirm final runtime insertion points.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Runtime gate executes deferred resolution before context build when required.
- Flag transitions are deterministic (`True->False` on success, fail-fast on invalid).
- Full AOT path remains unchanged.

## Validation / Test Plan
- Unit tests for runtime gate state transitions and failure outcomes.

## UX / API / Data Notes
- Internal behavior; no external API shape change expected.

## Risks / Mitigations
- Risk: duplicate gating or stale flag clears.
  Mitigation: centralize lifecycle transitions at one runtime gate point.

## Open Questions
- Which mutation/contract change hooks should always force `resolution_required=true`?

## Decision Log
- 2026-02-15: Story created from user-approved `hybrid_rule_bound` direction.

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Existing runtime path already enforces lineage revalidation before context retrieval, so `resolution_required` integration should hook this path instead of creating a second resolver.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:402-430, src/melder/aether/conduit/meld/meld.py:569-619, src/melder/spellbook/spell.py:469-497
  IMPACT: Limits implementation risk and preserves current runtime architecture.
  NEXT: Complete propagation discovery map and then implement flag lifecycle updates at the runtime gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Ready runtime-lifecycle story. Gated on discovery confirmation of final entrypoints.


