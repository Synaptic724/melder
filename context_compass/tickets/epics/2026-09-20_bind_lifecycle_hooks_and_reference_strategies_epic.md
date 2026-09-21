# Epic: Extend binding with reference checks, Spell activation and post-bind hooks

## Metadata
- Epic ID: EPIC-2026-09-20-bind-lifecycle-hooks-and-reference-strategies
- Status: in_progress
- Owner: user
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-20T08:04:19Z
- Updated: 2026-09-21T10:46:10Z
- Target Window: cross-component discovery complete; implementation not started
- Related Program/Initiative: Spellbook registration, Bind admission and Spell lifecycle

## Current Authorization
Discovery authorized on 2026-09-21. The owner selected Spellbook-level pre/activation/post bind hooks,
with activation receiving the Spell context, and requested a verdict on lesser-conduit binding.
Active task: tickets/tasks/2026-09-21_investigate_bind_lifecycle_hooks_task.md. No runtime hook
implementation or generated asset changes are authorized in this discovery tranche.
The owner's follow-up explicitly expands discovery to Crystallizer and every affected consumer.
The impact map below records required changes, existing machinery to retain and conditional work.

## Problem / Opportunity
Applications need to extend registration itself: check an incoming reference using user-added
strategies, modify the resulting Spell during bind activation, and run post-bind hooks after binding.
These operations should share the canonical binding flow so callers do not have to reproduce its
profiling, identity, registration, compilation or publication responsibilities.

## Owner-Requested Stages

| Stage | Intended subject | Requested purpose |
| --- | --- | --- |
| Pre-bind | The incoming reference and relevant binding context | Allow strategies to be added to check whether the reference may be bound |
| Bind activation | The newly constructed Spell, passed as a callback parameter | Mirror Meld activation for the newly created Spell definition |
| Post-bind | The completed binding and final Spell/result | Allow follow-up hooks after binding succeeds |

The activation subject is the **Spell definition**, not a resolved application instance. Pre-bind
checks should work with supported class, callable and existing-object references without constructing
them merely to perform a check.

Owner clarification (2026-09-21): register these hooks directly on Spellbook and associate them with
its Bind component. Activation receives the actual Spell when it is created. This does not require
a separate mutation whitelist, field-edit permission framework or automatic rehashing system.

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
- EXECUTION_BOUNDARY: Bind-time strategy/hook registration, execution ordering, actual Spell callbacks,
  coherent finalization/publication and related tests/docs. Existing instance-creation hooks remain separate.
- DEPENDENCIES: Existing Bind/Spellbook pipeline, Spell identity/state, configuration and hook patterns,
  staged/active bind paths, Crystallizer/MR/Nexus confirmation points and transaction/cleanup rules.
- EXIT_GATE: All three approved stages are usable, callback/strategy failures have defined outcomes,
  identity/publication remains coherent and compatibility/regression evidence is accepted.
- FAILURE_ESCALATION: Resolve callback ordering/failure semantics before coding; preserve existing
  identity, validation and ownership machinery without introducing a separate mutation framework.

## Goals (Outcomes)
- Register and compose pre-bind reference-checking strategies in a defined order.
- Reject invalid references before publishing a new binding, with actionable strategy diagnostics.
- Expose a bind-activation callback receiving the newly created Spell, like Meld instance activation.
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
- from_state: in_progress
- to_state: in_progress
- transition_reason: Owner expanded discovery to all affected owners; the full impact map is recorded.

## Proposed Lifecycle to Validate

```text
incoming reference + bind options
    -> configured pre-bind reference strategies
    -> construct/prepare the Spell
    -> bind-activation hooks receive that newly created Spell
    -> normal profile completion, registration and publication
    -> post-bind hooks receive the completed binding
```

Bind currently computes a fingerprint before constructing the Spell. The activation seam is the
newly created Spell, before it is returned to Spellbook for registration/publication. Mirror the
existing activation callback model; do not redesign identity merely to introduce the callback.

Evidence:
- `src/melder/aether/spellbook/bind/bind.py:433-551`
- `src/melder/aether/spellbook/spellbook.py:5190-5310`

## Requirements
- Define strategy registration, ordering, duplicate/removal behavior and the pre-bind result contract.
  Decide whether rejection is an explicit result or an exception; do not silently coerce truthy values.
- Give pre-bind strategies the actual reference and sufficient context to check it. Reference
  replacement/transformation is not part of the requested checking capability unless later approved.
- Pass the actual newly constructed Spell into activation callbacks. Do not substitute a restricted
  data copy or introduce a field-edit whitelist; user callback behavior follows the existing Spell API.
- Keep native fingerprint/key rules unchanged. Activation runs before normal profile completion and
  publication; consumers use the resulting Spell through their existing contracts. Passing the real
  Spell does not promise automatic rehashing or replay of arbitrary callback effects.
- Specify post-bind timing and payload, including whether it occurs inside or after the transaction.
  State clearly what remains committed if a post-bind hook raises; do not pretend external side effects
  can always be rolled back.
- Define failure behavior at each phase: later callbacks, partial Spell disposal, lookup claims,
  registration visibility and emitted records. Failed pre-bind checks must not publish a binding.
- Preserve native validation and existing creation hooks; activating a Spell for registration must
  not invoke the application constructor or its instance-activation hook.
- Make active versus inactive binding, pre/post-conjure binding and all wrappers consistent. Define
  whether lifecycle stages rerun when restore/graft re-enters bind and how duplicate effects are avoided.
- Register on Spellbook and store callbacks on its owned Bind. Preserve book isolation, including
  books sharing a configuration. Define registration updates separately from configuration freeze.
- Establish callback ownership, cleanup, reentrancy and concurrency contracts from the existing locks
  and transaction model. Document whether binding recursively from a hook is supported or refused.
- Keep the unconfigured path small. Measure any performance claim; do not add per-Meld checks for a
  feature that belongs to binding.

## Cross-Component Impact Map (2026-09-21)

This is a source-backed implementation map, not a claim that hooks are already implemented.
The core work is in Spellbook, Bind and the book-twin producer. The existing record/storage/readers
already carry arbitrary hook-name strings. Compiler, Nexus and MutationResearch need ordering and
compatibility checks rather than a second hook registry.

| Area | Required work or disposition |
| --- | --- |
| Spellbook public setup | Add ordered pre/activation/post registration directly on the book; validate callback inputs and document updates, scope and errors. |
| Owned Bind | Initialize callback storage; run pre on the original reference and activation on the actual new Spell; release stored references during cleanup. |
| Active binding | Signal post after this binding's normal registration/publication path; keep the existing spell_id return and transaction admission. |
| Inactive binding | Use the same construction hooks; signal post after parking/folding into the final target index. Later notch is not another bind activation. |
| Spell lifecycle | Preserve native identity and profile contracts; handle unpublished allocation teardown on activation failure without registered-world removal. |
| Existing creation hooks | Keep their current bind kwargs and Meld execution. Define/test precedence when a bind activation also configures Spell creation hooks. |
| Book twin producer | Pass value-only bind-hook presence from Book/Bind into SpellbookCrystal emission, including origin-bearing re-freeze. |
| Crystal record/storage | Keep generic hook_names, checkpoint, formation, cache and external emission payloads; add transport and compatibility regressions. |
| Restore/preflight | Existing generic hook shortfalls remain; fresh-book callback reattachment is a separate optional loader addition before replayed binds. |
| Graft | Receiving live book hooks participate through normal bind/bind_inactive. Source callbacks are not copied by an index graft. |
| Fluent/decorator/scan/Conduit | Reuse canonical Book/Bind dispatch; avoid duplicate callbacks or new per-call forwarding arguments. Lesser bind doors remain disabled. |
| Preset books/upgrade | Fresh Book means fresh Bind and empty callback storage by default; shared configuration must not imply shared callbacks. |
| Transactions/concurrency | Preserve bind admission, nested sessions and structural staging. Specify callback failure, reentrancy and registration-update ordering. |
| Compiler/Creations/cache | Preserve normal completion, staged validation, existing-object registration and automatic cache behavior. Add no new per-Meld feature checks. |
| Nexus/MR | Preserve active/staged publication order and current native payloads; no independent callback storage or arbitrary metadata persistence promise. |
| Documentation/build assets | Update public contracts, component/graph descriptions, examples and release draft after implementation; regenerate assets after owner code review. |

### Crystallizer: concrete additions and boundaries

1. **Producer handoff is required.** SpellbookConfiguration currently creates the book twin and
   enumerates only its conduit and meld hook maps. Book-owned bind callbacks are invisible there.
   Carry stage-presence strings, provisionally `bind:pre`, `bind:activation`, `bind:post`, from the
   actual Book/Bind owner. Do not put the callbacks into configuration merely to reuse its emitter.
   An optional value-only argument through the existing origin-bearing freeze/emission path is one
   bounded implementation; a Book-owned emission helper is another. Keep one authoritative producer.
2. **Cover both freeze paths and updates.** Standalone configuration.finalize has no book identity;
   conjure calls freeze with origin identity even when already frozen. Both origin paths need markers.
   If live hook registration/removal is allowed after conjure, refresh the complete book twin when
   recording. Emitting only changed markers would replace and lose the rest of the book snapshot.
   If updates are restricted, document the gate instead. Build no payload while recording is inactive
   or the frame is automatic, and do not introduce a world sweep at Crystallizer activation.
3. **Persist presence, not callback code.** SpellbookCrystal already accepts and describes arbitrary
   hook_names. SpellCrystal captures fixed native binding policy/source data, not arbitrary metadata,
   tags, callbacks or callback side effects. Activation precedes existing capture; there is no new
   guarantee that every in-memory customization survives restore.
4. **Keep current restore honesty.** ConfigurationLossStrategy reports each marker as informational
   code participation. RestoreEngine reports `hook_requires_code_participation` for every recorded
   name. Ordinary restore constructs a fresh Book, immediately replays active binds, conjures and then
   replays staged binds. It does not reattach callback functions today. Retaining that behavior is
   the recommended bounded feature scope, with explicit documentation and tests.
5. **If replaying callbacks is later required, add an explicit pre-replay seam.** Application code
   must configure the newly built Book after construction and before the first active bind. Thread
   that participation through loader admission/restore and its public entry points; use restored
   identity mappings and report unresolved markers honestly. This is conditional extra work, not
   something the generic marker field or current loader already provides. Callback side effects
   remain outside the loader's ability to undo arbitrary external actions.
6. **Graft is different.** GraftRunner calls public bind verbs on a live receiving book, so its
   configured callbacks will run on actual newly bound members. Resident/unhydratable skips do not
   bind. The index graft contains member custody and selection, not source-book callbacks. A graft
   is not automatically atomic across members; a later callback failure must report partial work
   consistently with that existing contract.
7. **No new serialization format is indicated for stage markers alone.** PersistenceProfile captures
   book.describe in checkpoint segments and conduit/frame formations. PersistenceCrystal forwards
   captured payloads; JSON cache and the external emission envelope retain them. RecordVersion 2.0.0
   already has the generic field: adding marker strings does not introduce an incompatible schema.
   Reconsider versioning only if implementation adds record structure or changes replay policy.

Evidence/read targets:
- `src/melder/aether/spellbook/spellbook.py:5722-5790`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:265-403`
- `src/melder/crystallizer/crystals/spellbook_crystal.py:91-142`
- `src/melder/crystallizer/crystals/spellbook_crystal.py:213-264`
- `src/melder/crystallizer/crystals/spell_crystal.py:265-299`
- `src/melder/crystallizer/crystals/spell_crystal.py:1071-1170`
- `src/melder/crystallizer/crystal_analysis/preflight/configuration_loss_strategy.py:69-119`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1750-2023`
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py:229-573`
- `src/melder/crystallizer/persistence/persistence_profile.py:833-903`
- `src/melder/crystallizer/persistence/persistence_profile.py:1028-1306`
- `src/melder/crystallizer/persistence/persistence_profile.py:1380-1428`
- `src/melder/crystallizer/persistence/persistence_crystal.py:345-451`
- `src/melder/crystallizer/persistence/record_version.py:17-79`
- `src/melder/crystallizer/asset_management/crystallizer_cache.py:127-175`
- `src/melder/crystallizer/asset_management/crystallizer_cache.py:266-302`
- `src/melder/crystallizer/asset_management/crystallizer_cache.py:374-479`
- `src/melder/crystallizer/asset_management/asset_management_system.py:362-448`
- `src/melder/crystallizer/asset_management/asset_management_system.py:994-1043`
- `src/melder/crystallizer/crystallizer.py:605-694`
- `src/melder/crystallizer/crystallizer.py:1522-1575`

### Other lifecycle details the implementation must carry

- **Cleanup needs actual wiring.** Bind.cleanup already has an owned-helper teardown, but
  Spellbook._cleanup_core currently only deletes `_bind`; it does not call its cleanup method.
  Once Bind stores user callbacks, Book teardown must explicitly retire that owner. Release callback
  references; do not call cleanup on user-supplied callback objects as if Melder owned them.
- **Unpublished failure is a separate teardown state.** Spell.cleanup normally delegates to
  cleanup_and_remove_spell unless `_spellbook_cleanup` selects local teardown. That public removal
  path requires a registered local Spell. An activation exception occurs before registration, so
  explicitly retire its unpublished Spell/profile/compiler artifacts and newly allocated SpellIndex
  without emitting removal of a resident binding or touching a target sibling index.
- **Activation precedes collision checks.** Bind returns the new Spell before Spellbook's duplicate
  and frame lookup claims. A later collision can follow a successful activation. Pre and activation
  are per attempted construction; post is only reached after registration succeeds. Retrying bind
  may rerun callbacks. Do not advertise exactly-once external effects across retries.
- **Explicit creation-hook kwargs retain precedence.** Book._add_hooks_to_spell runs after Bind
  returns. Spell._set_hooks replaces supplied lists and leaves None lists alone. Preserve and test
  that order rather than silently losing it when adding registration activation.
- **Post-bind is not automatically post-commit.** The active bind stages structural work for its
  transaction. Nested binds join an outer session; the outer end may still validate or abort.
  Recommended scope: post observes this binding's completed registration inside its existing
  envelope, with no promise of outer commit. A callback error propagates with phase/cause, skips later
  callbacks and follows existing transaction failure handling; it is not automatic rollback of all
  maps, emitted records or external effects. If strict commit notification is desired, explicitly
  move it to the session hook pipeline and define deferred ordering instead.
- **Preserve actual transaction failure detection.** end_transaction_for_identity derives success
  from sys.exc_info and ABORT_ONLY. The Book not passing its local success variable to that method
  is not evidence of a missing failure path. Do not repair the mediator speculatively for this epic.
- **Use existing concurrency owners.** Bind uses RLock and Book has separate registration/map locks.
  Callbacks execute synchronously in the admitted bind path. Test finite nested binds and concurrent
  hook registration/cleanup under the chosen contract; preserve lock order. If current-call callback
  snapshots are needed because registration can mutate during invocation, document that correctness
  reason. Do not add asynchronous dispatch or a process-global synchronization framework.
- **New books stay isolated.** create_new_preset_spellbook copies frame name and configuration only.
  A lesser borrows definitions and cannot bind. Upgrade creates a new Book/Bind; callback inheritance
  is not implied by shared configuration or by preserved creations. Recommend empty hooks on that
  new book unless explicitly configured.
- **Downstream publication remains native.** Activation precedes profile completion, structural
  staging, crystal capture, MR world entry and Nexus publication. Staged members remain parked and
  do not gain active Nexus publication simply because an activation hook ran. Current Nexus profile
  payloads and SpellCrystal fields do not promise arbitrary Spell.metadata/tag export.

Evidence/read targets:
- `src/melder/aether/spellbook/bind/bind.py:183-231`
- `src/melder/aether/spellbook/bind/bind.py:411-551`
- `src/melder/aether/spellbook/spell.py:512-614`
- `src/melder/aether/spellbook/spell.py:637-680`
- `src/melder/aether/spellbook/spellbook.py:358-535`
- `src/melder/aether/spellbook/spellbook.py:581-698`
- `src/melder/aether/spellbook/spellbook.py:704-734`
- `src/melder/aether/spellbook/spellbook.py:4371-4528`
- `src/melder/aether/spellbook/spellbook.py:4530-4676`
- `src/melder/aether/spellbook/spellbook.py:4753-5002`
- `src/melder/aether/spellbook/spellbook.py:5132-5310`
- `src/melder/aether/spellbook/spellbook.py:5380-5428`
- `src/melder/aether/spellbook/spellbook.py:5913-5965`
- `src/melder/aether/spellbook/spellbook.py:6240-6278`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:694-747`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:409-527`
- `src/melder/nexus/frame_descriptor_manager.py:498-571`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/general_profile.py:118-138`
- `src/melder/mutation_research/mutation_research.py:1234-1319`

### Implementation sequence and re-entry scope

1. **Book/Bind lifecycle:** finalize the small registration API and error contract; add storage,
   callbacks and deterministic cleanup. Read Binding Pipeline and Spellbook Core component slices,
   then Bind, Spell construction/cleanup and both Book bind bodies. Mirror Meld's synchronous callback
   invocation and HookExecutionError reporting without making Bind depend on Meld execution.
2. **Recording and replay compatibility:** add the value-only marker handoff and the chosen update
   rule. Read configuration freeze, SpellbookCrystal, capture/codecs, preflight, restore and graft
   references above. Preserve report-only full restore unless the owner selects the extra seam.
3. **Entry-point and publication qualification:** cover fluent/scan/decorator/normal Conduit,
   active/staged, pre/post-conjure, shared-config/preset books, failed/retried/nested binds, and
   optional Nexus/MR/Crystallizer combinations. Read those wrappers and their existing tests before
   choosing exact test placement. Lesser binding and existing-object uniqueness remain unchanged.
4. **Docs and delivery:** describe setup, timing, errors and persistence limits in public examples,
   source docstrings and src_components/src_architecture. Update graph descriptors/indexes and release
   notes, then regenerate packaged assets only after the owner's implementation review/approval.

Before runtime implementation, create the selected bounded tasks and required architecture/component
patch contracts. This discovery pass only updates the research records.

### Required regression matrix

| Boundary | Observable contract to prove |
| --- | --- |
| Empty setup | Existing bind IDs, outputs, native refusals and Meld behavior remain compatible. |
| Callback stages | Ordered reference/new-Spell/completed-Spell subjects; return values do not replace the target; pre rejection is explicit. |
| Reference families | Class, callable, existing unique object and resolvable=False definition; activation never constructs an application object. |
| Failure/retry | Each phase can raise; later callbacks stop; unpublished allocations retire; collision does not emit post; retry behavior is explicit. |
| Existing hooks | Original creation hooks still run at Meld; explicit hook kwargs preserve documented replacement precedence. |
| Registration forms | Direct, fluent, scanner/decorator, normal Conduit and bind_inactive reach each phase once; notch is not fresh activation. |
| Scope/ownership | Two books sharing configuration remain isolated; preset/upgrade starts with chosen policy; lesser bind refusals stay intact. |
| Transactions | Standalone and nested bind completion, failed outer validation, finite reentrancy and concurrent work release admission/locks correctly. |
| Cleanup | Book invokes Bind teardown; callbacks release; a captured failed activation Spell is cleaned; unrelated registrations survive. |
| Recording | Nonempty bind stages coexist with meld/conduit markers; fresh freeze and origin re-freeze work; chosen late-update/removal policy is recorded. |
| Persistence | Markers survive replace-on-emit, checkpoint JSON roundtrip, frame/conduit formations and emission tap; legacy absent/empty names load. |
| Restore/graft | Full restore reports callback shortfalls; receiving-book graft hooks run only for new members; source hooks are not invented. |
| Publication | Activation effects within existing native contracts reach capture and publishers in order; staged members retain staged semantics. |
| Performance | Measure ordinary bind with no bind hooks; no new per-Meld checks, callback hashing, cache scanner or graph-wide update. |

These are future implementation tests. The existing 13 passing checks characterize today's bind and
Meld behavior; the expanded persistence map above is source-reviewed, not a completed feature test run.

### Documentation contradictions to correct with delivery

The current component material includes a stale Crystallizer `_catch_up_live_world` claim; source
activation only catches up Aether root policy. It also describes hook-name admission more loosely
than the source's explicit supported-name check. Do not design against those statements. Correct
the affected paragraphs and generated documentation when delivering the hook feature; no broad
component audit is part of this discovery.

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
- [x] Trace registration/configuration/identity boundaries and settle direct registration/activation context.
- [x] Map recording, persistence, restore/graft, cleanup, copying, transactions and publication impact.
- [ ] Create approved stories/tasks and patch contracts with focused failing regressions.
- [ ] Implement pre-bind strategies, Spell activation customization and post-bind callbacks.
- [ ] Qualify failure, identity, wrapper, replay and existing-hook compatibility; update docs/assets.

## Stories (Proposed; Not Yet Created)
- [ ] Define strategy registration, lifecycle payloads, ordering and errors.
- [ ] Add pre-bind reference-checking strategies at the agreed admission point.
- [ ] Invoke bind activation with the newly constructed Spell before normal registration completes.
- [ ] Add post-bind hooks and qualify the complete lifecycle across entry points and replay.

## Acceptance Criteria
- A user can add multiple reference-checking strategies and observe the documented execution order.
- A rejected reference leaves no successfully published binding or success post-bind notification.
- Activation receives the actual newly constructed Spell before profile completion/publication,
  preserving the native Spell API and existing fingerprint rules without a new mutation framework.
- Post-bind hooks observe the documented registration state once per completed bind operation;
  the contract explicitly distinguishes that notification from an outer transaction commit.
- Failure, cleanup and retry behavior match the approved contract without orphaned local state.
- Existing creation hooks retain their current execution timing and newly created-instance subject.
- Direct/fluent/decorator/scan/Conduit and active/inactive/replay behavior follow the explicit matrix.
- Ordinary unconfigured binding and Meld behavior retain compatibility.

## Validation / Test Approach
Discovery: 13 current-runtime characterization/integration checks passed; scoped lint passed.
The future bind-hook implementation itself is not written or tested yet.

Use the Required regression matrix above. Assert final state and user-visible behavior rather than
only callback counts or private fields. No field-by-field mutation enforcement is being introduced.

## Risks / Mitigations
- Private identity changes after hashing can violate existing contracts: retain the native Spell API
  and fingerprint rules; adding activation does not add automatic rehashing.
- Existing hook names look similar but run during meld: use explicit bind-time vocabulary.
- Publication before activation finishes can expose conflicting state: trace every confirmation sink.
- Arbitrary user callbacks inside locks can re-enter binding: define supported behavior from source.

## Open Questions
- Resolved: hooks are registered directly on Spellbook and associated with its Bind component.
- What are their exact signatures, result types and failure contracts?
- Resolved: activation receives the actual newly constructed Spell; no separate field-edit framework.
- When does post-bind run relative to commit, structural work and passive publication?
- Resolved by source: bind_inactive shares construction, wrappers route to bind, graft uses a live
  receiving book, and full restore constructs fresh books without callback reattachment.
- Choose registration append/replacement/removal and late-update behavior. If updates are allowed,
  include current marker re-emission and current-call iteration semantics.
- Recommended: keep full restore's existing code-participation shortfalls. Automatic callback
  reattachment requires the explicit pre-replay extension described above and owner selection.

## Decision Log
- Owner requested pre-bind reference strategies, Spell-modifying activation hooks and post-bind hooks.
- Existing pre/activation/post creation hooks must remain behaviorally distinct.
- Owner clarified activation receives the real Spell upon creation, mirroring Meld activation.
- Hook setup is directly on Spellbook, associated with Bind; the configuration-registry proposal
  was superseded. Ordinary binding already works with default configuration before explicit freeze.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/bind_hooks_discovery_20260921/plan.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: future accepted feature closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: settle callback update and post-bind failure timing before implementation.

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

- DATETIME: 2026-09-21T00:58:00Z
  TYPE: DECISION
  CLAIM: Owner selected a direct activation-callback model: register on Spellbook, associate with
    Bind, and pass the newly created Spell as the activation parameter. Discovery confirms both
    lesser bind doors are disabled; a lesser can resolve later owner registrations. Ordinary bind
    works before explicit configuration/freeze; configure-first is a dynamic Crystallizer conjure gate.
  EVIDENCE:
  - tickets/tasks/2026-09-21_investigate_bind_lifecycle_hooks_task.md
  - artifacts/bind_hooks_discovery_20260921/plan.md
  - artifacts/bind_hooks_discovery_20260921/characterization_final.log:1-2
  IMPACT: A bounded implementation can reuse the existing Book/Bind ownership and hook error
    pattern. No field whitelist, rehashing framework, new scope or per-Meld feature work is required.
  NEXT: Owner reviews the direct callback plan before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T10:46:10Z
  TYPE: FACT
  CLAIM: Expanded discovery now separates required Book/Bind and book-twin producer edits from
    generic persistence consumers and conditional restore reattachment. The impact map includes
    freeze/re-freeze and marker updates, formations/cache/tap, full restore versus live graft,
    unpublished teardown, Book-to-Bind cleanup, nested transaction timing, wrappers, preset/upgrade,
    compiler/Nexus/MR publication, future regressions and per-tranche reading requirements.
  EVIDENCE:
  - tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md:148-348
  - tickets/tasks/2026-09-21_investigate_bind_lifecycle_hooks_task.md
  IMPACT: The feature has a concrete cross-component implementation boundary. Keep actual-Spell
    activation and direct Book setup; no new serialization, identity-rehash or mutation framework.
    The broader impact review is source-based; future bind-hook tests are explicitly not yet run.
  NEXT: Owner reviews the plan and selects the runtime implementation tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Feature implementation and validation delivered in a later authorized pass.
- [ ] Owner accepts the final callback timing, update and failure contracts.

## Noting Behavior
Record shared lifecycle decisions here; future child tasks own source traces and verification evidence.

## Context / Handoff Summary
Expanded discovery is complete. Start at Cross-Component Impact Map and its Crystallizer/lifecycle
subsections above; they supersede the initial core-only plan. Direct Book setup and actual-new-Spell
activation are owner-settled. Do not reopen a field-edit/rehash framework or move registration to config.

Required edits: Book/Bind callbacks and cleanup, active/inactive post notification, and value-only
bind-stage markers in the existing book emitter. Generic crystals, record storage, preflight and
restore already transport/report arbitrary names. Full restore has no callback reattachment seam;
recommend retaining honest shortfalls. Live receiving-book graft uses its own hooks. Preserve native
compiler, cache, Nexus and MR flows. The regression matrix and re-entry references are above.

13 earlier current-runtime checks and lint passed. This expanded review added source findings, not
runtime features or new test execution. Lesser binding remains disabled; ordinary Book.bind already
works before explicit configuration. No production hook feature or asset generation has been started.
