# Task: Investigate runtime hook standardization across subsystems

## Metadata
- Task ID: TASK-2026-09-21-investigate-runtime-hook-clearing
- Epic: EPIC-2026-09-21-runtime-hook-lifecycle-and-adjustment
- Status: backlog
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-21T11:45:14Z
- Updated: 2026-09-22T09:11:27Z

## Objective
Parked with the broad epic at the owner's request. Active discovery now belongs to
`tickets/tasks/2026-09-22_investigate_pooled_conduit_hook_reset_task.md`.

After the bind-hook implementation, investigate how existing Conduit/Meld hook systems can safely
support clearing and re-registration. Produce a source-backed proposal before changing their APIs.
Include per-Spell creation hooks and the owner's local-versus-lineage recollection. Establish actual
behavior before deciding how runtime adjustment should work.
Owner expanded discovery to all applicable hook systems for one management style. Trace RiftSpace,
event/memory subscriptions, change-control/session hooks and remaining extension seams; classify
callback registries separately from infrastructure and strategy overrides before proposing APIs.

## State Transition Event
- from_state: review
- to_state: backlog
- transition_reason: Owner selected the narrower pooled-hook reset investigation and backlogged the broad epic.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested this investigation after bind hooks are finished.
- EXECUTION_BOUNDARY: Read current configuration, shared/local hook ownership, dispatch, inheritance,
  cleanup and recording; characterize unclear behavior; record a bounded design. No implementation.
- DEPENDENCIES: Bind hooks source is complete and awaiting owner review; asset generation remains held.
- EXIT_GATE: Shared/local clearing semantics, re-registration, concurrency and persistence impact
  are mapped with exact changes and meaningful regression requirements.
- FAILURE_ESCALATION: Keep unsupported claims UNKNOWN; ask about material inherited-hook semantics
  after tracing what the source currently does.

## Known Starting Point
- SpellbookConfiguration hook registration is additive and rejects modification after freeze.
- Conduit.register_conduit_hooks adds local conduit and Meld hook updates; it does not clear.
- Meld.set_meld_hooks supports reference storage, local copy/merge and overwrite internally.
- Spell._set_hooks internally replaces only supplied creation-hook lists and bumps the door epoch.
- There is no matching public clear method on these existing systems. Bind's new clear API is owned
  separately and does not change any of them.

## Required Reading
Use current component indexes, then read the complete relevant source call paths:
- src/melder/aether/spellbook/configuration/spellbook_configuration.py: hook maps/freeze/getters.
- src/melder/aether/conduit/conduit.py: initialization, local hook registration, chain collection,
  lesser inheritance, pooling/upgrade and teardown.
- src/melder/aether/conduit/meld/meld.py: set_meld_hooks and dispatch.
- src/melder/aether/spellbook/spell.py: creation-hook lists, door invalidation and cleanup.
- src/melder/aether/spellbook/spellbook_creation_system.py: initial hook wiring.
- Existing Conduit/Meld/creation-hook tests and current Crystallizer marker producers/readers.

## Steps / Checklist
- [x] Trace each registry's actual owner and shared/local reference behavior.
- [x] Record clear/reset choices while preserving the owner's accepted local/lineage model.
- [x] Map in-flight calls, re-registration, pooling/upgrade, cleanup, cache and recording.
- [x] Record the findings, proposed stories and future regressions in the new epic.
- [x] Complete the continued event/signature, reuse, transaction, reset and graduation source trace.
- [x] Trace RiftSpace action/category hooks, event/memory subscriptions and their dispatch wrappers.
- [x] Trace change-control manager/orchestrator/session hooks and transaction strategy boundaries.
- [x] Classify remaining callback, persistence, weak-reference and import-hook seams.
- [x] Record one source-backed operation matrix, common API proposal and staged migration scope.

## Validation
16 current-behavior probes passed in 4.83 seconds before the documentation-only instruction.
Scoped Ruff passed. No production changes or generation. Graduation wiring was verified in source;
an additional runtime graduation probe was not run after the owner stopped code/test changes.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/runtime_hook_discovery_20260921/
  - artifacts/runtime_hook_discovery_20260921/hook_trace.md
  - artifacts/runtime_hook_discovery_20260921/system_hook_standardization.md
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Notes
- DATETIME: 2026-09-21T11:45:14Z
  TYPE: DECISION
  CLAIM: Owner approved bind clearing and requested separate investigation of the more complex
    Conduit/Meld systems after bind hooks are finished. Preserve the four distinct starting surfaces.
  EVIDENCE:
  - Owner's follow-up after approving clear_bind_hooks.
  - src/melder/aether/conduit/conduit.py:1656-1710
  - src/melder/aether/conduit/meld/meld.py:1264-1307
  - src/melder/aether/spellbook/spell.py:638-682
  IMPACT: This ticket records the next lane without silently changing existing runtime hooks.
  NEXT: Trace initialization, inheritance and local/effective hook chains through their real owners.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T21:52:43Z
  TYPE: PLAN
  CLAIM: Owner selected investigation of Conduit, Meld and per-Spell hooks, recalling local and
    lineage modes and wanting runtime adjustment. Trace configuration-to-owner wiring, local versus
    borrowed maps, lessers/spaces/pools/upgrades, dispatch and compiled-hook consumers before proposing
    clear/re-register APIs. Bind hooks remain complete with 729 passing selected tests; assets held.
  EVIDENCE:
  - Owner's current local/lineage and adjustable-hook investigation request.
  - tickets/tasks/2026-09-21_implement_bind_lifecycle_hooks_task.md
  IMPACT: Discovery and bounded characterization are authorized; do not implement runtime-hook APIs.
  NEXT: Read complete Conduit/Meld hook initialization, sharing and dispatch call paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T21:58:08Z
  TYPE: FACT
  CLAIM: Conduit keeps a lineage table and a separate local lifecycle table. For a given event,
    a nonempty local list wins and suppresses the shared list; the dispatcher docstring claiming
    shared-then-local order is stale. Local Meld registration instead copies the current effective
    table and appends callbacks into that copy. Conduit retains its original _meld_hooks lineage
    table separately, and lesser construction uses the root's seed tables. SpellSpace construction
    borrows the current ConduitMeld map. Lesser pool return clears local Conduit hooks but does not
    reset the Meld hook map; SpellSpace reuse keeps collaborators. Runtime probes must qualify these
    reference/timing differences before a clearing API is selected.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:334-363
  - src/melder/aether/conduit/conduit.py:1657-1711
  - src/melder/aether/conduit/conduit.py:1779-1841
  - src/melder/aether/conduit/conduit.py:563-587
  - src/melder/aether/conduit/conduit.py:2228-2382
  - src/melder/aether/conduit/conduit.py:6418-6468
  - src/melder/aether/conduit/meld/meld.py:1264-1329
  - src/melder/aether/conduit/spell_space/spell_space.py:166-208
  IMPACT: Clearing a Conduit-local lifecycle override would expose its inherited handlers again.
    Meld has already flattened base/local callbacks, so selective local clearing needs provenance.
    Existing scopes and pooled objects may retain different map references after local updates.
  NEXT: Trace pool acquisition/reset and upgrade, then characterize scope-local callback visibility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:06:28Z
  TYPE: FACT
  CLAIM: Pools start empty and reuse the same objects; neither SpellSpace acquisition nor its
    pool cleanup refreshes the Meld hook reference. Lesser return clears only local lifecycle hooks.
    Spell._set_hooks replaces supplied lists and bumps _door_epoch; direct Conduit/Space meld reads
    target Spell hooks live and checks that epoch on warm doors. Callback dispatch surrounds the
    selected root execution; dependency behavior still needs a probe. Upgrade keeps existing hook
    references; it calls create_new_preset_spellbook without adopting the returned Book. This corrects
    the earlier inference that upgrade necessarily adopts a fresh, hook-empty Book.
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:114-195
  - src/melder/aether/conduit/conduit_pool.py:100-161
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:148-279
  - src/melder/aether/conduit/spell_space/spell_space.py:343-367
  - src/melder/aether/conduit/conduit.py:1960-2140
  - src/melder/aether/spellbook/spellbook.py:6386-6423
  - src/melder/aether/spellbook/spell.py:638-682
  - src/melder/aether/conduit/meld/conduit_meld.py:369-576
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:237-309
  IMPACT: A correct adjustment API must define retained-scope/pool behavior and root ownership;
    clearing lists alone is insufficient. No runtime repair is authorized in this discovery.
  NEXT: Run bounded current-behavior probes for sharing, pool reuse, warm Spell updates and dependencies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:13:46Z
  TYPE: MEASURE
  CLAIM: Thirteen current-behavior probes pass. Confirmed lifecycle local shadow/fallback; Meld
    copied merge and lost later seed updates; local Meld callbacks surviving lesser pool reuse;
    old/recycled SpellSpaces missing owner-local map replacements; partial mixed registration on
    invalid input; publicly rejected on_meld_activation despite a working internal dispatch branch;
    lifecycle-error suppression versus Meld error propagation; live per-Spell set/clear on warm
    root/Space paths without replacing compiled contexts; and root-only creation-hook dispatch in
    the tested dependency graph. Clearing Spell hooks during pre also suppresses that call's post.
  EVIDENCE:
  - tests/experimentation/test_runtime_hook_discovery_experiment.py
  - artifacts/runtime_hook_discovery_20260921/characterization.log:1-2
  - artifacts/runtime_hook_discovery_20260921/characterization.xml
  IMPACT: Runtime adjustment is feasible but must settle shared/local provenance, pooled-lease
    reset and in-flight semantics. Existing selected-Spell epoch machinery already supports warm
    updates; dependency-hook execution is a separate behavior decision, not just another setter.
  NEXT: Verify persistence and upgrade ownership, then write the source-backed proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:28:07Z
  TYPE: DECISION
  CLAIM: Owner explicitly preserves the current local/lineage model, highlights pooled-map reset
    and graduation bind-hook ownership, and restricts further work to documentation in a new epic.
    Created EPIC-2026-09-21-runtime-hook-lifecycle-and-adjustment with those priorities, reading
    requirements, source evidence, proposed stories and future corrective tests. The final existing
    characterization selection passed 16 cases; it also confirms per-Spell version-wide direct-call
    behavior, permanent-only lesser cleanup events and missing runtime-local/Spell hook markers.
  EVIDENCE:
  - Owner's model-preservation, graduation and documentation-only instructions.
  - tickets/epics/backlog/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md
  - artifacts/runtime_hook_discovery_20260921/characterization_final.log:1-2
  - artifacts/runtime_hook_discovery_20260921/characterization_final.xml
  - artifacts/runtime_hook_discovery_20260921/lint.log:1-1
  IMPACT: No further code/test changes. Preserve current composition and active-scope behavior;
    repair pool boundaries and establish full new-Book adoption only in a later approved story.
  NEXT: Owner reviews the new epic and selects the next bounded story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:40:35Z
  TYPE: PLAN
  CLAIM: Owner requested continued tracing of all hooks. Complete conjure, link/contract dispatch,
    reuse paths and graduation reference ownership, then consolidate the inventory in the epic.
    Existing certification and role continue; no runtime/test edits or asset generation authorized.
  EVIDENCE:
  - Owner's latest request to keep investigating and trace all hooks.
  - tickets/epics/backlog/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md:13-20
  IMPACT: This resumes discovery without treating implementation-review approval as granted.
  NEXT: Trace conjure hook registration and all three dispatch stages through creation completion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:42:00Z
  TYPE: FACT
  CLAIM: Root conjure uses the configuration's Book-keyed Conduit map. Pre-created has no arguments
    and runs after phase preparation but before Conduit construction. Activated receives the new
    Conduit after Book attachment, before define_conduit_into_spells and cached-context hydration.
    Post-created receives it after ownership wiring, cache work, Nexus publication and risk registration.
    Each stage iterates its live callback list and logs/suppresses individual callback exceptions.
    This is a distinct dispatcher from runtime Conduit's local-shadow selection.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:202-288
  - src/melder/aether/spellbook/spellbook_creation_system.py:954-1019
  - src/melder/aether/spellbook/spellbook_creation_system.py:1242-1316
  IMPACT: Activation is an intermediate initialization seam, not proof that all runtime artifacts
    are attached. Future hook adjustments must preserve argument shape, timing and error policy.
  NEXT: Enumerate admitted event names and trace link/contract dispatch on each participant.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-21T22:44:00Z
  TYPE: FACT
  CLAIM: Eleven configuration event names are admitted: two Meld and nine lifecycle/link/contract.
    Runtime Conduit registration uses the same name set, no lock around its two-registry update,
    and local lifecycle shadowing. Config add_hooks applies sequentially, including items within an
    iterable, so a later invalid entry can leave earlier registrations. Link/unlink dispatch occurs
    only on the initiating Conduit after its transaction closes. Single add/remove and bulk contract
    APIs emit once per successful operation/batch with (self, peer), not per affected Spell, within
    their transaction. Index add/remove and remove_root_from_contracts have no direct hook dispatch.
    Peer lookup failure suppresses the advisory contract event. Runtime lifecycle dispatch snapshots
    the chosen event list, unlike root conjure's direct list iteration.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:78-112
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:692-928
  - src/melder/aether/conduit/conduit.py:1657-1840
  - src/melder/aether/conduit/conduit.py:4541-4643
  - src/melder/aether/conduit/conduit.py:4940-5003
  - src/melder/aether/conduit/conduit.py:5439-6136
  - src/melder/aether/conduit/conduit.py:6369-6464
  IMPACT: Event names are not a complete graph mutation stream. Preserve current scope and timing;
    record missing event symmetry and update atomicity as separate decisions, not implicit repairs.
  NEXT: Trace ordinary and reuse-only Meld dispatch, warm paths and hook callback signatures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:46:08Z
  TYPE: FACT
  CLAIM: Both ordinary Meld doors order selected-Spell pre() then Meld pre(Spell), execution,
    selected-Spell activation(instance) then internal Meld activation(Spell, instance) only if created,
    then Spell post() and Meld post(Spell). Reused results still run ordinary pre/post; both
    meld_existing_spell implementations bypass all callbacks. Warm doors read the Meld map live and
    compare the Spell epoch; no new compiled-cache mechanism is needed for hook presence changes.
    Meld dispatch rereads the effective map per stage and iterates the selected live list. There is
    no whole-call hook snapshot as in Bind. Setter copy/replace does not mutate old map references.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:359-751
  - src/melder/aether/conduit/meld/spellspace_meld.py:333-703
  - src/melder/aether/conduit/meld/meld.py:1264-1329
  - src/melder/aether/conduit/meld/meld.py:1660-1716
  IMPACT: Document reuse-only bypass and stage-by-stage visibility explicitly. Clear/reset must
    restore a truly empty effective map for the no-hooks branch and avoid clearing a borrowed map.
  NEXT: Trace bind/per-Spell registration wrappers and pool/graduation ownership end to end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:46:08Z
  TYPE: FACT
  CLAIM: Bind hooks and application-object hooks are distinct end to end. Both Book bind paths
    capture immutable Bind tuples; pre gets the input reference, activation gets the new unpublished
    Spell before profile completion, and post gets the published/parked Spell after recording.
    Per-bind pre_hooks/activation_hooks/post_hooks are attached later through Book validation and
    Spell._set_hooks. Thus an explicit creation-hook kwarg can replace the same stage set earlier
    by bind activation. SpellBinder with_*_hook(s) only stages those per-Spell creation kwargs.
    Normal-Conduit add/clear-bind facades delegate to the attached Book; the only ownership guard
    there is normal state. Correct Book adoption is therefore essential on graduation.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:257-415
  - src/melder/aether/spellbook/bind/bind.py:636-788
  - src/melder/aether/spellbook/spellbook.py:4962-5089
  - src/melder/aether/spellbook/spellbook.py:5285-5450
  - src/melder/aether/spellbook/spellbook.py:5526-5575
  - src/melder/aether/spellbook/spell.py:638-684
  - src/melder/aether/spellbook/spellbinder.py:696-870
  - src/melder/aether/conduit/conduit.py:3098-3179
  IMPACT: Do not route new clear methods into the wrong registry or describe per-object activation
    as bind activation. Snapshot/error policies differ intentionally between families today.
  NEXT: Finish the pool and graduation reference trace, including child scopes and hard teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:46:08Z
  TYPE: FACT
  CLAIM: Graduation changes normal state and stores but leaves Conduit/ConduitMeld Book aliases,
    seed maps, effective hook maps and existing SpellSpaceMeld references attached to old owners.
    The normal-state bind-hook facade consequently still delegates to the parent Book. Normal
    cleanup calls cleanup on that attached Book. Ward conversion requires zero children, contradicting
    the Conduit docstring's retained-children promise, and clears only its own parent pointer without
    removing the parent's child-map entry. The Conduit state flip precedes that refusal. Parent ward
    cleanup permanently cleans retained child-map entries, so graduation needs ownership qualification
    beyond replacing one Book reference. These are source findings; no new graduation probe ran.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1960-2140
  - src/melder/aether/conduit/conduit.py:3098-3179
  - src/melder/aether/conduit/conduit.py:767-866
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:526-579
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:305-329
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1140-1185
  - src/melder/aether/conduit/meld/meld.py:241-270
  - src/melder/aether/conduit/spell_space/spell_space.py:166-208
  IMPACT: The graduation story must test parent isolation, leaf refusal before mutation, reciprocal
    detachment, Book attachment/map aliases and existing/idle Spaces. Do not promise child migration.
  NEXT: Record pool-reset and hard-cleanup hook boundaries, then verify persistence markers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:46:08Z
  TYPE: FACT
  CLAIM: Lesser acquisition fires the calling parent's lifecycle chain on fresh and recycled shells,
    but new child seed maps come from the lineage root. Pool return clears local lifecycle callbacks
    only after Space and creation disposal. Managed Space recycle and manual cleanup both retain their
    Meld maps; both pool acquisition paths omit refresh. Pool overflow hard-cleans an idle shell after
    its local lifecycle callbacks were cleared. Permanent Conduit cleanup dispatches start before
    _cleaned, complete after core fields are removed, and retains the logger until afterward. Meld
    cleanup drops borrowed maps without clearing them. Space hard cleanup deletes its Meld reference
    without invoking Meld.cleanup; deterministic subordinate teardown deserves a focused future probe.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:564-695
  - src/melder/aether/conduit/conduit.py:2228-2382
  - src/melder/aether/conduit/conduit_pool.py:100-161
  - src/melder/aether/conduit/spell_space/spell_space.py:266-400
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:146-279
  - src/melder/aether/conduit/meld/meld.py:297-362
  IMPACT: Reset repairs must cover both Space acquire paths and must not add disposal to callback
    objects. Cleanup-complete is observational and cannot assume intact Meld/Book/Creations fields.
  NEXT: Trace the exact durable marker producer and restore/preflight behavior for each hook family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:46:08Z
  TYPE: FACT
  CLAIM: Book recording combines configuration event-name keys with nonempty bind-stage markers.
    Preflight emits informational code-participation findings, and restore reports shortfalls without
    reconstructing callbacks. Conduit twins contain no runtime-local hook markers; SpellCrystal has
    no per-Spell creation-hook markers. Existing-object executor returns (instance, False), so normal
    Meld pre/post can observe it but activation does not run. Created/reused flags come from execution
    doors; callback invocation remains in the concrete Meld front door after context execution.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:332-418
  - src/melder/aether/spellbook/spellbook.py:4833-4858
  - src/melder/aether/conduit/conduit.py:422-466
  - src/melder/crystallizer/crystals/spell_crystal.py:1071-1170
  - src/melder/crystallizer/crystals/spellbook_crystal.py:243-264
  - src/melder/crystallizer/crystal_analysis/preflight/configuration_loss_strategy.py:75-120
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1738-1818
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:179-234
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:237-274
  IMPACT: Future runtime controls need explicit marker owners and update emissions; callable replay
    remains application-supplied. Hook-presence fixes must not expand transient persistence scope.
  NEXT: Consolidate the dispatch/ownership inventory and prioritized follow-up boundaries in the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-21T22:51:53Z
  TYPE: FACT
  CLAIM: Public Conduit.meld always uses its own Meld, while SpellSpace.meld uses the Space's Meld.
    An active Space does not redirect a Conduit call into Space hooks. Dynamic Conduit meld holds
    its outer CreationGate ticket across callbacks; direct Space meld has no equivalent outer ticket.
    CreationContext gates its execution only, so Space pre/post callbacks sit outside that inner ticket.
    The complete hook inventory is now recorded; these gate boundaries need preservation/qualification
    if hook updates gain new synchronization. No new concurrency guarantee is asserted.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4051-4199
  - src/melder/aether/conduit/spell_space/spell_space.py:440-495
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:237-274
  - artifacts/runtime_hook_discovery_20260921/hook_trace.md
  IMPACT: A transaction drain must not be assumed to freeze all Space callbacks. Discovery is ready
    for review; implementation remains held, and no tests ran during this continuation.
  NEXT: Owner selects the first repair story, with pool reset recommended before graduation ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:53:54Z
  TYPE: MEASURE
  CLAIM: Documentation review completed. All 54 source citations in hook_trace.md resolve to files
    and in-bounds line ranges; one excessive end line was corrected. Task, epic and artifact/attention
    routing agree on discovery review. Runtime tests: Not run during this documentation-only pass.
  EVIDENCE:
  - artifacts/runtime_hook_discovery_20260921/hook_trace.md
  - attention_board.md:86-86
  - artifact_board.md:67-67
  IMPACT: The trace is ready for re-entry and review. Citation checks establish valid locations;
    behavior claims rely on the source reads, and graduation still needs future runtime reproduction.
  NEXT: Owner selects a repair story; pool-reset work can remain separate from graduation ownership.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-21T23:07:41Z
  TYPE: FACT
  CLAIM: The owner asked whether the trace includes every hook in the system. It does not.
    Additional confirmed surfaces are RiftSpace action/category pre/post hooks, room event/memory
    subscriptions, ChangeControlManager commit/abort hooks, and SyntheticModule import hooks.
    Only their entry surfaces were examined in this follow-up; full lifecycle coverage remains scoped
    to the earlier core binding/resolution/Conduit/Space families. The trace now states this explicitly.
  EVIDENCE:
  - src/melder/nexus/rift/rift_space/rift_space.py:325-409
  - src/melder/nexus/rift/rift_space/rift_space.py:596-727
  - src/melder/nexus/rift/rift_space/event_system/rift_event_system.py:152-199
  - src/melder/nexus/rift/rift_space/memory_system/rift_memory_system.py:340-387
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:481-642
  - src/melder/crystallizer/synthetic_module.py:1298-1340
  IMPACT: Do not interpret the earlier complete trace as a repository-wide inventory or silently add
    unrelated runtime repairs. No runtime/test changes or asset generation occurred.
  NEXT: Discuss the current core epic; a system-wide lifecycle audit would be a separate scope decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T23:28:14Z
  TYPE: DECISION
  CLAIM: Owner requires common hook-management style across subsystems, alongside live clearing,
    re-registration and modification. Recorded a common-contract design step in the epic covering
    names/signatures, registration shape, addressing, returns, mutation rules and documentation.
    Exact APIs remain to be proposed; existing scope ownership stays intact and implementation is held.
  EVIDENCE:
  - Owner's runtime-modification requirement and immediate clarification about standardized style.
  - tickets/epics/backlog/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md
  IMPACT: Adding isolated clear/set methods per subsystem is insufficient. Broader hook families now
    belong in design coverage, while their complete lifecycle audit remains outstanding.
  NEXT: Propose the common hook-management contract and map current APIs onto it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:00:48Z
  TYPE: PLAN
  CLAIM: Owner authorized broader source investigation after requiring both runtime modification
    and consistent API style. Trace each remaining family's registration, dispatch, removal/replacement,
    ownership, concurrency and cleanup. Classify infrastructure seams rather than assuming all
    callable-taking methods are lifecycle subscriptions. Record one common-contract proposal.
  EVIDENCE:
  - Owner's instruction to investigate and understand the systems after the standardization discussion.
  - tickets/epics/backlog/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md
  IMPACT: Broader discovery is active. Runtime/test changes and generated assets remain held.
  NEXT: Read RiftSpace hook registries, action wrappers and event/memory systems end to end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:02:24Z
  TYPE: FACT
  CLAIM: RiftSpace owns ordered per-category/per-action dictionaries addressed by subscription IDs.
    Registration is additive; unregister removes one ID and prunes empty buckets. No replace or
    clear-group API exists. Dispatch snapshots pre under the room lock and post separately at exit,
    then invokes callbacks outside that lock. Category pre precedes action pre; action post precedes
    category post. Pre failure prevents body/post; body failure still reaches post, whose raw exception
    can replace it. Command/codegen hooks wrap RiftGate admission/release; viewer helpers delegate
    through the shared decorator/scope chain. Room cleanup releases registrations, not callback objects.
    Depth is room-wide per category rather than thread-local: overlapping calls can suppress each
    other's top-level hooks. Literal action_name='*' collides with the category marker used by removal.
  EVIDENCE:
  - src/melder/nexus/rift/rift_space/rift_space.py:155-322
  - src/melder/nexus/rift/rift_space/rift_space.py:676-990
  - src/melder/nexus/rift/frame_viewer/view_action_hooks.py:11-67
  - src/melder/nexus/rift/frame_viewer/frame_viewer.py:6651-6673
  - src/melder/nexus/rift/command_system/command_system.py:1009-1110
  - src/melder/nexus/rift/command_system/command_system.py:1171-1200
  - src/melder/nexus/rift/command_system/codegen_command_system.py:634-890
  IMPACT: Common management can reuse stable subscription addressing, but callback visibility and
    error timing need explicit migration decisions. Concurrency and '*' collision are source-derived
    regression candidates; no runtime reproduction or repair is claimed in this documentation pass.
  NEXT: Trace room event and memory callback registries and actual emission ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:03:28Z
  TYPE: FACT
  CLAIM: RiftEventSystem and RiftMemorySystem each own an ordered ID-to-callback dictionary with
    register/unregister but no replace/group-clear methods. Emission snapshots the callbacks under
    its registry lock, invokes outside that lock, passes the event/memory object and propagates the
    first raw exception. Removal during an emission leaves that emission's captured callbacks intact.
    Memory callback presence is the memory_enabled flag; command emission skips record construction
    when empty and releases RiftGate before memory callbacks. Cleanup clears references without
    disposing callbacks. Codegen publication still holds its producer lock while emitting; workstation
    weak-collection publication suppresses observer failures. Registry-lock freedom does not mean
    callback execution is outside every producer lock or that every producer shares one error policy.
  EVIDENCE:
  - src/melder/nexus/rift/rift_space/event_system/rift_event_system.py:78-290
  - src/melder/nexus/rift/rift_space/memory_system/rift_memory_system.py:80-435
  - src/melder/nexus/rift/command_system/command_system.py:1072-1157
  - src/melder/nexus/rift/codegen_system/observability/codegen_event_publisher.py:213-248
  - src/melder/nexus/rift/rift_space/workstation.py:862-888
  IMPACT: These subscription registries can map onto common mutation operations with their payload
    types preserved. Clearing callbacks must not reset memory counters/context or destroy the room.
  NEXT: Trace transaction-wide setters and per-session hook registration, dispatch and finalization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:05:07Z
  TYPE: FACT
  CLAIM: ChangeControlManager has replaceable single callback slots; None disables each. It wires
    its own dispatchers into the orchestrator and installs structural-validation/dirty-marking defaults.
    Manager dispatch snapshots per phase; clearing all orchestrator hooks would also remove internal
    correctness wiring. Session-local validators/commit/abort callbacks are ordered append-only lists
    with no returned IDs, remove/replace/clear APIs, callability checks or registration-time status/thread
    checks. Commit snapshots validators plus hooks together; abort snapshots hooks plus reverse-order
    rollback actions and collects BaseException failures. Mediator runs session commit, strategy delta,
    then orchestrator commit, and always strategy on_end. Abort failures are collected by session but
    the shown mediator finalizer does not consume that list; orchestrator suppresses abort-hook errors.
    Revalidators are return-valued conduit-scoped services, not ordinary notification subscribers.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:222-334
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:427-642
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-878
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:1257-1291
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:1522-1576
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:448-587
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:409-528
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1043-1089
  IMPACT: Standardize optional hook management while retaining internal validation, dirtying and
    rollback obligations as explicit owner contracts. Dispatch/error policies need classification;
    identical names alone would hide material semantics. Registration validation/status need tests.
  NEXT: Trace the separate aetheric transaction strategy/inverse model and remaining extension seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:06:26Z
  TYPE: FACT
  CLAIM: The separate aetheric plane uses registered TransactionStrategy classes, with on_start,
    apply_commit_delta and on_end methods, rather than an application callback registry. Its session
    has described rollback actions, allowed only while OPEN; inverse discard refuses OPEN sessions
    and finalization releases the closures after a terminal result. Clearing live rollback obligations
    would change transaction recovery, not merely unsubscribe an observer. DevOps session hooks are
    reached through the mediator's active-session surface; public Book/Conduit transaction context
    managers yield their owner, not a hook/session handle. These paths must be distinguished in the
    common API mapping instead of exposing every internal function pointer as a user hook.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/transaction_strategy.py:91-212
  - src/melder/aether/aetheric_mediator/strategy_builder.py:197-226
  - src/melder/aether/aetheric_mediator/transaction_session.py:641-681
  - src/melder/aether/aetheric_mediator/transaction_session.py:896-1002
  - src/melder/aether/aetheric_mediator/mediator.py:644-701
  - src/melder/aether/aetheric_mediator/mediator.py:1125-1151
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:971-995
  - src/melder/aether/conduit/conduit.py:3075-3096
  - src/melder/aether/spellbook/spellbook.py:4513-4534
  IMPACT: Standardization applies to the management idiom while preserving transaction obligations
    and native extension kinds. Strategy/inverse mutation is not an automatic consequence of clear_hooks.
  NEXT: Classify weak-reference, persistence and logging callback seams, then build the common API matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:08:15Z
  TYPE: FACT
  CLAIM: Weak-reference callbacks are another family: SyncWeakRef replaces one on_collect callback
    and accepts None to clear; WeakRefNode has a separate container callback plus additive extras,
    consumed before GC/explicit firing, with errors suppressed and no individual unregister/replace.
    Workstation uses an extra node callback to publish binding_collected. These must preserve container
    pruning and GC constraints. ExternalPersistenceManager handlers are service providers (fetch/list
    return values), configured then frozen; runtime reconfiguration swaps the whole manager and cleans
    the previous one. Its opt-in emission tap reuses store_unit, not a separate subscription list.
    AetherUtilitySystem's logger resolver is likewise a replaceable/clearable provider, with root-twin
    emission. A common lifecycle-hook clear must not also remove those service/provider contracts.
  EVIDENCE:
  - src/melder/utilities/synchronization/sync_weak_ref.py:109-259
  - src/melder/utilities/synchronization/sync_weak_ref.py:325-347
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:109-212
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:493-553
  - src/melder/nexus/rift/rift_space/workstation.py:821-888
  - src/melder/crystallizer/asset_management/external_persistence_manager_configuration.py:488-628
  - src/melder/crystallizer/asset_management/asset_management_system.py:482-523
  - src/melder/crystallizer/asset_management/asset_management_system.py:976-1043
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:83-154
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:479-559
  - src/melder/aether/aether_utility_system.py:280-374
  IMPACT: The inventory must classify notification hooks, GC callbacks, service providers and internal
    control wiring explicitly. Shared management style is useful; erasing their lifecycle distinctions
    would change system behavior. No new runtime checks were run.
  NEXT: Resolve remaining on_mutation/validity/scheduler callback leads and complete the proposed map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:11:52Z
  TYPE: FACT
  CLAIM: Remaining callback leads resolve into distinct ownership contracts. Hosted ResearchSets
    call the root's injected on_mutation emission callback after mutation; hydration suppresses it
    until rebuild completes. FrameACLContainer receives a manager/Nexus callback that refreshes Rift
    projections. SpellSystemStates attaches a RiskManager object and forwards validity notifications.
    These are live internal notification links, not current user subscription registries. Standalone
    ResearchSet can accept its own callback but has no runtime mutation API for that slot. Scheduler
    factories/UnitOfWork functions are executable tasks; inherited Future callbacks keep that external
    contract. SyntheticModule install/remove operates on sys.meta_path, and Rift's frame-disposed
    method is a logging-only placeholder. None should be mistaken for another Meld-style registry.
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py:129-205
  - src/melder/mutation_research/research_set/research_set.py:209-288
  - src/melder/mutation_research/research_set/research_set.py:2634-2645
  - src/melder/mutation_research/mutation_research.py:885-903
  - src/melder/mutation_research/mutation_research.py:3930-3972
  - src/melder/nexus/frame_acl_manager.py:276-289
  - src/melder/nexus/acl/frame_acl_container.py:132-192
  - src/melder/nexus/acl/frame_acl_container.py:1331-1340
  - src/melder/nexus/nexus.py:2716-2728
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:832-859
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:728-736
  - src/melder/utilities/synchronization/phase_scheduler.py:618-677
  - src/melder/utilities/synchronization/unit_of_work.py:1-19
  - src/melder/crystallizer/synthetic_module.py:1298-1340
  - src/melder/nexus/rift/rift.py:1124-1147
  IMPACT: The system inventory can now distinguish modifiable hook subscriptions from provider,
    strategy, task and mandatory owner-notification seams. Include every family in the mapping and
    document applicability instead of silently changing infrastructure under a generic clear verb.
  NEXT: Write the cross-subsystem operation matrix and a concrete common API recommendation for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:18:18Z
  TYPE: DECISION
  CLAIM: Broader source investigation and common management proposal are complete for the mapped
    families. system_hook_standardization.md contains the full operation matrix, dispatch/lifecycle
    traces, explicit classification of internal/provider/strategy seams, candidate API names and
    migration/regression requirements. Recommend stable registration IDs with common register,
    replace, unregister and clear operations. Facade placement and whole-operation selection are
    review decisions, not implemented behavior. Source reference bounds were checked and three task
    note end-lines corrected. No runtime tests or generation occurred.
  EVIDENCE:
  - artifacts/runtime_hook_discovery_20260921/system_hook_standardization.md
  - tickets/epics/backlog/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md
  IMPACT: Owner can assess one consistent contract using current source evidence. Optional hooks
    must remain distinguishable from required recovery, validation, ACL and persistence wiring.
  NEXT: Review the common API, target placement and in-flight rule before starting an implementation story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T01:06:48Z
  TYPE: TRADEOFF
  CLAIM: Owner requested a per-system comparison of current behavior and improvements. Separate
    correctness friction (Conduit/Meld/Space map ownership, pooling and graduation) from management
    friction (anonymous lists, IDs and single slots) and behavioral friction (in-flight snapshots).
    Recommend the common contract plus core lifecycle repair first; Rift event/memory are simpler
    migrations because ID-based individual removal already exists. Internal wiring requires an
    explicit boundary rather than generic observer clearing.
  EVIDENCE:
  - artifacts/runtime_hook_discovery_20260921/system_hook_standardization.md
  - artifacts/runtime_hook_discovery_20260921/hook_trace.md
  IMPACT: Comparison and priorities are now explicit without claiming that naming alone fixes the
    lifecycle defects or that the owner approved the proposed API spelling/order.
  NEXT: Discuss the common mutation contract against the comparison; keep implementation held.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T09:11:27Z
  TYPE: DECISION
  CLAIM: Parked this broad discovery alongside the owner-backlogged epic. Preserve prior evidence,
    but continue only pooled Conduit/Meld modified-state and safe-baseline investigation in the new task.
  EVIDENCE:
  - Owner's explicit narrowing and backlog request.
  - tickets/tasks/2026-09-22_investigate_pooled_conduit_hook_reset_task.md
  IMPACT: Shared hook API, other callback families and graduation work are no longer active scope.
  NEXT: Use the narrow task for current work; this record remains reference only.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
BACKLOG: owner narrowed scope on 2026-09-22. The following broader investigation is historical context.
Broader investigation complete; read system_hook_standardization.md first for the current inventory
and common API proposal. Core details remain in hook_trace.md. No implementation or new tests yet.
Latest owner direction requires one consistent management style across subsystems as well as runtime
add/clear/re-add/modification. The epic now carries that requirement and the common-API design step.
Candidate public signatures and migration are recorded; final placement and semantics await review.
No implementation is authorized.
Documentation-only trace complete. Read the runtime-hook lifecycle epic and hook_trace.md; owner accepts the
local/lineage model and wants lifecycle/reset gaps recorded, not a redesign. Sixteen prior probes
pass; no runtime source was modified. No further test changes after the owner's stop instruction.
Priority: pooled lesser Meld maps, SpellSpace next-lease baselines, and graduation's discarded new-Book
return. A fresh Book has empty Bind hooks, but current upgrade does not adopt it; complete ownership
rewiring needs a dedicated story. Other adjustment/recording findings remain separate decisions.
The prior bind-hook feature and all generated assets remain under the existing code-review hold.
The complete event map includes arguments, order, error/snapshot policy, reuse-only bypass, and recording.
Graduation also has current leaf-only ward admission after a Conduit state flip, retained parent child-map
membership, old-Book cleanup/facade targets and stale existing Space collaborators. These source findings
need focused runtime probes after approval. No tests ran during this continuation; prior sixteen-pass
characterization evidence remains unchanged. Recommend pool reset as the first independent repair.
