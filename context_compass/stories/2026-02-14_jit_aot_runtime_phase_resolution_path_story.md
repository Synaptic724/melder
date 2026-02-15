# Story: JIT/AOT Runtime Deferred Phase Resolution Path

## Metadata
- Story ID: STORY-2026-02-14-jit-aot-runtime-phase-resolution-path
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a runtime maintainer, I want a safe deferred-resolution runtime path for
split JIT/AOT mode, so that spells can be instantiated without invalidation and
late phases can resolve on demand.

## Value / MRP Alignment
This story carries the runtime behavior changes after discovery confirms
contracts, preserving the MRP principle of reliable defaults plus explicit
opt-in flexibility.

## Requirements (Functional)
- Define runtime trigger points for deferred phase execution in split mode.
- Define interaction between `resolution_required` and runtime context build/get.
- Define correctness guardrails so full AOT behavior remains unchanged.
- Define fallback/error semantics when deferred resolution fails.

## Requirements (Non-Functional)
- No regressions for default full AOT path.
- Deterministic behavior under concurrent context access.
- Explicit test matrix for split mode vs full AOT.

## Scope Boundaries
- In scope:
- Runtime deferred phase-resolution behavior design and implementation planning.
- Out of scope:
- Initial config naming/placement decisions (handled in config story).

## Dependencies / Related Work
- `STORY-2026-02-14-jit-aot-split-discovery-and-viability`
- `STORY-2026-02-14-jit-aot-configuration-and-spell-contract`
- `TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract`
- `TASK-2026-02-14-discovery-jit-aot-phase-order-contract`

## Tasks (Implementation Checklist)
- [ ] Task: Use discovery outputs to define exact deferred-phase runtime triggers.
- [ ] Task: Create implementation task for runtime phase-resolution path after discovery decision gate.
- [ ] Task: Create validation task for split-mode regression matrix after implementation scope is approved.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Runtime deferred-resolution strategy is specified with explicit trigger points.
- Failure semantics and fallback behavior are defined and reviewed.
- Downstream implementation/validation tasks are scoped and ready.

## Validation / Test Plan
- Planning phase: discovery evidence + decision review.
- Implementation phase (future): targeted unit tests + regression matrix for AOT and split mode.

## UX / API / Data Notes
- Runtime behavior is internal; external API changes should be avoided where possible.

## Risks / Mitigations
- Risk: Deferred execution introduces race/state bugs around creation-context readiness.
  Mitigation: design around existing switch election and context ownership rules.

## Open Questions
- Should deferred execution happen at meld entry only, or also at context build time?
- What minimal artifact set is required before allowing runtime instance creation?

## Decision Log
- 2026-02-14: Story created as runtime-implementation lane, explicitly gated by discovery and contract stories.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Meld path currently uses spell-owned creation-context switch gating and resolves/builds context on demand through `_get_or_build_creation_context`.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:345-373, src/melder/spellbook/spell.py:469-497, src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264
  IMPACT: Runtime deferred-phase design must integrate with current switch-based context ownership, not bypass it.
  NEXT: Wait for discovery outputs, then create concrete implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Runtime story is staged and blocked on discovery + contract decisions. It will
translate approved split semantics into implementation tasks once feasibility is
proven.
