# Task: Map named lesser conduit implications across subsystems

## Metadata
- Task ID: TASK-2026-09-06-named-conduit-cross-system-discovery
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Story: none (cross-cutting epic discovery)
- Status: review
- Owner: codex
- Agent Name: codex_1, updater_0
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-07T11:46:34Z

## Objective
Map how optional lesser names/discovery interact with pooling, automatic/dynamic mode, frame root
ownership, Crystallizer recording/replay, Nexus projection/ACL/commands and other cloud consumers.

## Ticket Contract
- ENTRY_GATE: Owner approved cross-system discovery and the parent epic is recorded.
- EXECUTION_BOUNDARY: Indexed docs, complete relevant source methods/call paths, focused read-only
  checks/probes and ticket/story findings. No runtime or generated-source edits.
- DEPENDENCIES: tickets/tasks/2026-09-06_named_conduit_semantics_task.md and the parent epic's draft stories.
- EXIT_GATE: Evidence map, concrete impacts, recommended boundaries and genuine owner decisions are recorded.
- FAILURE_ESCALATION: Stop before implementing or deciding unapproved recording/lifetime/permission semantics.

## Questions
- Which consumers require roots specifically, and which really need a discovery directory?
- Is automatic naming/discovery purely metadata, or does any current gate rely on unnamed lessers?
- What happens to name/projection/identity when a lesser is created, pooled, reacquired or upgraded?
- What does Crystallizer record now: root topology, lesser topology, scope instances, or none of these?
- What does Nexus expose for lessers today, and which commands presume the selected conduit is normal?
- Does broadening cloud lookup/listing affect frame liveness, DevOps counts, clusters, lookup caches or restore?

## Steps / Checklist
- [x] Map the identified root/discovery consumers and pool/upgrade transitions.
- [x] Trace Nexus publication, visibility/ACL and command assumptions.
- [x] Trace Crystallizer emissions, root replay and name-collision consumers.
- [x] Synthesize story-level implications, validation expectations and owner decisions.

## Validation
- Prior naming evidence: three existing integration tests and an isolated probe passed.
- Two-mode pooled-name probe passed and confirmed the current stale-label/reassignment issue.
- Source-backed impact review completed; no implementation tests for the proposed feature exist yet.
- Full suite not run. Runtime source, CI and generated assets were not modified by this task.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Initial source-backed implications, probe results and owner decisions are recorded.

## Noting Behavior
Read one call path through; record factual evidence and a next single step before moving to another subsystem.

## Notes
- DATETIME: 2026-09-06T17:17:54Z
  TYPE: PLAN
  CLAIM: Reuse verified naming evidence instead of repeating it. First identify consumers of the
    frame root maps and cloud enumeration; then follow Nexus publication and Crystallizer replay.
  EVIDENCE:
  - tickets/tasks/2026-09-06_named_conduit_semantics_task.md
  - src/melder/aether/aetheric_frame/aetheric_frame.py:160-196
  IMPACT: Keep discoverability distinct from ownership and avoid scope expansion into new lifetime features.
  NEXT: Inventory and read the relevant frame/cloud consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:28:01Z
  TYPE: FACT
  CLAIM: Aether list/count/name/id facades read root-only frame maps directly; they do not route
    through ConduitCloud. Transfer-of-ownership and Nexus command surfaces call those Aether APIs.
    Conduit cleanup owns child/pool teardown separately from root unregistration. The conduit crystal
    emitter explicitly excludes lessers and automatic mode, while Nexus conduit publication accepts
    normal, lesser and pooled_lesser states when publication is enabled.
  EVIDENCE:
  - src/melder/aether/aether.py:1643-1890
  - src/melder/aether/conduit/conduit.py:443-467
  - src/melder/aether/conduit/conduit.py:756-951
  IMPACT: Broadening a cloud index alone will not broaden Aether lookup or command access. Conversely,
    broadening root maps would alter consumers beyond naming. Discovery and persistence already differ.
  NEXT: Read Nexus records/commands and the Crystallizer restore/admission consumers found by search.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:42:21Z
  TYPE: FACT
  CLAIM: Nexus frame summaries already distinguish root ids/names/counts from cloud names/counts.
    Conduit records already carry name, state, parent id, depth and root id. Passive publication is
    gated by rift_enabled, not the dynamic flag alone. Fresh lessers publish, but pooled release
    and reuse deliberately do not republish. Capability/codegen raw-name helpers first validate
    published identity and command permissions, then use root-only Aether lookup; static rooms
    deliberately reject raw conduit access. Naming must not silently change those permissions.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:222-415
  - src/melder/aether/spellbook/spellbook.py:5883-5922
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:2227-2385
  - src/melder/nexus/rift/command_system/command_system.py:1345-1428
  - src/melder/nexus/rift/command_system/capability_command_system.py:198-294
  - src/melder/nexus/rift/command_system/codegen_command_system.py:272-309
  - src/melder/nexus/rift/command_system/static_command_system.py:137-160
  IMPACT: Existing payload fields largely fit named scopes. Publication timing and the final
    live-object resolver need explicit decisions; discovery must not imply new raw-object authority.
  NEXT: Record the persistence and pool implications before synthesizing the design choices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:42:21Z
  TYPE: FACT
  CLAIM: Conduit._emit_conduit_twin requires normal state, dynamic mode and active recording.
    RestoreEngine._conjure_for_book selects one recorded conduit per Spellbook and calls conjure;
    simply emitting lesser twins would not restore a child hierarchy correctly. Both host preflight
    and skip-existing replay probe cloud.has_conduit_name, so a wider discovery namespace can
    change restore collisions even if lesser scopes themselves remain unrecorded. Transfer impact
    enumeration and cluster membership are also intentionally root-oriented consumers.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:421-467
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1826-1880
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:434-544
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:752-814
  - src/melder/aether/aetheric_frame/conduit_cloud.py:214-254
  - src/melder/aether/aetheric_frame/conduit_cloud.py:663-707
  IMPACT: Recommended boundary is ephemeral discovery without a new crystal family or lifetime.
    Still specify restore collision rules and preserve root-only transfer/cluster contracts.
  NEXT: Synthesize recommendations and unresolved owner choices in the epic and draft stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:42:21Z
  TYPE: MEASURE
  CLAIM: An isolated pool probe passed in automatic and dynamic modes: a lesser labeled request-a
    is returned by the next acquisition as the same shell, still named request-a, and assigning
    request-b raises because the setter is write-once. This is a baseline finding, not the desired
    new behavior. All probe roots/books were cleaned; no runtime source file was changed.
  EVIDENCE:
  - Two-mode pooled-name probe (exit 0; same_shell=true, name_after_reuse=request-a, rename_rejected=true)
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:1588-1630
  - src/melder/aether/conduit/conduit_pool.py:108-161
  IMPACT: Registry insertion alone would be incomplete. Unregister/clear before pool return and
    fresh name/publication on acquisition are part of the core feature contract.
  NEXT: Present the evidence-backed design boundaries and obtain owner direction before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T22:13:56Z
  TYPE: PLAN
  CLAIM: After synaptic_python_developer onboarding and owner certification as updater_0,
    the owner requested targeted src_components reading for this epic. The component index
    check passes: 136 sections over 8445 lines. Read lifecycle/frame/cloud boundaries, then
    Nexus visibility and commands, Crystallizer restore, and relevant DevOps contracts.
  EVIDENCE:
  - system_docs/src_components_index.md:10-18
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md:28-41
  - Owner's component-reading request and updater_0 certification in this conversation.
  IMPACT: This pass builds documented design context; existing implementation decisions remain open.
    Document descriptions will not be promoted to independently verified runtime behavior.
  NEXT: Read the indexed conduit, frame/cloud and instance-ownership sections as one lifecycle unit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T22:15:56Z
  TYPE: FACT
  CLAIM: updater_0 read the full indexed C3 entries for Spellbook, configuration, Aether/frame,
    Conduit, Ward and Creations, plus the C2 registry/lifecycle/cluster entries and related flows.
    The documented model places lesser lineage and pooling under conduit ownership, preserves the
    creations manager during upgrade, and separates scope teardown from root registration.
    Naming must fit these existing ownership and disposal boundaries.
  EVIDENCE:
  - system_docs/src_components.md:339-498
  - system_docs/src_components.md:717-1049
  - system_docs/src_components.md:2057-2456
  - system_docs/src_components.md:4175-4345
  - system_docs/src_components.md:5407-5458
  IMPACT: The lifecycle read identifies the design seams; this is documentation context,
    not an independent verification of current source behavior.
  NEXT: Read Nexus descriptor, viewer and command contracts for named-scope visibility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T22:15:56Z
  TYPE: CONFLICT
  CLAIM: The component map says lessers cannot have names and describes cloud lookup as dynamic-only.
    The epic's recorded source discovery distinguishes unregistered lesser labels from discovery
    and reports root lookup in both modes. The C2 cloud entry also describes a generic _registry,
    whereas the epic records borrowed root maps. These descriptions must be reconciled against
    source before implementing; a current document index does not prove current semantics.
  EVIDENCE:
  - system_docs/src_components.md:2106-2116
  - system_docs/src_components.md:4333-4345
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md:49-59
  IMPACT: Do not use these component statements to override the newer discovery or choose mode/API
    semantics. No runtime source was reread to adjudicate the mismatch in this document-reading pass.
  NEXT: Complete the requested component context, then retain these source-verification targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T22:17:11Z
  TYPE: FACT
  CLAIM: updater_0 read the indexed AR runtime, descriptor/ACL manager, workstation/command,
    viewer and publication/refresh sections. The documented chain separates canonical records
    owned by FrameDescriptorManager, projections owned by Rift, and room-specific command access.
    Record removal does not itself mutate Rift projection state; the document specifies refresh.
    Workstation bindings also have their own lifetime and pre-bind ACL boundary.
  EVIDENCE:
  - system_docs/src_components.md:1304-1752
  - system_docs/src_components.md:1833-2056
  - system_docs/src_components.md:4953-5167
  - system_docs/src_components.md:5259-5328
  IMPACT: Named-scope publication/removal and projection refresh are separate design concerns.
    Returning a raw lesser must preserve room-mode/ACL gates and must not imply ownership transfer
    or automatic cleanup of workstation-bound objects. These are document-derived boundaries.
  NEXT: Read Crystallizer recording, load admission, restore and collision-related component sections.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T22:18:00Z
  TYPE: FACT
  CLAIM: updater_0 read the Crystallizer C3 entry and indexed persistence/restore, decomposition,
    load-scope and public-cloud sections. The documented record, asset store and loader have
    distinct ownership. Host admission and skip-existing replay consult public cloud name probes;
    name collisions can refuse before replay or enter an explicit skip/shortfall path.
    New recorded entity kinds require matching record and loader treatment.
  EVIDENCE:
  - system_docs/src_components.md:1050-1303
  - system_docs/src_components.md:7626-7818
  - system_docs/src_components.md:7819-8058
  IMPACT: Even ephemeral named lessers can affect restore through a shared discovery namespace.
    Collision policy must therefore be explicit while recording/replay scope remains independently
    defined. Read dated promoted material alongside newer amendments, not as one timeless contract.
  NEXT: Read the frame DevOps and transaction-admission sections to finish the requested boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T22:18:28Z
  TYPE: FACT
  CLAIM: updater_0 completed the requested component reading with the DevOps control-plane,
    transaction-admission and information-strategy entries plus their C2 state/strategy sections.
    The documented plane distinguishes per-conduit resolution state, structural scope claims,
    mirrored relationship/population reports and the separately borrowed world LoadGate.
    Naming/discovery does not itself define a new structural transaction or validity contract.
  EVIDENCE:
  - system_docs/src_components.md:2835-3223
  - system_docs/src_components.md:4810-4925
  IMPACT: Preserve identity-based validity, root/cluster accounting, scope proportionality and
    existing lock ordering when the naming contract is designed. The component read is complete;
    no source behavior was independently verified or changed in this pass.
  NEXT: Discuss the epic's pending contract decisions using this context and the recorded doc mismatches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-07T11:05:29Z
  TYPE: PLAN
  CLAIM: Owner clarified the present constructor rule: lesser conduits are initialized unnamed.
    The requested design keeps only named conduits in cloud discovery; finishing a named lesser
    unregisters and wipes its name before pool reuse, while an unnamed lesser skips unregistration.
    Check the constructor and pooled lifecycle to narrow the earlier document-conflict note.
  EVIDENCE:
  - Owner's 2026-09-07 clarification in this conversation.
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md:36-41
  IMPACT: Named-only registry work is accepted design overhead. This clarification does not choose
    the remaining mode, namespace, setter, Nexus or persistence semantics or authorize runtime edits.
  NEXT: Read the complete initialization, name setter, lesser acquisition and pool-release paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:07:30Z
  TYPE: FACT
  CLAIM: Source recheck narrows updater_0's 2026-09-06 conflict note. Conduit.__init__ calls
    _configure_conduit_state, which warns and clears a supplied lesser name to None. The owner's
    constructor description is correct. The separate post-init setter checks cleaned/write-once
    state only, assigns _name, and performs no cloud registration. Fresh lesser creation supplies
    no name; pooled acquisition bypasses __init__. Pool preparation resets scoped state and returns
    the shell without clearing _name. Thus a manually assigned label surviving reuse is a setter
    path observation, not evidence that named lesser construction is currently supported.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:195-420
  - src/melder/aether/conduit/conduit.py:1365-1384
  - src/melder/aether/conduit/conduit.py:1556-1630
  - src/melder/aether/conduit/conduit.py:533-620
  - src/melder/aether/conduit/conduit.py:2227-2425
  - src/melder/aether/conduit/conduit_pool.py:106-161
  IMPACT: Correct the earlier broad mismatch claim. Named acquisition must handle both fresh and
    reused shells, and unregistration/name clearing must finish before pool publication. Keep name
    presence consistent with successful discovery registration when defining the setter contract.
  NEXT: Carry the owner's named-only cloud and conditional cleanup rule into the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:07:30Z
  TYPE: FACT
  CLAIM: The narrow cloud source read confirms the remaining component-description drift:
    ConduitCloud retains injected _conduits and _conduit_ids_by_name mappings, not an owned _registry.
    get_conduit delegates to get_conduit_by_name, which checks cleaned state and looks up name/id
    under the cloud lock without a dynamic-mode gate. Conduit.get_conduit_cloud also has no mode gate.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:108-168
  - src/melder/aether/aetheric_frame/conduit_cloud.py:321-369
  - src/melder/aether/conduit/conduit.py:1632-1651
  IMPACT: The owner's lesser-init correction does not imply that basic cloud lookup is dynamic-only.
    Named-scope discovery still needs an explicit registry boundary separate from root ownership.
  NEXT: Preserve the remaining namespace, mode, setter and consumer choices for the design discussion.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-07T11:14:34Z
  TYPE: FACT
  CLAIM: updater_0 has now read prewarm_lesser_conduits and the full AbstractElasticPool source;
    the earlier read covered ConduitPool/reuse/return but omitted prewarming. Prewarm takes a batch
    through create_lesser_conduit, holds the whole batch, then cleans each shell into the idle pool.
    Its target is min(count, pool.max_idle). The base constructor starts with an empty deque;
    the idle target is capacity, not eager construction. The live conduit path calls the specialized
    create_object/return_lesser_conduit methods directly, bypassing base acquire/prepare_object/release.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1161-1211
  - src/melder/aether/conduit/conduit.py:2227-2385
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit_pool.py:62-161
  - src/melder/utilities/general_base/abstract_elastic_pool.py:114-190
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-382
  IMPACT: Prepared shells exist before an application requests a named scope. A caller's name
    belongs to initialization of that use through the lesser-creation API; it cannot depend on
    rerunning the Python constructor or on an unused base-pool preparation hook.
  NEXT: Record creation-only naming and remove later lesser naming/renaming from pending choices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:14:34Z
  TYPE: DECISION
  CLAIM: Owner fixed the public timing: lesser conduits can receive a name only when the caller
    makes the lesser conduit. No post-creation naming or renaming is part of this feature. Prewarmed
    idle shells stay unnamed; the creation call initializes the selected shell for this scope,
    including its optional name/cloud registration. Release unregisters/clears before reuse.
  EVIDENCE:
  - Owner's creation-only naming and prebuilt-pool clarification in this conversation.
  - src/melder/aether/conduit/conduit.py:1161-1211
  - src/melder/aether/conduit/conduit.py:2227-2385
  IMPACT: Lesser naming time is settled and is not an open setter-policy decision. Keep internal
    pool reset distinct from public mutation; preserve the unnamed path's absence of cloud work.
  NEXT: Continue only with the remaining namespace, mode, publication and consumer decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:20:50Z
  TYPE: DECISION
  CLAIM: Owner requires Crystallizer to save and restore the structure/state of named conduits,
    including lessers. Created runtime objects are not the restoration target. This supersedes
    the earlier ephemeral-only recommendation. Nexus impact is an investigation question: determine
    whether cloud discovery supplies its reads or whether publication/projection work is required.
  EVIDENCE:
  - Owner's named-lesser structural persistence correction in this conversation.
  IMPACT: Trace emitter, crystal fields, record/journal/checkpoint, removal/fold, formation selection,
    sequential/parallel replay and Nexus consumers before recommending a structural contract.
    Keep creation-only naming and named-only cloud cleanup; runtime implementation is not started.
  NEXT: Read the conduit emission and complete ConduitCrystal/record/capture path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:24:22Z
  TYPE: FACT
  CLAIM: The capture chain is now source-read through Conduit._emit_conduit_twin, the complete
    ConduitCrystal, Crystallizer.emit, PersistenceSystem.record/create_checkpoint, profile typed
    record/replace/journal/capture and the complete PersistenceCrystal cached-item round trip.
    The emitter excludes lessers and records name, state/root id, policy, book id and outbound links;
    it supplies no immediate-parent id and no Creations object store. Conduit twins are keyed by id.
    Checkpoints detach current twin payloads for identities journaled in the window; cloud enumeration
    is not the capture mechanism. Profile removal has book/frame subtree eviction but no conduit-only
    removal verb or conduit_removed capture case.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:421-467
  - src/melder/crystallizer/crystals/conduit_crystal.py:8-306
  - src/melder/crystallizer/crystallizer.py:1522-1575
  - src/melder/crystallizer/persistence/persistence_system.py:245-278
  - src/melder/crystallizer/persistence/persistence_system.py:939-1011
  - src/melder/crystallizer/persistence/persistence_profile.py:230-333
  - src/melder/crystallizer/persistence/persistence_profile.py:436-526
  - src/melder/crystallizer/persistence/persistence_profile.py:571-720
  - src/melder/crystallizer/persistence/persistence_profile.py:1028-1163
  - src/melder/crystallizer/persistence/persistence_profile.py:1336-1429
  - src/melder/crystallizer/persistence/persistence_crystal.py:78-451
  IMPACT: Named-lesser persistence needs explicit emission and parent topology plus a scope-removal
    record mirrored by folding. Returning a lesser cannot reuse book-removal semantics because it
    borrows the book. Pooled id reuse requires checking within-window removal/re-emission ordering.
  NEXT: Read fold and both replay schedulers, including book-to-conduit selection and teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:24:22Z
  TYPE: FACT
  CLAIM: capture_formation_slice currently selects one conduit twin plus its book/custody/indexes
    for a conduit anchor. A frame slice gathers every recorded conduit sharing each selected book.
    It does not walk lesser parent/child edges. Adding lesser twins without revising selection would
    leave a lesser-anchored slice without its root/parent support, and a root anchor without its children.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:1164-1307
  IMPACT: Formation ancestor/descendant inclusion is part of structural restoration, separate from
    serializing created objects. Determine the named-child/unnamed-parent contract explicitly.
  NEXT: Trace how the loader currently chooses and reconstructs conduits from recorded book ids.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:28:03Z
  TYPE: FACT
  CLAIM: Fold and both replay drivers are now read, along with the full book/bind/conjure/staged/
    selection unit, bind-target hydration and rollback. _conjure_for_book matches all conduit rows
    by spellbook_id, takes recorded[0], and calls Spellbook.conjure without inspecting conduit_state
    or parent/root configuration. Other same-book conduit rows are not built. The sequential driver
    has no lesser stage; the parallel plan has book nodes but no child-conduit dependency nodes.
    Hydration resolves class/function binding targets; it does not restore saved Creations objects.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:465-1085
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1714-2125
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2456-2539
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:265-309
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2680-2702
  IMPACT: Merely allowing lesser emission can select a child as the book's root and omit other rows.
    Replay must select roots explicitly and recreate lesser structure through parent creation verbs,
    preserving shared book ownership, parent order, fresh-id translation and rollback in both drivers.
    A shared per-book hierarchy replay could serve both drivers; exact task design remains pending.
  NEXT: Trace Nexus record/publication/projection and raw-name resolution to settle cloud sufficiency.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:28:03Z
  TYPE: FACT
  CLAIM: _fold_chain replays every journal entry in order using the window's final payload per
    kind/key. It recognizes superseding *_removed events when an earlier payload is absent, but
    _fold_entry has no conduit_removed case. Book removal sweeps every conduit sharing that book.
    Formation host preflight checks every recorded conduit name through cloud.has_conduit_name;
    world loads skip host preflight. skip_existing currently drops a collided root name before conjure.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1086-1319
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1827-1881
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:165-545
  IMPACT: Scope removal needs its own record/capture/fold semantics. Tests must cover release before
    a seal and the same pooled id emitted, removed and re-emitted with another name within one window
    and across windows. Collision handling must preserve named structural intent or report explicit refusal.
  NEXT: Complete Nexus and structural-preflight source reads before synthesizing implementation boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:36:28Z
  TYPE: FACT
  CLAIM: Nexus already carries conduit_name/state, parent id/depth and root id, and the publication
    manager accepts normal, lesser and pooled_lesser. Frame summaries read cloud names, but command
    name/list/has paths read descriptor records plus compiled enabled ids. Capability/codegen named
    getters then call Aether's root maps; the existing id getter instead has a recursive lesser
    fallback. The raw capability cloud getter directly returns the cloud after frame/raw-access gates.
    Fresh lesser creation publishes; pooled release/reuse do not update those records today.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:177-497
  - src/melder/nexus/frame_descriptor/conduit_record.py:65-161
  - src/melder/nexus/frame_descriptor/conduit_descriptor_payload.py:62-154
  - src/melder/nexus/rift/command_system/capability_command_system.py:141-463
  - src/melder/nexus/rift/command_system/codegen_command_system.py:272-309
  - src/melder/nexus/rift/command_system/command_system.py:194-250
  - src/melder/nexus/rift/command_system/command_system.py:1221-1428
  - src/melder/aether/aether.py:1842-1983
  - src/melder/aether/conduit/conduit.py:872-952
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:2227-2385
  IMPACT: Existing payload fields suffice for basic named-lesser description; no new named flag is
    indicated. Cloud changes serve raw-cloud consumers and frame summaries, but do not automatically
    update published names or the named command resolver. Keep ACL checks and reuse an appropriate
    lesser-aware resolution seam rather than turning frame root maps into a generic scope registry.
  NEXT: Record the exact live-descriptor versus compiled-membership boundary before choosing refresh work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:36:28Z
  TYPE: FACT
  CLAIM: The full CommandProjection/ViewProjection classes borrow the live FrameDescriptor and own
    detached compiled ACL surfaces. Descriptor upsert/remove changes later record reads directly.
    Compilation derives visible/enabled conduit-id sets from then-published ids. ViewFrame._build_links
    iterates compiled visible ids and raises when a record was removed; capability lists instead
    filter current records by enabled ids. Nexus publication/removal only ensure the ACL container;
    an existing container is returned unchanged. It does not recompile existing Rift projections there.
  EVIDENCE:
  - src/melder/nexus/rift/projection/command_projection.py:65-164
  - src/melder/nexus/rift/projection/view_projection.py:65-151
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:227-242
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:412-465
  - src/melder/nexus/acl/frame_acl_compiler.py:340-383
  - src/melder/nexus/acl/frame_acl_compiler.py:687-768
  - src/melder/nexus/rift/frame_viewer/view_frame.py:2182-2303
  - src/melder/nexus/rift/frame_viewer/view_conduit.py:1510-1564
  - src/melder/nexus/nexus.py:1297-1363
  - src/melder/nexus/nexus.py:3395-3413
  - src/melder/nexus/frame_acl_manager.py:253-289
  IMPACT: Correct the earlier broad refresh implication: same-id payload replacement and changed id
    membership are different. Existing prewarmed ids can carry new names through updated records,
    while added/removed ids require projection-membership handling. Removing pooled records without
    reconciling compiled ids can break viewer reads. Evaluate retained unnamed pooled records versus
    removal plus refresh; do not impose a full refresh on every name change without need.
  NEXT: Complete structural preflight review and revise the persistence/Nexus stories from this evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:36:28Z
  TYPE: FACT
  CLAIM: Ward linking stores the actual immediate parent separately from the root. Nested lessers
    are real hierarchy; _detach_for_pool recursively cleans descendants, removes the parent edge,
    and keeps the root for reuse. A named child can therefore require an unnamed intermediate parent
    when restoring its exact prior structure; root_id alone cannot reconstruct that relationship.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:381-436
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1141-1209
  - src/melder/nexus/frame_descriptor_manager.py:417-466
  IMPACT: Define structural ancestor inclusion explicitly. Only-named cloud membership does not by
    itself decide which unnamed supporting nodes a faithful structural record/replay needs.
  NEXT: Present required ancestor closure as a concrete remaining contract question.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:39:38Z
  TYPE: FACT
  CLAIM: The full PersistenceAnalyzer, LinkIntegrityStrategy and FramePostureStrategy are read.
    The analyzer runs its ordered strategy set over the folded value bundle. Link integrity checks
    outbound peer link_targets only; frame posture checks each book's frame twin. These passes do
    not establish the new lesser-parent/root relationship contract or ancestor ordering.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py:113-217
  - src/melder/crystallizer/crystal_analysis/preflight/link_integrity_strategy.py:73-103
  - src/melder/crystallizer/crystal_analysis/preflight/frame_posture_strategy.py:75-110
  IMPACT: The new structural schema needs preflight for missing/cyclic parents, root/book consistency
    and invalid recorded lifecycle state. Peer-link warnings must not stand in for required parent
    validation. Created-instance persistence is outside this work.
  NEXT: Revise the epic and four story contracts to reflect the owner's structural persistence requirement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:46:34Z
  TYPE: RISK
  CLAIM: RecordVersion speaks 1.0.0 and refuses only newer-major artifacts. A new child-bearing
    conduit payload written under the same major reaches an old root-only loader that selects
    recorded[0] per book. Unknown additive fields therefore cannot protect structural meaning.
  EVIDENCE:
  - src/melder/crystallizer/persistence/record_version.py:76-76
  - src/melder/crystallizer/persistence/record_version.py:142-180
  - src/melder/crystallizer/persistence/persistence_crystal.py:376-451
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1827-1881
  IMPACT: The implementation needs a forward-safe version/migration decision, with older root-only
    input still supported and older readers refusing records whose child topology they cannot replay.
  NEXT: Include schema/version safety in the persistence story and patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Owner confirmed creation-only naming, named-only cloud discovery, conditional unregister/name reset
before pool reuse, and required named-lesser structural persistence. Created-instance data is excluded.
The earlier ephemeral-only recommendation is superseded.

The 2026-09-07 source trace covers emitter/twin, record/journal/checkpoint and cached values, removal/fold,
formation selection, both replay drivers, binding hydration, host/structural preflight and version gates.
Current gaps: no lesser emission/immediate-parent data/conduit-only removal, first-row root selection,
no lesser reconstruction and no child-aware formation closure. Pooled id reuse needs chronology tests.

Nexus already has name/state/parent/root fields. Frame summaries read cloud names; published named
queries use records plus compiled ids and final named lookup uses Aether root maps. Same-id record
updates are visible through borrowed descriptors; changed membership needs coherent projection handling.
All four stories are aligned with the required structural scope. Remaining decisions: mode/namespace,
unnamed ancestor support, version/collision policy and Nexus pooled-record/refresh semantics.
Runtime implementation and new test execution were not part of this discovery pass.
