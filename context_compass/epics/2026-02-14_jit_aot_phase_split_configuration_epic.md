# Epic: Implement Configurable JIT/AOT Phase Split for Runtime Resolution

## Metadata
- Epic ID: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15
- Target Window: 2026-Q1
- Related Program/Initiative: Runtime Resolution Flexibility

## Problem / Opportunity
Current spell execution contracts are oriented around full pre-runtime phase
materialization, and CreationContext build currently fails fast when crafter
artifacts do not exist. We need an optional configuration mode that can keep
current AOT behavior intact while enabling runtime resolution of later phases.

## MRP Alignment (Most Reasonable Product)
The MRP is a durable dual-mode contract:
- Full AOT remains default and unchanged.
- Optional split mode supports runtime assembly/resolution without invalidating
  spells that intentionally defer late-phase artifacts.
- Runtime path remains explicit, testable, and contract-safe.

## Goals (Outcomes)
- Add one configuration-controlled JIT/AOT split mode.
- Support optional deferred phases (user target: 8-12) at runtime.
- Add `resolution_required: bool` lifecycle contract on spells.
- Preserve spell validity when deferred resolution is intentional.
- Keep full AOT path behavior unchanged by default.

## Non-Goals (Explicit Exclusions)
- Rewriting all phase schedulers.
- Breaking current public spellbook/meld entrypoints.
- Blindly bypassing validation contracts without evidence.

## Scope Boundaries
- In scope:
- Discovery and contract mapping for phase ordering and deferred-resolution safety.
- Story/task scaffolding for config surface, spell-state contract, and runtime path.
- Explicit assumption-challenge step with user discussion.
- Out of scope:
- Immediate code implementation in this ticketing pass.
- Unrelated perf refactors outside JIT/AOT split design.

## Success Metrics
- Epic has linked discovery tasks and implementation stories with clear acceptance criteria.
- Discovery explicitly confirms or rejects the requested 1-7 / 8-12 split shape.
- At least one documented pushback/decision discussion is captured with evidence.

## Requirements (Functional + Non-Functional)
- Functional:
  - Define one config gate for full AOT vs split JIT/AOT behavior.
  - Define `resolution_required: bool` ownership, transitions, and consumers.
  - Define runtime build/resolution contract for deferred phases.
- Non-functional:
  - Keep backward compatibility for existing full AOT flows.
  - Maintain strict UNKNOWN-first evidence discipline in discovery notes.
  - Preserve microcycle documentation rigor.

## Constraints / Assumptions
- Constraint: Current phase ordering evidence shows phase 6-7 execution after
  phase 8-11 in `run_all_phases`; a direct "1-7 now, 8-12 later" split is not
  yet proven valid.
- Assumption: Desired split can be represented through configuration and spell
  state without API breakage (UNKNOWN until discovery completes).

## Dependencies / External References
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
- `src/melder/aether/conduit/meld/meld.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Discovery confirms viable split contract and phase-order constraints.
- [ ] Milestone 2: Implementation stories approved for config + spell-state + runtime path.
- [ ] Milestone 3: Explicit assumption challenge discussed with user and logged as decision.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability - Discovery and feasibility gates.
- [ ] Story: STORY-2026-02-14-jit-aot-configuration-and-spell-contract - Config and spell-state implementation scope.
- [ ] Story: STORY-2026-02-14-jit-aot-runtime-phase-resolution-path - Runtime deferred-resolution implementation scope.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-14-jit-aot-split-discovery-and-viability.
- [ ] Task: Complete story STORY-2026-02-14-jit-aot-configuration-and-spell-contract.
- [ ] Task: Complete story STORY-2026-02-14-jit-aot-runtime-phase-resolution-path.
- [ ] Task: Execute explicit user-facing assumption challenge discussion task.
- [ ] Task: Verify Ticket Microcycle enforcement across active stories/tasks.

## Acceptance Criteria (Epic Done)
- Discovery produces evidence-backed decision on requested phase split semantics.
- Stories have implementation-ready scope and non-goals with no hidden assumptions.
- `resolution_required` contract is defined and reviewed before implementation.
- User confirms acceptance after explicit challenge discussion.

## Risks / Mitigations
- Risk: Requested 1-7 split conflicts with existing phase dependencies.
  Mitigation: discovery-first phase-order contract map and explicit decision gate.
- Risk: Runtime deferral could hide invalid spells.
  Mitigation: define validity semantics + regression requirements before code changes.

## Validation / Test Approach
- Discovery validation: evidence-backed notes and decision logs only.
- Implementation validation (future): targeted unit tests for spell/creation-context
  lifecycle and regression checks for full AOT compatibility.

## Rollout / Adoption Plan
- Execute discovery tasks first.
- Review evidence and challenge findings with user.
- Only then create/execute implementation tasks under linked stories.

## Open Questions
- Can phase 6-7 contracts run safely if 8-11 are deferred?
- Where should `resolution_required` flip from true to false in runtime flow?
- Should phase 12 be treated as part of deferred runtime set or separate lane?

## Decision Log
- 2026-02-14: Epic created from user request to add configurable JIT/AOT split with runtime deferred resolution and a spell-level `resolution_required` flag.
- 2026-02-14: Added explicit assumption-challenge task per user request to push back on weak ideas with evidence.

## Notes
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: User requested immediate implementation of the phase-order parity patch; epic execution moved from discovery-ready to in-progress with a dedicated alignment task.
  EVIDENCE: context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-95, context_compass/stories/2026-02-14_jit_aot_runtime_phase_resolution_path_story.md:1-83
  IMPACT: Epic now includes an active narrow implementation lane ahead of broader split-mode rollout.
  NEXT: Complete TASK-2026-02-15-align-spellcrafter-phase-order-with-spellbook-creation-system and reassess remaining discovery order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Phase-order parity task is implemented and validated; epic focus now shifts back to deferred-runtime discovery tasks, starting with creation-context builder/factory contract options.
  EVIDENCE: context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-110, context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:1-78
  IMPACT: Epic sequencing is unblocked for contract viability mapping on deferred runtime behavior.
  NEXT: Execute `TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current spell-level phase sequence runs 8-11 before 6-7 in `run_all_phases`, while structural-only helper runs only 1-4.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:5018-5045, src/melder/spellbook/spell_crafter/spell_crafter.py:5058-5069, src/melder/spellbook/spell.py:1270-1297, src/melder/spellbook/spell.py:1305-1319
  IMPACT: The requested "1-7 now, 8-12 later" split may require contract changes; it is not yet proven by current ordering.
  NEXT: Execute `TASK-2026-02-14-discovery-jit-aot-phase-order-contract`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: CreationContext build path currently requires crafter artifacts for non-existing creations and runtime retrieval is routed through spell/factory switch paths.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:82-86, src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264, src/melder/spellbook/spell.py:469-497, src/melder/aether/conduit/meld/meld.py:345-373
  IMPACT: Deferred-phase mode must define how builder/factory contracts behave when late artifacts are intentionally absent.
  NEXT: Execute `TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created and routed to discovery-first execution. No implementation has
started. Next step is phase-order feasibility discovery, followed by builder
contract discovery and explicit assumption challenge discussion.
