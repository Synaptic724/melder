# Task: Investigate Spellbook bind hooks and lesser-conduit binding

## Metadata
- Task ID: TASK-2026-09-21-investigate-bind-lifecycle-hooks
- Epic: EPIC-2026-09-20-bind-lifecycle-hooks-and-reference-strategies
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-21T00:41:00Z
- Updated: 2026-09-21T10:46:10Z

## Objective
Trace Spellbook registration and propose pre-bind, Spell-context activation and post-bind hooks.
Establish whether a lesser conduit can bind and identify the existing admission rule that decides it.
Complete the owner's expanded impact review of recording, restore/graft, copying, cleanup and consumers.

## Ticket Contract
- ENTRY_GATE: Owner selected the existing bind-hooks epic for investigation and planning.
- EXECUTION_BOUNDARY: Component/graph/source reads, bounded characterization if needed, and durable
  discovery/design records. No feature implementation, generated refresh or release publication.
- DEPENDENCIES: Spellbook/Bind/Spell/configuration, Conduit forwarding, transactions and publication.
- EXIT_GATE: Source-backed hook ownership, order, payload/failure options and lesser-bind verdict
  are documented with a bounded implementation path and explicit remaining decisions.
- FAILURE_ESCALATION: Raise unresolved identity or callback-mutation contracts before implementation.

## Scope Boundaries
- In scope: Book-level registration, existing hook facilities, bind/bind_inactive, wrapper/replay
  implications, lesser/root restrictions and the live epic inventory requested by the owner.
- Out of scope: Runtime feature edits, arbitrary published-Spell mutation, ownership redesign,
  unrelated compiler/cache work, asset generation and release changes.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Expanded source research is recorded in the epic's impact and regression maps.
  The earlier 13 checks remain evidence for current behavior; no runtime feature edits were made.

## Steps / Checklist
- [x] Read relevant component/graph slices and complete bind/configuration call paths.
- [x] Establish lesser bind/bind_inactive behavior and verify it where useful.
- [x] Map three callback stages, ownership, payloads, identity and publication ordering.
- [x] Record a bounded recommendation and required follow-up decisions in the epic.
- [x] Trace full Crystallizer transport/replay and every directly affected lifecycle/publication owner.
- [x] Distinguish required changes, unchanged consumers and conditional callback reattachment.

## Deliverables
- Source-backed discovery notes and implementation recommendation in this task and the parent epic.
- Bounded tests/evidence only if needed to distinguish runtime behavior from source descriptions.

## Validation
13 characterization/integration checks passed in 0.47 seconds through the existing uv environment.
Scoped Ruff passed. No new bind-hook runtime implementation, generation or performance claim.
Expanded 2026-09-21 impact review: source/document inspection only; no additional pytest run.
Final readback checked board routing and 49 source citation ranges across 21 files. Corrected the
emission-tap method's end range to the actual file end, line 1043.

## Risks / Mitigations
Existing pre/activation/post hook arguments belong to creation, not bind. Preserve their semantics.
Fingerprinting precedes Spell construction today; activation-time edits need a coherent contract.

## Applicable Anti-Patterns
- No repurposing existing meld-time callbacks.
- No speculative broad hook framework or hot-path checks.
- No implementation before the registration/mutation ordering is settled.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/bind_hooks_discovery_20260921/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Notes
- DATETIME: 2026-09-21T00:41:00Z
  TYPE: PLAN
  CLAIM: Owner wants Spellbook-configured pre-bind checks, activation receiving Spell context,
    and post-bind callbacks. They also ask whether lesser-conduit binding is currently disabled.
    Begin with the existing epic and binding/configuration/conduit component owners.
  EVIDENCE:
  - tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md:20-46
  - Owner's 2026-09-21 investigation request.
  IMPACT: Discovery and a bounded probe are authorized; production hooks are not implemented here.
  NEXT: Trace both binding entry points and book-owned hook configuration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:44:00Z
  TYPE: FACT
  CLAIM: Both public Conduit.bind and Conduit.bind_inactive immediately reject any conduit whose
    state is not normal, raising "Only normal conduits can bind spells." This occurs before book
    delegation; inactive binding also requires dynamic mode. The live epic folder contains named
    lesser conduits, application recovery, configuration uniformity and conjure boot-meld work;
    the broader user-created-object ownership proposal remains explicitly backlogged.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3160-3197
  - src/melder/aether/conduit/conduit.py:3250-3283
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md:1-26
  - tickets/epics/2026-09-07_stateful_application_recovery_epic.md:1-15
  - tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md:1-13
  IMPACT: The new bind hooks belong to Spellbook's existing registration flow; they do not imply
    enabling lesser binding. Next trace the actual hook registry and finalization order.
  NEXT: Read Spellbook.bind/bind_inactive, Bind construction and configuration hook registration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:48:00Z
  TYPE: FACT
  CLAIM: Spellbook.bind and bind_inactive share Bind construction but publish through separate
    paths. Bind computes SHA256 before constructing Spell; Spell immediately establishes its key,
    family flags and compiler artifact. Existing hook kwargs are attached afterward and execute
    during meld. Configuration hooks currently allow only Meld/Conduit/Link/Contract names and
    reject registration after freeze; there is no bind category today.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:405-551
  - src/melder/aether/spellbook/spell.py:386-508
  - src/melder/aether/spellbook/spellbook.py:4836-4974
  - src/melder/aether/spellbook/spellbook.py:5138-5292
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:76-115
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:679-914
  IMPACT: A Spell-context hook fits before publication, but changing identity-bearing fields is
    a different contract from metadata/hook customization. Asked the owner what edits are needed.
    Component docs claiming arbitrary hook names register silently are stale; source rejects them.
  NEXT: Verify lesser behavior with a bounded runtime probe while tracing wrappers and hook persistence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:53:00Z
  TYPE: FACT
  CLAIM: Fluent finalization and scanning both delegate to Spellbook.bind, so a book-owned
    bind lifecycle reaches them without new per-call wrapper arguments. Crystallizer records hook
    names as code-participation markers; configuration emission enumerates the two current hook
    maps explicitly, and restore reports any recorded hook name generically. A new bind category
    can preserve that existing persistence contract without serializing callbacks.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbinder.py:851-875
  - src/melder/aether/spellbook/bind/scan.py:328-371
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:363-398
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1793-1824
  IMPACT: The likely core changes are book registration/dispatch and a third per-book hook category
    in existing configuration. Dynamic post-conjure binding uses hooks registered before freeze.
    Late hook registration and permitted Spell edits remain explicit design decisions.
  NEXT: Run the lesser-binding and current-hook timing characterization, then write the bounded plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:54:08Z
  TYPE: DECISION
  CLAIM: Owner clarified activation: pass the actual newly constructed Spell as a callback
    parameter, mirroring Meld activation. Register these hooks directly on Spellbook and associate
    them with its Bind component. Do not gate the design on a field-by-field mutation inventory or
    introduce a separate mutation/rehashing framework. The earlier configuration-registry proposal
    is superseded by this direct Spellbook registration requirement.
  EVIDENCE:
  - Owner's activation/context and direct-Spellbook clarification on 2026-09-21.
  - src/melder/aether/spellbook/bind/bind.py:525-551
  IMPACT: Investigation now targets a simple book-owned registration surface and Bind activation
    callback seam. Existing configuration freeze does not itself define the new API's lifecycle.
  NEXT: Verify whether ordinary bind actually requires prior explicit configuration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:56:00Z
  TYPE: MEASURE
  CLAIM: The discovery selection passes 13 tests, including an ordinary Spellbook().bind call
    before any explicit configuration/freeze. Lesser bind and bind_inactive refuse in both modes;
    existing lessers resolve later owner bindings. Existing pre/activation/post kwargs run only at
    meld. Source confirms the stronger configure-first rule is enforced at dynamic conjure only
    when Crystallizer is active; bind itself counts early registrations instead of refusing them.
  EVIDENCE:
  - artifacts/bind_hooks_discovery_20260921/characterization_final.log:1-2
  - tests/experimentation/test_bind_lifecycle_discovery_experiment.py
  - src/melder/aether/spellbook/spellbook.py:3546-3568
  - src/melder/aether/spellbook/spellbook.py:5432-5477
  - src/melder/aether/spellbook/spellbook.py:6513-6541
  IMPACT: Direct Spellbook registration is the accepted hook setup surface. Configure-first is not
    a universal current bind gate. No new configuration gate is required merely for these hooks.
  NEXT: Record the revised direct-Spellbook/Bind implementation plan and hand it back for discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:58:00Z
  TYPE: FACT
  CLAIM: Completed the revised direct-Spellbook/Bind plan. Hook registration belongs on Spellbook;
    activation receives the real newly constructed Spell. Preserve existing identity/profile work
    and creation hooks. No mutation whitelist or new configuration hook category is required.
    Existing book-twin hook markers can be extended without persisting callback bodies.
  EVIDENCE:
  - artifacts/bind_hooks_discovery_20260921/plan.md
  - artifacts/bind_hooks_discovery_20260921/characterization_final.log:1-2
  - artifacts/bind_hooks_discovery_20260921/lint.log:1-1
  IMPACT: Discovery is ready for discussion/implementation direction. Configuration-before-bind
    is only a recorded dynamic-world requirement, enforced at conjure; lesser binding is disabled.
  NEXT: Owner reviews the bounded callback setup and selects implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T10:28:54Z
  TYPE: PLAN
  CLAIM: Owner requested the complete cross-component impact, especially Crystallizer, recorded
    in the epic. The earlier pass traced the bind core and hook markers but did not complete
    persistence/replay/graft/clone/publication consumer verification.
  EVIDENCE:
  - Owner's request to research Crystallizer and all other affected elements.
  - artifacts/bind_hooks_discovery_20260921/plan.md
  IMPACT: Reopen discovery only. Preserve direct Spellbook registration, actual-Spell activation,
    existing identity semantics and the no-feature-implementation boundary.
  NEXT: Trace book emission, serialized records, preflight/restore/graft, book copying and publishers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T10:31:54Z
  TYPE: FACT
  CLAIM: SpellbookCrystal already carries a generic hook_names string list and describes it
    unchanged; ConfigurationLossStrategy and restore iterate arbitrary names. Direct bind hooks
    therefore need producer-side marker wiring, not a new callable serializer. Preset Spellbooks
    share only configuration and frame name; they create a fresh book/Bind and transfer no other state.
    SpellCrystal captures a fixed native bind-policy payload, not arbitrary Spell metadata or hook bodies.
  EVIDENCE:
  - src/melder/crystallizer/crystals/spellbook_crystal.py:91-142
  - src/melder/crystallizer/crystals/spellbook_crystal.py:213-264
  - src/melder/crystallizer/crystal_analysis/preflight/configuration_loss_strategy.py:69-119
  - src/melder/aether/spellbook/spellbook.py:6240-6278
  - src/melder/crystallizer/crystals/spell_crystal.py:265-299
  - src/melder/crystallizer/crystals/spell_crystal.py:1071-1170
  IMPACT: The epic must distinguish required emission wiring from already-generic record readers,
    define new-book hook isolation, and avoid claiming arbitrary callback effects are replayed.
  NEXT: Follow checkpoint/formation materialization and the actual restore/graft bind entry points.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T10:39:15Z
  TYPE: FACT
  CLAIM: Record capture transports the book twin's describe payload; restore builds a fresh Book
    and immediately replays active binds before conjure and staged binds afterward. Graft instead
    calls bind/bind_inactive on an existing receiving Book. Full restore currently has no callback
    reattachment point between Book construction and first bind. Nexus/MR consume normal finalized
    publication; they need correct ordering, not independent bind-hook registries.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:1030-1164
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1710-2023
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:229-573
  - src/melder/aether/spellbook/spellbook.py:5913-5965
  - src/melder/nexus/frame_descriptor_manager.py:498-571
  - src/melder/aether/spellbook/spellbook.py:4965-5002
  IMPACT: Separate mandatory presence-marker recording from optional restore reattachment. Keep
    per-bind post notification distinct from outer-transaction commit; callback failures cannot
    promise to reverse arbitrary user effects. Crystallizer activation catches up only root policy.
  NEXT: Finish formation/cache transport verification and write the complete epic impact matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T10:42:47Z
  TYPE: FACT
  CLAIM: Formation capture includes book.describe unchanged, checkpoint codecs and JSON cache
    transport generic payloads, and emission taps forward describe dictionaries. New bind markers
    fit existing hook_names. Two lifecycle details must be included in implementation: Book currently
    deletes its Bind reference without calling Bind.cleanup, and public Spell.cleanup routes through
    registered-book removal unless the local-teardown guard is set. An unpublished activation failure
    therefore cannot blindly call the public removal path. The bind mediator derives failure from
    sys.exc_info and ABORT_ONLY; the absent success argument at the Book door is not proof of a bug.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:1164-1306
  - src/melder/crystallizer/persistence/persistence_crystal.py:345-451
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:127-175
  - src/melder/crystallizer/asset_management/asset_management_system.py:994-1043
  - src/melder/aether/spellbook/spellbook.py:358-387
  - src/melder/aether/spellbook/spellbook.py:704-734
  - src/melder/aether/spellbook/spell.py:512-614
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:694-747
  IMPACT: Required work is producer marker wiring plus concrete callback ownership/cleanup and
    failure tests. Generic storage/readers need compatibility tests, not new callable schemas.
    Explicit creation-hook kwargs still attach after activation and replace only provided lists.
  NEXT: Consolidate required edits, unchanged consumers and conditional restore work in the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T10:46:10Z
  TYPE: FACT
  CLAIM: The epic now carries the complete impact map, concrete recording work, generic-reader
    compatibility, full-restore/graft distinction, cleanup/failure ordering, implementation sequence,
    source reread pointers and observable regression matrix. Inspection also confirmed bind structural
    work stages until transaction end; post at registration completion cannot claim outer commit.
  EVIDENCE:
  - tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md:148-348
  - src/melder/aether/spellbook/spellbook.py:4371-4528
  - src/melder/aether/spellbook/spellbook.py:4530-4676
  IMPACT: Expanded discovery is ready for owner review. Runtime implementation remains a separate
    authorized tranche; no generated assets or new persistence schema were added.
  NEXT: Owner reviews the epic and selects implementation with the listed remaining API choices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Expanded discovery is complete. The parent epic's Cross-Component Impact Map is the current result;
the plan artifact is the original core recommendation with an update pointer. Direct Book registration
and actual-new-Spell activation are settled. Keep native identity and existing creation hooks.

Required scope includes deterministic Book-to-Bind cleanup, unpublished activation-failure teardown,
active/inactive post dispatch and bind-stage markers passed to the current book-twin emitter. Generic
record/cache/formation/tap transport and hook shortfall readers already work on arbitrary names.
Full restore creates a fresh Book and offers no pre-bind callback attachment; recommend report-only
compatibility unless owner selects the conditional extension. Graft uses receiving live-book hooks.

Book preset/upgrade isolation, transaction commit distinction, normal native publication and the
required regression matrix are in the epic. Lesser binding remains disabled; ordinary bind uses
mutable defaults. The prior 13 tests/lint passed; expanded research used source inspection only.
Production hooks and generated assets remain unmodified. Next: owner review and implementation choice.

## Noting Behavior
Record one complete call-path finding at a time, with source evidence and the next concrete step.
