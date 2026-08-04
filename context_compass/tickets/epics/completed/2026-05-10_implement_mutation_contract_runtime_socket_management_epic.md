Completed: 2026-06-06T18:18:17Z
Summary: Closed per user direction as historical completed work. The original MutationContract runtime-socket-management program was superseded by the later overlay-first mutation override direction and downstream compiler/runtime convergence work.

# Epic: Implement Mutation Contract Runtime Socket Management

## Metadata
- Epic ID: EPIC-2026-05-10-implement-mutation-contract-runtime-socket-management
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T19:02:12Z
- Updated: 2026-06-06T18:18:17Z
- Target Window: 2026-Q2
- Related Program/Initiative: Dynamic spell mutation semantics and governed runtime retargeting

## Problem / Opportunity
`MutationContract` exists today as a declared mutation socket shape, but it does
not yet have a real runtime usage story. The descriptor is classified in Phase
1, preserved as metadata in Phase 3, and then blocked in Phase 4 with
`MUTATION_CONTRACT_DISABLED`.

At the same time, the runtime already has meaningful mutation-related
invalidation behavior:
- `Spell.mutation_override`
- `Spell.apply_mutation_override(...)`
- `Spell.clear_mutation_override(...)`
- `SpellSystemStates.mark_structural_change(...)`
- meld-time revalidation/gating

That creates a concrete opportunity:
- define `MutationContract` as a mutable single dependency socket
- expose spell-facing APIs to inspect and retarget those sockets
- clear the spell-owned creation context when a socket changes
- mark the SpellIndex dirty/gated so the next resolve path re-evaluates fit

This would make MutationContract useful even before a full MutationResearch
promotion system is finished.

## MRP Alignment (Most Reasonable Product)
The MRP is not a complete mutation runtime overhaul.

The MRP is:
- one investigation that proves the exact source seams
- one first implementation slice that lets a spell enumerate mutation sockets
- one explicit retarget/update path for a socket
- invalidation/revalidation hooks through existing Spell / SpellSystemStates
  machinery

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the direction of using
  `MutationContract` as a mutable single dependency socket and asked for an
  epic so we can investigate and then implement it.
- EXECUTION_BOUNDARY: investigate and implement the runtime socket-management
  layer for `MutationContract` without widening into broad MutationResearch or
  module-version promotion work.
- DEPENDENCIES:
  - `src/melder/aether/conduit/meld/contracts/mutation_contract.py`
  - `src/melder/spellbook/spell.py`
  - `src/melder/spellbook/spell_crafter/**`
  - `src/melder/aether/conduit/meld/overrides/graph_mutator.py`
  - `src/melder/aether/dev_ops/spell_system_states/**`
- EXIT_GATE: the first real MutationContract runtime feature exists and is
  validated.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current mutation socket
  metadata is too thin and a larger contract redesign is required before safe
  implementation.

## Goals (Outcomes)
- Define the real intended role of `MutationContract`.
- Investigate where mutation sockets are already represented in runtime
  metadata.
- Add a spell-facing API to inspect mutation sockets.
- Add a spell-facing API to retarget or clear a mutation socket target.
- Reuse current invalidation/revalidation mechanisms rather than inventing a
  second dirty-state system.

## Non-Goals (Explicit Exclusions)
- Full MutationResearch promotion system.
- Full module-version promotion/runtime adoption choreography.
- Broad conduit ownership redesign.
- Broad graph-mutation UX or agent tooling beyond the first API slice.

## Scope Boundaries
- In scope:
  - `MutationContract` runtime interpretation
  - spell-facing socket enumeration
  - spell-facing socket retarget/clear API
  - dirty/index revalidation trigger behavior
  - focused tests for the new mutation-contract feature
- Out of scope:
  - full MutationResearch lane/head/merge system
  - module mutation/version promotion
  - conduit-lineage semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new epic so the
  MutationContract runtime-socket feature can be investigated and then
  implemented.

## Success Metrics
- We can explain what MutationContract is actually for in runtime terms.
- A spell can expose its mutation sockets explicitly.
- A spell can retarget a mutation socket explicitly.
- Retargeting triggers the existing invalidation/revalidation path.
- Focused tests prove the feature.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify mutation sockets on a spell
  - return them in an inspectable form
  - allow target mutation through a supported API
  - clear spell-owned creation context when a socket changes
  - mark SpellIndex / spell state dirty for revalidation
- Non-functional:
  - keep the first feature bounded
  - no conduit-lineage spillover
  - no fake promotion semantics

## Constraints / Assumptions
- MutationContract is currently metadata-only and blocked in validation.
- `mutation_override` is the only real active mutation mechanism today.
- Existing invalidation/revalidation machinery should be reused rather than
  rebuilt.
- Dynamic mode is the only meaningful runtime posture for this feature.

## Dependencies / External References
- current mutation-contract and mutation-override source reads
- current SpellIndex / SpellSystemStates / meld revalidation behavior

## Milestones (Track Progress)
- [ ] Milestone 1: investigate current mutation socket semantics and concrete runtime hooks
- [ ] Milestone 2: implement spell-facing mutation socket inspection + retarget path
- [ ] Milestone 3: validate the feature with focused tests

## Stories (Required to Complete)
- [ ] Story: investigate current mutation-contract and mutation-override seams
- [ ] Story: implement spell-facing mutation socket runtime API
- [ ] Story: validate mutation socket retargeting and re-evaluation behavior

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: investigate the current runtime MutationContract story
- [ ] Task: define the spell-facing mutation-socket API shape
- [ ] Task: implement socket retarget/clear behavior
- [ ] Task: add focused tests for socket mutation + revalidation trigger

## Acceptance Criteria (Epic Done)
- The current MutationContract runtime role is explicit and source-backed.
- A first real spell-facing mutation-socket feature exists.
- The feature uses existing dirty/revalidation machinery instead of bypassing it.
- Focused tests pass.

## Risks / Mitigations
- Risk: feature design drifts into full MutationResearch redesign.
  Mitigation: keep the first slice on spell-facing socket retargeting only.
- Risk: runtime invalidation semantics become ambiguous.
  Mitigation: route all state change through explicit spell APIs and existing
  SpellSystemStates gating.

## Applicable Anti-Patterns
- [ ] No epic-state transition without evidence-backed scope.
- [ ] No pretending MutationContract is already a live DI provider.
- [ ] No conduit-lineage drift.
- [ ] No full mutation-runtime overbuild in the first feature slice.

## Validation / Test Approach
- Investigation first.
- Then focused unit/component/integration tests around:
  - mutation socket discovery
  - mutation socket retargeting
  - creation-context invalidation
  - spell-state dirty/revalidation trigger behavior

## Rollout / Adoption Plan
- First: investigate exact runtime seams
- Second: implement spell-facing API
- Third: validate
- Fourth: decide whether to widen into MutationResearch promotion later

## Open Questions
- Should the first API mutate the `MutationContract` descriptor itself, or a
  spell-owned overlay representation of it?
- Is `mark_structural_change(...)` sufficient as the first invalidation hook,
  or do we want a more specific contract-style dirty reason?
- What exact socket-inspection payload is the smallest useful user/agent shape?

## Decision Log
- 2026-05-10T19:02:12Z: Opened after the user approved the “mutable single
  dependency socket” direction for MutationContract and asked for an epic so
  we can investigate and then implement it.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-10T19:02:12Z
  TYPE: FACT
  CLAIM: The current code already gives us the split we need for a first
    feature definition. `MutationContract` is classified in Phase 1 and
    preserved as metadata, `mutation_override` is the real active spell-level
    mutation hook, and Spell / SpellSystemStates already clear creation context
    and mark structural change when mutation overlay state changes.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:10-175
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:1044-1104
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3437-3465
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:106-123
  - src/melder/spellbook/spell.py:1574-1646
  IMPACT: The first feature can be built on existing invalidation/revalidation
    seams instead of needing a full new mutation runtime from scratch.
  NEXT: route the first investigation task and inspect the exact spell-facing
    socket metadata path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic owns the investigation and first implementation slice for making
MutationContract a real spell-facing mutable socket feature instead of a purely
blocked metadata placeholder.
