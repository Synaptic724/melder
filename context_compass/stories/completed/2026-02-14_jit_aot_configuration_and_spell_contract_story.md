# Story: JIT/AOT Configuration and Spell Contract

Completed: 2026-02-15
Summary: Closed after user acceptance; linked discovery/implementation tasks are complete and validated for this story scope.


## Metadata
- Story ID: STORY-2026-02-14-jit-aot-configuration-and-spell-contract
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15

## User Narrative
As a spellbook integrator, I want a clear configuration mode and spell-level
`resolution_required` contract, so that deferred runtime resolution is explicit
and does not silently break validity semantics.

## Value / MRP Alignment
This story defines stable API/contract boundaries before runtime-path code
changes, keeping full AOT default behavior safe while enabling a deliberate
split mode.

## Requirements (Functional)
- Define one configuration surface for `full_aot` vs `split_jit_aot` behavior.
- Define `resolution_required: bool` ownership and lifecycle transitions.
- Define how spell validity is interpreted when resolution is intentionally deferred.
- Define default behavior as full AOT with no behavioral change.

## Requirements (Non-Functional)
- Backward-compatible by default.
- No public API breakage without explicit decision.
- Discovery evidence must be completed before implementation tasks are started.

## Scope Boundaries
- In scope:
- Configuration contract and spell-state contract design plus implementation planning.
- Out of scope:
- Runtime execution-path code changes (handled in runtime story).

## Dependencies / Related Work
- `STORY-2026-02-14-jit-aot-split-discovery-and-viability`
- `TASK-2026-02-14-discovery-jit-aot-resolution-required-spell-contract`
- `TASK-2026-02-14-discovery-jit-aot-assumption-challenge`

## Tasks (Implementation Checklist)
- [ ] Task: Use discovery outputs from `TASK-2026-02-14-discovery-jit-aot-resolution-required-spell-contract` as design baseline.
- [ ] Task: Execute story `STORY-2026-02-15-jit-aot-config-flag-and-fluent-api`.
- [ ] Task: Execute story `STORY-2026-02-15-jit-aot-conjure-propagation`.
- [ ] Task: Execute story `STORY-2026-02-15-jit-aot-post-conjure-bind-propagation`.
- [ ] Task: Execute story `STORY-2026-02-15-jit-aot-transfer-ownership-propagation-non-contracted`.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Configuration contract is specified with default + optional modes.
- Spell `resolution_required` contract is specified with lifecycle transitions.
- User reviews and accepts the proposed contract before implementation tasks proceed.

## Validation / Test Plan
- Design-time validation via evidence and decision logs.
- Implementation validation deferred to downstream tasks.

## UX / API / Data Notes
- Configuration naming and placement remain UNKNOWN until discovery confirms integration points.

## Risks / Mitigations
- Risk: Contract may be under-specified and force rework later.
  Mitigation: require explicit lifecycle state table and user acceptance before coding.

## Open Questions
- Where should configuration live (spellbook creation config vs conduit runtime config)?
- Is `resolution_required` persisted, computed, or both?

## Decision Log
- 2026-02-14: Story created to isolate configuration/spell-state contract before runtime execution changes.

## Notes
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: This umbrella story has been decomposed into focused implementation stories covering config/fluent API plus three propagation surfaces (conjure, late bind, transfer owned-only).
  EVIDENCE: context_compass/stories/2026-02-15_jit_aot_config_flag_and_fluent_api_story.md:1-83, context_compass/stories/2026-02-15_jit_aot_conjure_propagation_story.md:1-82, context_compass/stories/2026-02-15_jit_aot_post_conjure_bind_propagation_story.md:1-79, context_compass/stories/2026-02-15_jit_aot_transfer_ownership_propagation_non_contracted_story.md:1-82
  IMPACT: Scope is clearer and each propagation requirement now has a dedicated acceptance surface.
  NEXT: Complete propagation contract-surface discovery task, then execute decomposed stories in order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Spell runtime context retrieval currently routes through spell-owned switch/factory paths and can bypass rebuild when context is already open.
  EVIDENCE: src/melder/spellbook/spell.py:469-497, src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264, src/melder/aether/conduit/meld/meld.py:345-373
  IMPACT: `resolution_required` and config mode must align with these fast paths to avoid stale or missing context behavior.
  NEXT: Wait for discovery story outputs before creating implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Configuration/spell contract story is prepared and intentionally gated on
discovery outputs to avoid speculative API design.

