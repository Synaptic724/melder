# Epic: Named lesser conduits as discoverable live scopes

## Metadata
- Epic ID: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: in_progress
- Owner: codex
- Agent Name: codex_1, updater_0
- Priority: p2
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-07T17:22:45Z
- Target Window: Owner-approved design first; implementation not yet authorized.

## Problem / Opportunity
Applications may need to locate a particular request, session, job, or other live scope without
maintaining their own conduit registry. A lesser conduit borrows binding definitions but can own
scoped creations. Naming should make that existing owner discoverable without promoting it into
a normal root, creating another Spellbook, or changing its instance lifetimes.

The value is shared scope discovery and operational tracking. It is not a new lifetime model,
automatic cleanup, asset ownership, or a substitute for keeping a direct reference when that is enough.
For a strictly local synchronous scope, a name adds little. It becomes useful when separate parts
of an application or inspection tools need to locate the same active scope.

Crystallizer must also preserve named lesser conduit structure for later reconstruction. The saved
values describe names, structural roles and relationships; previously created instance data is outside
this feature. Restore must recreate the lesser under the right parent and shared Spellbook.

## MRP Alignment
Define naming, lookup, ownership, pooling and projection/persistence semantics as one coherent
contract. Do not ship an index that outlives the scope or silently turns ephemeral lessers into roots.

## Ticket Contract
- ENTRY_GATE: Owner requested an epic and cross-system discovery; existing naming evidence is recorded.
- EXECUTION_BOUNDARY: Planning and source-backed discovery across conduit/frame/cloud/pooling,
  Crystallizer, Nexus, DevOps, consumers, tests and public documentation.
- DEPENDENCIES: Four draft stories below and the linked cross-system discovery task.
- EXIT_GATE: Agreed contracts, approved implementation, verified stories and owner acceptance.
- FAILURE_ESCALATION: No runtime edits until naming/mode/lifecycle and persistence decisions are approved.

## Goals
- Optional names identify live lesser conduits without changing their lesser status or existing lifetimes.
- ConduitCloud can locate an eligible named lesser as the same live object.
- Returning a named lesser to its pool unregisters its discovery entry and clears its assigned name.
- Unnamed lessers skip cloud registration and unregistration; only named conduits enter cloud discovery.
- Establish whether naming/discovery should work in automatic and dynamic mode; the owner is open to both.
- Crystallizer saves and restores named lesser conduit structure without restoring created runtime objects.
- Make Nexus and other consumers distinguish discoverable lesser scopes from structural roots.

## Non-Goals
- Autofac-style InstancePerMatchingLifetimeScope or a new Existence mode.
- Scope promotion, new bindings, peer links, or compiler changes solely to obtain a name.
- A new lease/handle or live-object snapshot protocol, distributed discovery, or post-cleanup object-use guarantees.
- Silent changes to frame root accounting, permissions, recording policy, or release workflows.

## Current Verified Baseline
- Normal roots are named and frame-unique. conjure() defaults to default; both automatic and dynamic
  roots are discoverable through the frame-owned cloud.
- Upgrade(name) creates a named normal root and requires dynamic mode.
- Lesser creation currently accepts logger only. Initialization forces any supplied lesser name to None.
  The separate post-init setter permits an unregistered label; that setter path was used by the pool probe.
  Pooled acquisition bypasses initialization, and pool preparation currently does not clear that label.
- ConduitCloud borrows frame root-only maps, so its existing registry is not a generic scope directory.
- SpellSpace has no naming API. Scope storage is selected by Existence and identities, not names.
- Three naming/upgrade integration tests and an isolated name/lookup probe passed.
- Evidence owner: tickets/tasks/2026-09-06_named_conduit_semantics_task.md.

## Requirements
- Preserve the unnamed creation path and existing meld paths; naming work belongs at scope boundaries.
- Lesser names are supplied only when making the lesser through its creation API. Once returned,
  a lesser cannot be named or renamed; internal pool reset clears the name at the end of that use.
- Prewarmed shells remain unnamed. The creation call initializes the selected shell's optional name
  and discovery entry for the caller, whether the shell was already pooled or allocated on a miss.
- Cloud discovery retains named conduits only. Unnamed scope acquisition/release skips cloud registry work.
- Before a named lesser becomes available in the pool, unregister its discovery entry and clear its name.
  Apply new-name assignment to both fresh construction and pooled acquisition.
- Decide the namespace explicitly: frame-wide uniqueness versus parent-qualified names is still open.
- A cloud lookup returns a borrowed live conduit; it does not extend the owner's lifetime.
- Scope registration is not root registration and does not grant normal-conduit operations.
- Name publication must follow successful scope acquisition; cleanup/pool return must remove it before reuse.
- A collision or failed acquisition must not strand a registered name or corrupt the pool/parent relation.
- Root cleanup, explicit lesser cleanup, permanent destruction and upgrade each need defined index transitions.
- Any Nexus/Crystallizer inclusion, filtering and replay policy must be explicit, not an incidental effect
  of broadening an existing enumeration.
- Record named lesser structure through passive emissions after its name and actual parent are established.
- Add conduit-level record removal and folding for released scopes without evicting their shared book.
- Preserve sealed historical checkpoints while later checkpoints reflect release and reuse under new names.
- Restore roots explicitly and lessers in parent order using fresh identity translation and public creation verbs.
  Both replay drivers must preserve one shared book/root and the recorded child hierarchy.
- Define required unnamed ancestry and formation closure so a named descendant returns to its original place.
- Use a forward-safe record version: old root-only readers must not misinterpret child-bearing payloads.
- Reuse existing Nexus name/state/parent/root fields. Keep descriptor updates, compiled id membership and
  live-object lookup coherent; cloud registration alone does not update published named-query paths.

## Cross-System Impact Map (Source-Backed Initial Discovery)

| Surface | Current evidence | Design implication |
| --- | --- | --- |
| Conduit / pool | Init clears lesser names; post-init setter labels survive pooled reuse. | Named scopes unregister/clear before pool return; unnamed scopes skip cloud work. |
| Frame / Cloud | Cloud borrows root maps; Aether APIs read those maps directly. | Separate scope discovery from root ownership and preserve explicit root queries. |
| Automatic / dynamic | Both modes create lessers and expose root cloud lookup. | Recommend discovery in both modes without changing graph-mutation gates. |
| Nexus records | Name/state/parent/root fields exist; frame summaries snapshot cloud names. | Reuse fields and update per-scope metadata plus affected frame summaries. |
| Nexus projections | Live descriptor reference, detached allowed-id sets; missing compiled ids can raise. | Separate same-id updates from membership changes and pooled-record removal. |
| Nexus commands | ACL-checked named lookup ends at root-only Aether; static raw access is refused. | Decide explicit lesser-aware lookup without bypassing existing permissions. |
| Crystallizer capture | Only dynamic normal conduits emit; current twin lacks immediate parent; no conduit-only tombstone. | Required named-lesser structure, parent edges and release/removal chronology. |
| Crystallizer replay | First row for a book becomes its root; no lesser reconstruction in either driver. | Explicit root selection and parent-ordered child reconstruction. |
| Formations/versioning | Conduit slice has one anchor; old readers accept same-major unknown fields. | Ancestor/descendant closure and forward-safe child-record versioning. |
| Restore collisions | Admission/replay call cloud.has_conduit_name. | Choose whether live lesser names reserve the same namespace as restored roots. |
| Clusters / transfer | Cluster membership requires normal; transfer enumerates root Aether ids. | Naming grants neither membership nor root/Spellbook ownership. |

Detailed source ranges, earlier probe results and the deeper 2026-09-07 trace are in the discovery task.

## Confirmed Contract Direction
- Names are supplied only in the lesser-creation call, including use of a prewarmed shell.
- Only named conduits enter cloud discovery. Named release unregisters and clears before pool reuse;
  unnamed scope cycles skip cloud registry work.
- Crystallizer must save and restore named lesser structure. Created-instance state is outside this feature.

## Remaining Design Proposals (Not Yet Owner-Approved)
- Optional named lesser discovery in both automatic and dynamic mode.
- Frame-wide unique active cloud names, reusable after the old scope unregisters. This preserves
  unambiguous bare-name lookup; parent-qualified names remain an alternative if the owner wants repeats.
- Root ownership, existing Existence modes, dynamic mutation gates and static-room restrictions remain.
- Reuse the existing conduit-twin family with explicit lesser parent semantics and compatible old-root input.
- Preserve required ancestry for named descendants; supporting unnamed nodes can remain outside cloud discovery.
- Prefer shared per-book hierarchy replay where it can satisfy both sequential and parallel driver contracts.
- Cloud lookup returns the live borrowed Conduit, not a new object, lease or ownership transfer.

## Decisions Before Implementation
1. Confirm both-mode naming/discovery rather than dynamic-only.
2. Confirm frame-wide active-name uniqueness versus parent-qualified names.
3. Decide cloud listing/root-filter behavior and publication ordering; lesser naming is creation-only.
4. Settle required unnamed ancestry, formation closure, record versioning and restore collision rules.
5. Decide whether pooled Nexus records are removed or retained as unnamed pooled shells, and whether
   existing projections require explicit refresh for membership changes. Specify the ACL-preserving named resolver.

## Stories
- [ ] STORY-2026-09-06-named-conduit-directory-lifecycle
  - tickets/stories/2026-09-06_named_conduit_directory_lifecycle_story.md
- [ ] STORY-2026-09-06-named-conduit-crystallizer-contract
  - tickets/stories/2026-09-06_named_conduit_crystallizer_contract_story.md
- [ ] STORY-2026-09-06-named-conduit-nexus-consumers
  - tickets/stories/2026-09-06_named_conduit_nexus_consumers_story.md
- [ ] STORY-2026-09-06-named-conduit-validation-docs
  - tickets/stories/2026-09-06_named_conduit_validation_docs_story.md

## Cross-Cutting Tasks
- Prior naming evidence: tickets/tasks/2026-09-06_named_conduit_semantics_task.md (review).
- Initial impact discovery: tickets/tasks/2026-09-06_named_conduit_cross_system_discovery_task.md (review).
- Implementation map: tickets/tasks/2026-09-07_named_conduit_implementation_map_task.md (review; planning only).

## Milestones
- [x] Capture the existing naming/registration/lifetime findings.
- [x] Initial cross-system trace distinguishes discovery changes from root/persistence/permission boundaries.
- [x] Record owner requirements for creation-only naming, conditional cloud cleanup and structural persistence.
- [x] Trace conduit record/capture/fold, both replay drivers and targeted Nexus publication/name consumers.
- [ ] Obtain remaining decisions on modes, namespace, ancestry/versioning and Nexus lifecycle integration.
- [ ] Create precise implementation tasks and required patch contracts after decisions.
- [ ] Implement, verify, document and obtain acceptance.

## Acceptance Criteria
- Automatic/dynamic behavior and name uniqueness are documented and tested according to the agreed policy.
- Named lesser lookup returns the intended scope without root promotion or instance-lifetime changes.
- Cleanup removes discovery immediately; pool reuse does not inherit an earlier logical scope's name.
- An unnamed lesser performs no cloud registration or unregistration during its scope cycle.
- Roots, names, ids and hierarchy remain coherent through duplicate attempts, nesting and upgrades.
- A saved active named lesser restores with its name, lesser role and original parent/shared-book structure.
- Released scopes are absent from later checkpoints; earlier sealed checkpoints retain their saved structure.
- Same-id pool release/reacquisition, formation closure, both replay drivers and rollback are coherent.
- Restored scope stores contain no serialized prior creations or their mutable instance data.
- Old root-only records remain readable; incompatible old readers refuse new child-topology records safely.
- Nexus names and compiled membership remain coherent; DevOps/root-only consumers retain their intended semantics.
- No speculative hot-path checks, unapproved snapshots, or changes to the compiler/lifetime model.
- Documentation and focused/full validation evidence match the implemented contract.

## Risks / Open Decisions
- Broadening the root map changes frame ownership and every root enumeration consumer.
- A discoverable lesser may be mistaken for a bindable/linkable root by commands or clients.
- Pooled conduit identity can outlive one logical scope; stale labels/projections/records need careful handling.
- A named child below an unnamed parent needs recorded ancestry to preserve its original structure.
- Merely adding child emissions can cause an old loader to select a lesser row as a root and omit other children.
- Removing a Nexus record while its id remains compiled-visible can make viewer reads fail.
- Names do not make user-owned objects thread-safe or keep a scope alive after owner cleanup.
- Enforce creation-only lesser naming across the existing public setter; define type/empty-name rules.

## Validation / Rollout
Use targeted source traces and isolated probes during discovery. Later validate naming and cleanup
in both modes, duplicate names, parent/child teardown, pool reuse, lookup and existing lifetime behavior.
Validate required structural persistence, current/historical scope state, parent ordering and compatible readers.
Add Nexus lifecycle/projection tests for the selected integration. No benchmark claims without measurement.
No commits, pushes, asset regeneration or runtime implementation are authorized by this planning epic.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner authorized the epic and cross-subsystem discovery, not implementation.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-06T17:17:54Z
  TYPE: DECISION
  CLAIM: Owner wants an epic with value assessment, potential automatic/dynamic support,
    unregister/clear-on-pool behavior and Crystallizer/Nexus/other-subsystem implications.
    These are design candidates; implementation approval has not been given.
  EVIDENCE:
  - tickets/tasks/2026-09-06_named_conduit_semantics_task.md
  - Owner's epic/discovery request in the current conversation.
  IMPACT: Preserve prior findings and investigate the whole lifecycle before selecting implementation.
  NEXT: Trace discovery versus root ownership, then Nexus and Crystallizer consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:44:52Z
  TYPE: DECISION_REQUEST
  CLAIM: Initial impact discovery supports optional discovery in both modes, with active frame-wide
    names and ephemeral lesser lifetimes as the recommended contract. Nexus already has suitable
    fields but needs lifecycle-consistent publication; Crystallizer should keep lesser exclusion
    unless the owner explicitly wants child replay. Existing root queries and permission gates stay.
  EVIDENCE:
  - tickets/tasks/2026-09-06_named_conduit_cross_system_discovery_task.md
  - tickets/stories/2026-09-06_named_conduit_directory_lifecycle_story.md
  - tickets/stories/2026-09-06_named_conduit_crystallizer_contract_story.md
  - tickets/stories/2026-09-06_named_conduit_nexus_consumers_story.md
  IMPACT: The feature has a bounded value proposition and a cross-system contract. It is not yet
    authorized for implementation; five explicit choices are listed above.
  NEXT: Owner selects naming/discovery semantics, then implementation tasks can be defined precisely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:08:52Z
  TYPE: DECISION
  CLAIM: Owner confirmed named-only cloud discovery and conditional lifecycle work: a named lesser
    unregisters and clears its name when finished, before pool reuse; an unnamed lesser skips cloud
    unregistration. Registry overhead on the named path is accepted. Constructor source confirms
    that lesser initialization currently forces None, so the old label probe must be described as
    a separate post-init setter observation. Fresh and pooled acquisition both need the new contract.
  EVIDENCE:
  - Owner's 2026-09-07 lifecycle clarification in this conversation.
  - src/melder/aether/conduit/conduit.py:1365-1384
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:1588-1630
  - src/melder/aether/conduit/conduit.py:2227-2385
  - src/melder/aether/conduit/conduit_pool.py:106-161
  IMPACT: The named/unnamed lifecycle split is settled. Mode, namespace, setter/publication ordering,
    root/listing semantics and Nexus/Crystallizer choices remain open; overhead has not been measured.
  NEXT: Resolve the remaining contract variables before implementation tasks and patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:14:34Z
  TYPE: DECISION
  CLAIM: Owner selected creation-only lesser naming. Premade pool shells are initialized for an
    application scope when the lesser-creation call hands one out; that call is the only naming
    point. Later naming/renaming is excluded. Prewarming prepares unnamed shells and does not
    reserve application names. Release still unregisters/clears only the named path before reuse.
  EVIDENCE:
  - Owner's creation-only naming clarification in this conversation.
  - src/melder/aether/conduit/conduit.py:1161-1211
  - src/melder/aether/conduit/conduit.py:2227-2385
  - src/melder/aether/conduit/conduit_pool.py:106-161
  IMPACT: Remove the public lesser setter choice from the unresolved design. The implementation
    must use the actual specialized pool path and preserve prewarming and unnamed scope behavior.
  NEXT: Resolve namespace, mode, publication order and consumer semantics before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:46:34Z
  TYPE: DECISION
  CLAIM: Owner requires named lesser conduits in structural capture/replay and explicitly excludes
    previously created object state. The earlier ephemeral-only recommendation is superseded.
    Deep source work maps emitter/twin fields, record/journal/checkpoint, conduit-level removal gap,
    formation closure, root-only replay selection, both drivers and reader-version safety. Nexus
    already has descriptive fields, but published named queries and compiled membership do not
    automatically follow cloud registration. All four stories now use the required structural scope.
  EVIDENCE:
  - Owner's structural persistence clarification in this conversation.
  - tickets/tasks/2026-09-06_named_conduit_cross_system_discovery_task.md
  - tickets/stories/2026-09-06_named_conduit_crystallizer_contract_story.md
  - tickets/stories/2026-09-06_named_conduit_nexus_consumers_story.md
  IMPACT: Required persistence is core feature work, not a deferred optional extension. Remaining
    choices concern faithful ancestry, mode/namespace, compatibility and Nexus lifecycle behavior.
  NEXT: Review those concrete structural and consumer contracts before implementation tasks and patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T17:22:45Z
  TYPE: PLAN
  CLAIM: Owner requested all implementation steps and a general difficulty assessment without making
    the change. The linked mapping task now contains twelve ordered phases with affected paths,
    dependency order, open contracts, validation and rollback. Source review identified an existing
    upgrade book-ownership concern that must be handled as a bounded prerequisite.
  EVIDENCE:
  - tickets/tasks/2026-09-07_named_conduit_implementation_map_task.md
  IMPACT: Planning is reviewable without runtime implementation. The map preserves structural
    persistence and creation-only naming and does not treat open choices as owner-approved.
  NEXT: Review the implementation map and remaining contract choices before authoring execution patches/tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Noting Behavior
Keep program choices and cross-story implications here; detailed source evidence stays in the discovery task.

## Context / Handoff Summary
Initial discovery is recorded, with exact source locations in the cross-system task and four draft stories.
The existing lesser constructor forces names to None; prior two-mode probing used the post-init setter.
Owner confirmed creation-only naming, named-only cloud discovery, conditional unregister/name clearing
before pool reuse and named-lesser structural persistence/replay. The deep source trace is recorded;
the earlier ephemeral-only recommendation is superseded. Created-instance data is outside this feature.
Remaining decisions are mode/namespace, required unnamed ancestry and formation closure, record-version
safety and Nexus pooled-record/compiled-membership handling. The 2026-09-07 implementation-map task
contains the proposed twelve-phase sequence, source/test/doc targets and the upgrade ownership prerequisite.
