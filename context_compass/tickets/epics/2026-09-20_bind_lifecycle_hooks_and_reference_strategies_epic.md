# Epic: Extend binding with reference checks, Spell activation and post-bind hooks

## Metadata
- Epic ID: EPIC-2026-09-20-bind-lifecycle-hooks-and-reference-strategies
- Status: draft
- Owner: user
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-20T08:04:19Z
- Updated: 2026-09-20T08:10:09Z
- Target Window: future owner-approved implementation
- Related Program/Initiative: Spellbook registration, Bind admission and Spell lifecycle

## Current Authorization
Create this epic only. The owner requested all three bind-time extension points below. No runtime
implementation, new hook API, feature tests or release work is authorized by this planning request.

## Problem / Opportunity
Applications need to extend registration itself: check an incoming reference using user-added
strategies, modify the resulting Spell during bind activation, and run post-bind hooks after binding.
These operations should share the canonical binding flow so callers do not have to reproduce its
profiling, identity, registration, compilation or publication responsibilities.

## Owner-Requested Stages

| Stage | Intended subject | Requested purpose |
| --- | --- | --- |
| Pre-bind | The incoming reference and relevant binding context | Allow strategies to be added to check whether the reference may be bound |
| Bind activation | The Spell being established by this bind | Allow user hooks to modify the Spell through a defined mutation contract |
| Post-bind | The completed binding and final Spell/result | Allow follow-up hooks after binding succeeds |

The activation subject is the **Spell definition**, not a resolved application instance. Pre-bind
checks should work with supported class, callable and existing-object references without constructing
them merely to perform a check.

## Existing Hooks Are a Separate Lifecycle
The current `pre_hooks`, `activation_hooks` and `post_hooks` arguments are attached to the Spell by
Spellbook._add_hooks_to_spell. Spell._set_hooks describes them as pre-cast, newly created-instance
activation and post-cast hooks. ConduitMeld consumes them during Meld execution.

Preserve that existing behavior. This epic adds **bind-time** stages; it must not silently repurpose
the current creation hooks. Candidate names such as `pre_bind_strategies`, `bind_activation_hooks`
and `post_bind_hooks` are provisional vocabulary, not an implemented or finalized public API.

Evidence:
- `src/melder/aether/spellbook/spellbook.py:5380-5428`
- `src/melder/aether/spellbook/spell.py:637-684`
- `src/melder/aether/conduit/meld/conduit_meld.py:414-456`
- `tests/integration/melder/spellbook/test_spellbook_integration_hooks.py:38-131`

## MRP Alignment
Make customization explicit at registration while preserving one authoritative Spell, identity and
publication outcome. The three stages should have predictable ordering and failure semantics, and
ordinary binding should retain its existing behavior when no bind-time extensions are configured.

## Ticket Contract
- ENTRY_GATE: Owner accepts a concrete discovery/design result before implementation; create bounded
  stories/tasks and the required patch contracts when that work is selected.
- EXECUTION_BOUNDARY: Bind-time strategy/hook registration, execution ordering, permitted Spell edits,
  coherent finalization/publication and related tests/docs. Existing instance-creation hooks remain separate.
- DEPENDENCIES: Existing Bind/Spellbook pipeline, Spell identity/state, configuration and hook patterns,
  staged/active bind paths, Crystallizer/MR/Nexus confirmation points and transaction/cleanup rules.
- EXIT_GATE: All three approved stages are usable, callback/strategy failures have defined outcomes,
  identity/publication remains coherent and compatibility/regression evidence is accepted.
- FAILURE_ESCALATION: Resolve mutation authority and failure/rollback semantics before coding; do not
  permit arbitrary private-field edits to bypass fingerprint, lookup, validation or ownership rules.

## Goals (Outcomes)
- Register and compose pre-bind reference-checking strategies in a defined order.
- Reject invalid references before publishing a new binding, with actionable strategy diagnostics.
- Expose a bind-activation stage where users can modify the Spell through the supported contract.
- Invoke post-bind hooks with the successful, finalized binding result.
- Preserve one consistent implementation across direct, fluent, decorator, scan and Conduit forwarding
  entry points that reach binding, with explicit treatment of bind_inactive and replay.
- Make hook configuration, ownership and cleanup clear without adding work to ordinary Meld execution.

## Non-Goals
- Implementing the feature in this epic-creation pass.
- Renaming or changing existing pre-cast/instance-activation/post-cast hook semantics.
- Replacing the DI compiler, introducing new instance lifetimes or changing external-object ownership.
- Bypassing native internal-target, Protocol, uniqueness, existence or capability validation.
- Arbitrary live mutation of an already published Spell or automatic serialization of hook code.
- Implementing purge or named lesser conduits as part of this work.

## Scope Boundaries
- In scope: the three bind-time stages and the machinery necessary to make their effects coherent.
- Out of scope: unrelated runtime hooks, generalized plugin frameworks and speculative global registries.
- Exact setter/decorator/configuration names and callback signatures remain design work.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Owner requested a durable feature epic, not runtime implementation.

## Proposed Lifecycle to Validate

```text
incoming reference + bind options
    -> configured pre-bind reference strategies
    -> construct/prepare the Spell
    -> bind-activation hooks apply permitted Spell changes
    -> validate/finalize identity, registration and publication consistently
    -> post-bind hooks receive the completed binding
```

This is the intended ordering to investigate, not a claim that the current implementation already
has a provisional-Spell stage. Bind currently computes a fingerprint before constructing the Spell.
Spellbook subsequently claims the lookup and populates maps, then stages structural work and emits
record/publication data. The activation mutation point must account for those real boundaries.

Evidence:
- `src/melder/aether/spellbook/bind/bind.py:433-551`
- `src/melder/aether/spellbook/spellbook.py:5190-5310`

## Requirements
- Define strategy registration, ordering, duplicate/removal behavior and the pre-bind result contract.
  Decide whether rejection is an explicit result or an exception; do not silently coerce truthy values.
- Give pre-bind strategies the actual reference and sufficient context to check it. Reference
  replacement/transformation is not part of the requested checking capability unless later approved.
- Define exactly which Spell fields activation hooks may modify and through which supported methods.
  Preserve the owner's intent to customize the Spell; do not silently reduce activation to observation.
- Classify identity-bearing, compiler-relevant and descriptive edits. Either finalize affected derived
  state from the accepted final values or reject unsupported edits explicitly before registration.
- Return and publish the final consistent spell identity. Lookup claims, SpellIndex membership,
  compiler inputs, supplied-instance registration, Crystallizer records, research entries and Nexus
  descriptors must not describe different intermediate versions of the same bind.
- Specify post-bind timing and payload, including whether it occurs inside or after the transaction.
  State clearly what remains committed if a post-bind hook raises; do not pretend external side effects
  can always be rolled back.
- Define failure behavior at each phase: later callbacks, partial Spell disposal, lookup claims,
  registration visibility and emitted records. Failed pre-bind checks must not publish a binding.
- Preserve native validation and existing creation hooks; activating a Spell for registration must
  not invoke the application constructor or its instance-activation hook.
- Make active versus inactive binding, pre/post-conjure binding and all wrappers consistent. Define
  whether lifecycle stages rerun when restore/graft re-enters bind and how duplicate effects are avoided.
- Use current configuration/strategy/hook conventions where suitable. Decide global/book/per-bind
  scope and precedence explicitly, including what may change after configuration freeze.
- Establish callback ownership, cleanup, reentrancy and concurrency contracts from the existing locks
  and transaction model. Document whether binding recursively from a hook is supported or refused.
- Keep the unconfigured path small. Measure any performance claim; do not add per-Meld checks for a
  feature that belongs to binding.

## Required Reading Before Further Work
Use current architecture/component indexes, then graph slices and the real source. Finish complete
relevant implementations before editing; documentation and search hits are navigation aids.

- `system_docs/src_components_index.md`: Spellbook Core; Binding Pipeline; Spellbook Configuration
  and System State; SpellCompiler and Validation Pipeline; Nexus Descriptor And ACL Managers;
  Crystallizer Root; MutationResearch Root and ResearchSet.
- `system_docs/src_graph_index.md`: verify and slice owners identified by those component sections.
- `src/melder/aether/spellbook/bind/bind.py`: admission, profiles, fingerprinting and Spell construction.
- `src/melder/aether/spellbook/spellbook.py`: bind, bind_inactive, _add_hooks_to_spell, registration,
  transaction boundaries, structural staging and crystal/research/Nexus emission.
- `src/melder/aether/spellbook/spell.py`: native fields, immutability, metadata, _set_hooks and cleanup.
- `src/melder/aether/spellbook/bind/spell_index.py`: membership/selection and identity ownership.
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`: setters, hooks and freeze.
- `src/melder/aether/spellbook/spellbinder.py`: fluent configuration, finalize and reset.
- `src/melder/aether/spellbook/bind/scan.py`: scan_bind metadata and replayed bind arguments.
- `src/melder/aether/conduit/conduit.py`: bind/bind_inactive forwarding and transaction context.
- `src/melder/aether/conduit/meld/conduit_meld.py` and
  `src/melder/aether/conduit/meld/spellspace_meld.py`: existing creation-hook semantics to preserve.
- `src/melder/utilities/custom_exceptions/hook_execution_error.py`: existing hook error vocabulary.
- `src/melder/crystallizer/crystals/spell_crystal.py`: capture final bind values and callable-policy limits.
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py` and
  `src/melder/crystallizer/crystal_loader_system/graft_runner.py`: bind re-entry during reconstruction.
- `src/melder/nexus/frame_descriptor_manager.py` and
  `src/melder/mutation_research/mutation_research.py`: final registration publication/history.
- Existing tests to read before extending: `tests/integration/melder/spellbook/test_spellbook_integration_hooks.py`,
  `tests/unit/melder/spellbook/test_scan_bind.py`, `tests/unit/melder/spellbook/test_spellbinder.py`,
  `tests/unit/melder/aether/spellbook/test_bind_kwargs_metadata.py` and the current test-system indexes.

## Milestones
- [x] Capture the three requested bind stages and distinguish existing creation hooks.
- [ ] Trace registration/configuration/identity boundaries and settle the hook contract.
- [ ] Create approved stories/tasks and patch contracts with focused failing regressions.
- [ ] Implement pre-bind strategies, Spell activation customization and post-bind callbacks.
- [ ] Qualify failure, identity, wrapper, replay and existing-hook compatibility; update docs/assets.

## Stories (Proposed; Not Yet Created)
- [ ] Define strategy registration, lifecycle payloads, ordering and errors.
- [ ] Add pre-bind reference-checking strategies at the agreed admission point.
- [ ] Add activation-time Spell modification with coherent identity and publication finalization.
- [ ] Add post-bind hooks and qualify the complete lifecycle across entry points and replay.

## Acceptance Criteria
- A user can add multiple reference-checking strategies and observe the documented execution order.
- A rejected reference leaves no successfully published binding or success post-bind notification.
- An activation hook can make a supported Spell change, and the returned identity, registries,
  compiler inputs and emitted records reflect that same final result.
- Post-bind hooks observe the documented completed state exactly once per successful bind operation.
- Failure, cleanup and retry behavior match the approved contract without orphaned local state.
- Existing creation hooks retain their current execution timing and newly created-instance subject.
- Direct/fluent/decorator/scan/Conduit and active/inactive/replay behavior follow the explicit matrix.
- Ordinary unconfigured binding and Meld behavior retain compatibility.

## Validation / Test Approach
Tests: Not run. This pass only creates the epic.

Future regressions should cover ordered acceptance/rejection, each hook raising, supported and refused
Spell edits, identity-affecting values, collisions, staged binds, post-conjure binds, wrapper reset,
non-resolvable definitions, existing-object references, replay/graft, recursive binds and concurrent
binds. Assert final state and user-visible behavior rather than only callback counts or private fields.

## Risks / Mitigations
- Spell changes after hashing can invalidate identity: settle the mutation/finalization boundary first.
- Existing hook names look similar but run during meld: use explicit bind-time vocabulary.
- Publication before activation finishes can expose conflicting state: trace every confirmation sink.
- Arbitrary user callbacks inside locks can re-enter binding: define supported behavior from source.

## Open Questions
- Where are strategies/hooks configured, and what is the book/per-bind precedence?
- What are their exact signatures, result types and failure contracts?
- Which Spell edits are supported, especially native immutable or identity-bearing fields?
- When does post-bind run relative to commit, structural work and passive publication?
- How do bind_inactive, decorator/scan, restore and graft participate?
- What are recursion, concurrent registration, freeze and callable persistence rules?

## Decision Log
- Owner requested pre-bind reference strategies, Spell-modifying activation hooks and post-bind hooks.
- Existing pre/activation/post creation hooks must remain behaviorally distinct.
- Public names and implementation details are unselected; this is planning only.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: future accepted feature closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: settle the source-backed mutation and failure boundaries before implementation.

## Notes
- DATETIME: 2026-09-20T08:04:19Z
  TYPE: DECISION
  CLAIM: Owner requested an epic for all three registration lifecycle stages. Existing bind kwargs
    install creation hooks on Spell; Meld later invokes them against construction/resolution. The new
    activation stage instead targets the Spell definition and needs an explicit finalization boundary.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5380-5428
  - src/melder/aether/spellbook/spell.py:637-684
  - src/melder/aether/conduit/meld/conduit_meld.py:414-456
  - src/melder/aether/spellbook/bind/bind.py:433-551
  IMPACT: Preserve the three-stage intent without conflating it with existing instance hooks or
    promising unsupported private Spell mutation. No feature is implemented by this record.
  NEXT: Owner reviews the epic and selects discovery/implementation as a separate step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T08:10:09Z
  TYPE: FACT
  CLAIM: Draft epic records all three requested stages, the existing creation-hook distinction,
    mutation/finalization and failure questions, proposed story boundaries and concrete reading paths.
    Referenced paths resolve; no runtime, tests, release document or generated assets were changed.
  EVIDENCE:
  - tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md:14-43
  IMPACT: The feature can be resumed through one planning record without conflating bind and meld hooks.
  NEXT: Owner reviews the draft before selecting deeper discovery or implementation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Feature implementation and validation delivered in a later authorized pass.
- [ ] Owner accepts the final hook, mutation and failure contracts.

## Noting Behavior
Record shared lifecycle decisions here; future child tasks own source traces and verification evidence.

## Context / Handoff Summary
Draft epic only. Pre-bind strategies check the incoming reference; bind-activation hooks modify the
Spell through a defined contract; post-bind hooks observe the completed binding. Existing creation
hooks are separate. Identity/finalization, callback registration and failure/replay behavior require
discovery before implementation. No code, tests, build assets or 0.2.43 release scope changed.
