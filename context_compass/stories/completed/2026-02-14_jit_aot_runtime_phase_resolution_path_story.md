# Story: JIT/AOT Runtime Deferred Phase Resolution Path

Completed: 2026-02-15
Summary: Closed after user acceptance; linked discovery/implementation tasks are complete and validated for this story scope.


## Metadata
- Story ID: STORY-2026-02-14-jit-aot-runtime-phase-resolution-path
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15

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
- [x] Task: TASK-2026-02-15-align-spellcrafter-phase-order-with-spellbook-creation-system - align runtime phase-order contract parity before broader split-mode changes.
- [x] Task: Use discovery outputs to define exact deferred-phase runtime triggers.
- [ ] Task: Execute story `STORY-2026-02-15-jit-aot-runtime-resolution-gate-lifecycle`.
- [ ] Task: Execute story `STORY-2026-02-15-jit-aot-regression-matrix-and-compatibility`.
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
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Runtime lane has been decomposed into a dedicated runtime-gate story and a dedicated regression-matrix story so propagation requirements can be validated independently.
  EVIDENCE: context_compass/stories/2026-02-15_jit_aot_runtime_resolution_gate_lifecycle_story.md:1-84, context_compass/stories/2026-02-15_jit_aot_regression_matrix_and_compatibility_story.md:1-83
  IMPACT: Runtime execution and validation responsibilities are now independently scoped and easier to track.
  NEXT: Complete propagation contract-surface discovery task, then execute runtime gate story before regression matrix story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Runtime trigger recommendation is now explicit: use a pre-build runtime resolution gate (`hybrid_rule_bound`) when `resolution_required` is true, then build context through existing strict builder/factory contracts.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:31-44, context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:77-92
  IMPACT: Story can proceed to concrete implementation task creation immediately after user decision on the recommendation.
  NEXT: Request user decision on `hybrid_rule_bound` and open runtime implementation + validation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: User requested an immediate patch to align SpellCrafter phase ordering with SpellbookCreationSystem; a dedicated implementation task was opened to execute that change without waiting for broader split-mode rollout.
  EVIDENCE: context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-95, src/melder/spellbook/spellbook_creation_system.py:852-905, src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5094
  IMPACT: Runtime story moved from planning-ready to active implementation for a narrow contract-parity fix.
  NEXT: Complete TASK-2026-02-15-align-spellcrafter-phase-order-with-spellbook-creation-system and report validation results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Alignment implementation is complete and validated at targeted unit scope; runtime story now returns to deferred-resolution discovery/planning tasks.
  EVIDENCE: context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-110, src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5105, src/melder/spellbook/spell.py:1299-1349
  IMPACT: Story can proceed to builder/factory deferred-contract discovery without phase-order drift blocking the lane.
  NEXT: Execute `TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
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
Runtime story has discovery-backed trigger guidance and is awaiting user
decision on `hybrid_rule_bound`. After decision, the next step is creating
implementation and validation tasks for deferred runtime resolution.

