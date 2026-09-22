# Task: Refresh named lesser conduit design after graduation and pool repairs

## Metadata
- Task ID: TASK-2026-09-22-refresh-named-lesser-conduit-plan
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-22T20:51:02Z
- Updated: 2026-09-22T21:16:32Z

## Objective
Resume the owner's selected named-lesser epic using current graduation and pool behavior.
Refresh its first implementation boundary and distinguish settled requirements from open contracts.

## Ticket Contract
- ENTRY_GATE: Owner selected named lesser conduits after the completed hook/graduation work.
- EXECUTION_BOUNDARY: Existing epic/stories/implementation map, relevant component and source reads,
  and planning updates. No runtime edits, version changes or generated assets in this refresh.
- DEPENDENCIES: Completed graduation and pooled-hook epics; existing named-conduit implementation map.
- EXIT_GATE: Current first-slice plan, remaining decisions and source evidence recorded for review.
- FAILURE_ESCALATION: Identify unresolved naming/replay semantics before implementation begins.

## Scope Boundaries
- In: Creation-only names, named-only cloud discovery, release/reset, root ownership separation,
  Crystallizer structural replay and Nexus consistency; begin with the directory/pool boundary.
- Out: Application-instance persistence, new Existence modes, unrelated epics and build generation.
- Existing requirements stand: unnamed cycles skip cloud work; named release unregisters and clears
  before pool reuse; saved lesser structure must replay without restoring prior created instances.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Deeper source boundaries and regression matrix recorded; final concurrency choices remain explicit.

## Steps / Checklist
- [x] Read the four stories and existing implementation map.
- [x] Read relevant component documentation and current directory/pool/graduation source boundaries.
- [x] Refresh the epic's prerequisite and first implementation slice.
- [x] Present remaining material decisions with concrete recommendations.
- [x] Trace shared-name admission, reader/writer locks, pooled failures and promotion rollback.
- [x] Trace record removal/folding, ancestry/formation closure and both restore drivers.
- [x] Trace Nexus publication, compiled membership and public named lookup consumers.
- [x] Record a concrete implementation/test matrix with unresolved behavior explicitly identified.

## Deliverables
- Updated epic and source-backed first-slice plan recorded here.

## First Implementation Slice
Preserve the existing positional logger argument and add keyword-only
`name: Optional[str] = None` to `Conduit.create_lesser_conduit`.

1. Give Cloud a named-conduit directory; retain frame-owned root maps and the root map used
   by clusters. Root and lesser insertion share atomic name-collision admission.
2. Initialize names for both fresh and pooled acquisition. Prewarmed shells remain unnamed.
   Reject public post-creation lesser naming/renaming.
3. Unregister named scopes and clear names before idle publication, preserving creation disposal,
   descendant detach and hook restoration. Unnamed cycles skip cloud mutation; meld is unchanged.
4. Extend graduation name admission and rollback for existing lesser directory entries, including
   same-name promotion. Reuse the delivered new-Book conjure route.
5. Add tests for fresh/prewarmed paths, A -> B -> unnamed reuse, root/lesser collisions, nested
   cleanup, callback failures, overflow, and same/different-name graduation.

Before runtime edits, read complete changed units and verified graph slices, author the required
architecture/component/control-flow patch contracts, and map acceptance cases to tests.
This slice does not finish the epic: structural persistence and Nexus integration are required.

## Accepted Defaults and Remaining Design
- Owner accepted: one exact frame-wide namespace shared by roots and active named lessers. Nonempty
  strings, no silent trimming/case changes, reusable after release.
- Owner accepted: allow naming/discovery in automatic and dynamic mode. Keep the existing dynamic-only
  recording policy unless the owner explicitly requests broader capture.
- Recovery: preserve named lessers and necessary unnamed ancestry, including actual parent edges.
  Supporting unnamed ancestors remain outside Cloud; no prior creations or instance state replay.
- Compatibility: RecordVersion is now 2.0.0. Child-topology payloads require a forward-safe major
  policy, provisionally 3.0.0, with older root-only records still readable by the new code.
- Hook ordering: current activation precedes parent attachment; post-create follows it. The
  implementation patch must define when name/directory visibility begins and how failure unwinds.
- Nexus: reuse current name/state/parent/root fields. Decide pooled-record retention/removal and
  compiled visibility together before the consumer story; current source accepts pooled records.

Frame-wide unique names and both-mode discovery are settled. The owner requests deeper implementation
investigation before coding; ancestry, compatibility and publication details must be source-backed.

## Required Reading for Resumption
Read the deeper investigation conclusions and latest Notes first. These identify changed assumptions,
source-backed integration points and the two remaining concurrency contracts before code edits.

## Deeper Investigation Conclusions

| Boundary | Implementation direction | Existing machinery to preserve |
| --- | --- | --- |
| Named directory | Cloud owns name/id discovery for named roots and lessers; frame registration bridges root names into the same collision authority. | Frame root maps, Aether root facades, DevOps Book ownership and cluster input remain root-only. |
| Acquisition | Assign the requested name on each use, in both fresh and pooled branches. Commit the directory entry with actual lineage attachment. | Positional logger compatibility, narrow parent lock, advisory lifecycle hooks and root-owned pool. |
| Release | Retire directory/record names before publishing the shell idle; preserve enough identity for removal before clearing fields. | Dispose current creations, detach descendants, restore local hooks and then return to pool. |
| Graduation | Allow the same object's existing name, reserve a different target safely, and restore the original entry on pre-attachment failure. | Fresh independent Book, retained creation stores, existing-conduit conjure and current post-attachment failure semantics. |
| Persistence | Add conduit removal through the existing facade/system/profile/journal/capture/fold chain. Include supporting parent topology as values. | Passive emissions, profile ownership, detached sealed history and fresh runtime identity translation. |
| Replay | Select the root explicitly; rebuild the lesser tree in the shared per-Book unit after staged binds/selections. | Both sequential and parallel drivers, global reverse-build teardown and normal public creation verbs. |
| Nexus | Republish current name/state/parent values; resolve the ACL-authorized published identity through a lesser-aware path. | Existing payloads, explicit Rift projection refresh, raw-object access restrictions and root-only operations. |

### Lock and Failure Constraints for the Patch
- Use short directory critical sections. Frame root mutation can enter the directory in the
  frame -> directory order; directory helpers must not acquire frame, conduit, ward or Nexus locks.
  Do not call disposal, lifecycle callbacks, recorder sinks or projection refresh under that lock.
- Do not replace the existing narrow parent attachment lock with one spanning ordinary creation.
  A named operation needs a proved publication/retirement ordering across parent cleanup and reuse.
- Advisory lesser-hook exceptions are suppressed today. Tests must preserve that behavior instead
  of introducing a new hook veto. Hook-caused lifecycle mutation is a separate reentrancy case.
- Disposal failure can abort soft cleanup before pool publication, after creation records detach.
  Tests must distinguish an incomplete cleanup from a successfully retired named scope.
- Root/Book registration and graduation have multiple early/final name checks. Every relevant
  check must use the same collision authority; an early check alone cannot prevent concurrent claims.
- Lookup returns a borrowed live conduit, not a lease. No new guarantees for a retained reference
  used after owner cleanup or pool reuse are proposed.

### Remaining Concurrency Contracts
1. Serialize named publication/removal sufficiently that delayed work for use A cannot overwrite
   name B after the same shell is reused. Define the critical section and failure boundary without
   calling Nexus/Crystallizer while holding a leaf directory lock or broadening the unnamed path.
2. Define named lifecycle behavior during live restore. Current LoadGate drains transaction
   sessions and does not cover ordinary lesser acquire/reset. A one-time wait/probe does not create
   a drained operation span. Either document required quiescence for this new structural surface
   or design bounded named-only admission; do not silently add a transaction to every pool cycle.

These are identified implementation choices, not verified guarantees or blockers requiring a policy bypass.

### Proposed Nexus Pool Policy
Retain an existing id's record on soft return as unnamed pooled_lesser with no parent. That avoids
breaking views whose compiled ids already include the shell, and later same-id payload replacement
can show the new name. A newly allocated id still needs the existing explicit projection refresh.
Do not automatically drain/refresh a Rift from inside its active create-lesser command.
Permanent record removal remains a separate missing-record/refresh case to test and specify.
Name lookup must bind authorization to the identity actually returned; a reused name must not
redirect an old authorized id to an unchecked replacement. Current conduit ACL rules are family-wide.

### Regression Matrix Before and During Implementation
| Area | Required observable cases |
| --- | --- |
| Directory | Root/lesser and lesser/lesser collision; parallel same-name claims; lookup by name/id; named list/count agreement; frame isolation. |
| Unnamed path | No cloud registration/removal, no new meld-path work, prewarming stays unnamed; measured warm-cycle baseline. |
| Pool use | Cold and prewarmed name assignment; A -> B -> unnamed reuse; no public rename; root and nested-parent cleanup; overflow destruction. |
| Failures | Bad input before mutation; parent cleanup during acquisition; advisory throwing hook; hook-induced cleanup; disposal failure/retry; publication failure before pool return. |
| Graduation | Same-name promotion, different-name promotion, collision before mutation, pre-attachment rollback and post-attachment root cleanup. |
| Checkpoints | Emit/remove, emit/remove/re-emit with one id, both within one window and across seals; older sealed snapshots unchanged. |
| Hierarchy | Named child beneath unnamed ancestry, siblings and nesting, exact shared Book/root, support-node retirement, old Book removal after graduation. |
| Replay | Both drivers, parent-first creation, fresh ids, empty restored creation stores, partial-failure unwind, malformed/cyclic/mismatched parents. |
| Formations | Root anchor includes intended named descendants; lesser anchor includes required root/ancestors; retargeting; strict collisions and explicit skip policy. |
| Compatibility | Older root-only input accepted, new child topology rejected by incompatible readers, no silent child-as-root interpretation. |
| Nexus | Precompiled pooled id A -> unnamed -> B; fresh-id refresh; permanent removal; denied ACL/static raw access; named lookup identity race; no in-command drain timeout. |
| Load concurrency | Named lifecycle racing a live load under the selected admission/quiescence policy; cohort workers retain replay access. |

Existing test files were located, not executed or claimed to cover these new contracts:
- tests/component/melder/aether/test_conduit_cloud_component.py
- tests/unit/melder/aether/test_conduit_cloud.py
- tests/unit/melder/aether/conduit/test_conduit_pool_multithreaded.py
- tests/component/melder/aether/conduit/test_conduit_upgrade_validate_before_mutate_regression.py
- tests/unit/melder/crystallizer/persistence/test_persistence_profile.py
- tests/unit/melder/crystallizer/crystal_loader_system/test_restore_fold_safety.py
- tests/unit/melder/crystallizer/crystal_loader_system/test_restore_plan_levels.py
- tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
- tests/unit/melder/aether/test_command_system_direct.py
- tests/unit/melder/aether/test_frame_viewer_projection.py

### Source Reading Pointers
- Four stories and the completed implementation map linked from the parent epic.
- Verified src_components slices: AethericFrame Services; Conduit Runtime; Crystallizer Root;
  Nexus Descriptor And ACL Managers. Old C2 Cloud _registry/mutation-method claims are stale.
- src/melder/aether/aetheric_frame/conduit_cloud.py (whole file read here)
- src/melder/aether/conduit/conduit_pool.py (whole file read here)
- src/melder/aether/aetheric_frame/aetheric_frame.py:125-416
- src/melder/aether/conduit/conduit.py:196-452, 518-945, 1159-1209, 1363-1383
- src/melder/aether/conduit/conduit.py:1554-1649, 2087-2305, 2395-2591
- src/melder/aether/conduit/conduit_ward/conduit_ward.py:381-435, 1147-1189
- src/melder/aether/spellbook/spellbook.py:6635-6858
- src/melder/crystallizer/crystals/conduit_crystal.py
- src/melder/crystallizer/persistence/record_version.py
- src/melder/crystallizer/crystal_loader_system/restore_engine.py:1827-1878
- src/melder/nexus/frame_descriptor_manager.py:222-497

## Validation
Runtime tests: Not run; discovery and planning only.
Planning checks passed: six related ticket links resolve, review routing matches, Notes/handoff
headings are unique, and the task has no conflict markers or trailing whitespace. Deep-pass checks also
verified current source citations, all ten test-reading targets and epic/story/task whitespace.

## Risks / Rollback Notes
The September 7 plan predates independent graduation and root-owned hook baselines. Reusing old
line ranges or treating the cloud's root maps as generic scope ownership would mis-scope this change.

## Applicable Anti-Patterns
- [x] No implementation from old source citations alone.
- [x] No scope promotion or extra Spellbook just to name a lesser.
- [x] No build generation under the existing owner hold.

## Artifact Links
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Record findings after each complete source boundary, with explicit evidence and a single next step.

## Notes
- DATETIME: 2026-09-22T20:51:02Z
  TYPE: DECISION
  CLAIM: The owner selected named lesser conduits as the next epic. Its old plan names graduation
    ownership as a prerequisite, now delivered by the September 22 graduation epic. Refresh the
    existing plan against that work and the pool-hook reset contracts before any runtime changes.
  EVIDENCE:
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md:287-318
  - tickets/epics/completed/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md:3-23
  - tickets/epics/completed/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md
  IMPACT: Graduation repair is no longer pending; naming still needs its own scope-discovery lifecycle.
  NEXT: Read the existing implementation map and four stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T20:51:48Z
  TYPE: FACT
  CLAIM: The existing map already separates frame root ownership from a named cloud directory,
    and requires child-aware capture/removal/replay before enabling new structural writers.
    Its four stories preserve creation-only names and unnamed-cycle fast paths. Graduation repair
    is delivered separately; the remaining first slice is shared-name collision and scope lifecycle.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-07_named_conduit_implementation_map_task.md:111-154
  - tickets/stories/2026-09-06_named_conduit_directory_lifecycle_story.md:26-43
  - tickets/stories/2026-09-06_named_conduit_crystallizer_contract_story.md:26-48
  - tickets/stories/2026-09-06_named_conduit_nexus_consumers_story.md:22-39
  IMPACT: Reuse the existing story split and map; refresh changed source locations and transitions.
    Do not re-open the completed graduation implementation or reduce persistence to an optional add-on.
  NEXT: Verify component indexes and read the current directory/root/pool source boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T20:53:10Z
  TYPE: FACT
  CLAIM: Cloud currently borrows the frame's root id/name maps; its lookups have no dynamic-mode
    gate. Cluster creation also receives the borrowed root-id map, and cluster membership enforces
    normal state. Frame root registration additionally publishes Spellbook ownership to DevOps.
    A lesser therefore cannot be added to the existing root map just to become discoverable.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:125-228
  - src/melder/aether/aetheric_frame/aetheric_frame.py:340-412
  - src/melder/aether/aetheric_frame/conduit_cloud.py:108-167
  - src/melder/aether/aetheric_frame/conduit_cloud.py:321-553
  - src/melder/aether/aetheric_frame/conduit_cloud.py:607-708
  IMPACT: Keep root ownership and cluster input separate from named-scope discovery. Root and lesser
    name admission need the same collision authority. Component C2 claims about _registry and
    _register_conduit/_unregister_conduit are stale; those members are absent from current Cloud.
  NEXT: Read Conduit acquisition, cleanup and graduation methods to fix the lifecycle insertion points.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T20:54:40Z
  TYPE: FACT
  CLAIM: Current lesser acquisition still has only logger input and two hook/no-hook branches.
    Both pop the root pool directly, and reuse bypasses construction. Pool return disposes Spaces
    and creations, recursively detaches children, restores temporary hooks, then appends the idle
    shell. It neither clears the name nor republishes Nexus. Initial lesser construction clears
    names; the public name setter still permits assigning an unregistered label afterward.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:549-578
  - src/melder/aether/conduit/conduit.py:1159-1206
  - src/melder/aether/conduit/conduit.py:1363-1382
  - src/melder/aether/conduit/conduit.py:1554-1628
  - src/melder/aether/conduit/conduit.py:2395-2591
  - src/melder/aether/conduit/conduit_pool.py:106-161
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:381-435
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1147-1189
  IMPACT: Naming belongs to per-use acquisition/reset, alongside the existing pool lifecycle;
    add no naming checks to meld. Preserve the actual parent edge separately from shared root
    ownership. The API docstring mentions name/hooks that its current signature does not accept.
  NEXT: Confirm the existing-conduit conjure registration boundary, then refresh persistence and Nexus contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T20:55:57Z
  TYPE: FACT
  CLAIM: Graduation now constructs a fresh Book, prepares the existing conduit, and calls the
    Book-owned conjure route. That route replaces lookup/hook ownership and registers the root.
    Its early and final name checks still inspect root-only names; named-lesser promotion must
    extend these collision checks and preserve or replace the same object's directory entry.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2087-2305
  - src/melder/aether/spellbook/spellbook.py:6635-6858
  IMPACT: Remove the ignored-Book-return repair from the active prerequisite list. Keep named
    promotion admission/rollback in scope; successful and failed promotion must update discovery
    without transferring old definitions or reintroducing shared Book ownership.
  NEXT: Read the current conduit crystal/root replay and Nexus publication methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T20:59:36Z
  TYPE: FACT
  CLAIM: ConduitCrystal remains root-oriented and current emission omits immediate parent.
    Restore selects the first matching conduit row for a Book. RecordVersion is 2.0.0 and
    rejects only newer majors. Nexus carries actual parent/root/name/state, accepts pooled
    records, and separates root inventory from cloud names in frame summaries.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:406-450
  - src/melder/crystallizer/crystals/conduit_crystal.py:92-159
  - src/melder/crystallizer/crystals/conduit_crystal.py:282-306
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1827-1878
  - src/melder/crystallizer/persistence/record_version.py:76-78
  - src/melder/crystallizer/persistence/record_version.py:142-181
  - src/melder/nexus/frame_descriptor_manager.py:259-495
  IMPACT: Readers, removal/folding and parent replay must precede new child emissions. No new
    Nexus naming flag or payload family is justified by this trace.
  NEXT: Review frame-wide uniqueness and both-mode naming, then open the first implementation patch/task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T21:03:06Z
  TYPE: DECISION
  CLAIM: Owner accepts the proposed naming logic and requests deeper implementation investigation.
    Frame-wide uniqueness across roots/lessers and both-mode discovery are now settled; recording
    retains the existing dynamic policy. Continue reading real lifecycle/lock/record/consumer code.
  EVIDENCE:
  - Owner's current reply accepting the logic and directing implementation investigation.
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md
  IMPACT: Do not re-ask these defaults. Investigate correctness and record concrete implementation
    boundaries before runtime edits; existing generation hold still applies.
  NEXT: Trace registry ownership and lifecycle lock/callback ordering, then record/replay consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T21:05:50Z
  TYPE: FACT
  CLAIM: The deeper lifecycle trace corrects an earlier failure assumption: Conduit creation hooks
    catch/log Exception and continue, so a raising lesser hook is not a veto or rollback trigger.
    Ordinary conjure instead propagates its activation path failures. Creation-store reset detaches
    disposal records and can raise ExceptionGroup before Conduit reaches ward detach/pool return.
    Aether root facades and ownership-transfer enumeration read root maps directly.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:6585-6631
  - src/melder/aether/spellbook/spellbook_creation_system.py:202-288
  - src/melder/aether/spellbook/spellbook_creation_system.py:857-906
  - src/melder/aether/spellbook/spellbook_creation_system.py:955-1018
  - src/melder/aether/conduit/creations/creations.py:776-825
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:250-379
  - src/melder/aether/aether.py:1643-1982
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:752-815
  IMPACT: Preserve advisory hook semantics. Test throwing hooks separately from actual registration,
    publication and disposal failures. Root facades/cluster inputs stay root-only; Cloud uses a
    dedicated discovery surface. New directory locks must not cover callbacks, disposal or publication.
  NEXT: Trace record replacement/removal and same-id journal folding before choosing release publication order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T21:09:18Z
  TYPE: FACT
  CLAIM: Checkpoints capture each identity's final payload within a journal window, and folding
    reapplies that payload at each journal event. A conduit-specific removal must be added across
    facade, system, profile, capture and fold. Book removal cannot serve lesser release. Formation
    capture currently includes only the anchored conduit, not its ancestor/descendant closure.
    Both restore drivers already share _replay_one_book, so parent-ordered lesser reconstruction
    can live in that common book unit after root/staged/selection setup, without separate drivers.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:1250-1296
  - src/melder/crystallizer/crystallizer.py:1522-1575
  - src/melder/crystallizer/persistence/persistence_system.py:245-277
  - src/melder/crystallizer/persistence/persistence_system.py:337-407
  - src/melder/crystallizer/persistence/persistence_system.py:939-1010
  - src/melder/crystallizer/persistence/persistence_profile.py:230-332
  - src/melder/crystallizer/persistence/persistence_profile.py:649-719
  - src/melder/crystallizer/persistence/persistence_profile.py:1028-1307
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:713-1035
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1086-1318
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1714-1825
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2684-2706
  IMPACT: Required cases are emit/remove; emit/remove/re-emit under the same pooled id; the same
    sequences across seals; child-parent support; old Book removal after graduation; rollback of a
    partially rebuilt hierarchy. No new general scheduler or object-state serializer is needed.
    Name collision admission already consults Cloud, but skip_existing's root-name=None fallback
    actually becomes default through normal conjure; do not extend that misleading fallback to children.
  NEXT: Trace Nexus name resolution and compiled ACL membership, then write the cross-system matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T21:12:12Z
  TYPE: FACT
  CLAIM: Nexus named getters authorize a published id then resolve by root-only Aether name.
    The shared id getter already supports lesser traversal while enforcing room/frame/conduit ACLs.
    Current conduit ACL compilation includes published ids by family rules, not by name or state.
    Projections borrow live descriptors but own compiled id sets; removing a known record can make
    ViewFrame fail, whereas replacing the same id updates payload reads without recompilation.
    An automatic synchronous Nexus refresh inside a create-lesser command would wait for that
    command's own active RiftGate ticket until timeout; no current naming code performs that refresh.
  EVIDENCE:
  - src/melder/nexus/rift/command_system/command_system.py:194-249
  - src/melder/nexus/rift/command_system/command_system.py:1010-1107
  - src/melder/nexus/rift/command_system/command_system.py:1280-1427
  - src/melder/nexus/rift/command_system/capability_command_system.py:198-293
  - src/melder/nexus/rift/command_system/capability_command_system.py:428-462
  - src/melder/nexus/rift/command_system/codegen_command_system.py:272-308
  - src/melder/nexus/acl/frame_acl_compiler.py:340-382
  - src/melder/nexus/acl/frame_acl_compiler.py:687-767
  - src/melder/nexus/rift/projection/command_projection.py:65-164
  - src/melder/nexus/rift/projection/view_projection.py:65-151
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:412-464
  - src/melder/nexus/rift/frame_viewer/view_frame.py:2182-2303
  - src/melder/nexus/nexus.py:1297-1363
  - src/melder/nexus/nexus.py:2595-2727
  IMPACT: Prefer retained unnamed pooled records for soft return, with real pooled state and cleared
    parent/name metadata; fresh ids use the established explicit projection refresh. Permanent
    removal still needs a precise missing-record policy. Named getters must resolve the authorized
    identity and recheck its current name/liveness, rather than redirecting a reused name to an
    unchecked new id. Keep static-room raw access restrictions. Forward name only where creation exists.
  NEXT: Finish the lock/load-admission and structural-preflight constraints; record the implementation matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T21:14:27Z
  TYPE: FACT
  CLAIM: Load authority drains transaction sessions; ordinary lesser creation/reset opens no such
    session. The transaction enum has no lesser lifecycle kind. Naming therefore cannot claim that
    existing LoadGate authority serializes named cycles automatically. Frame cleanup holds its
    frame lock while cascading into conduit cleanup; frame-summary publication takes descriptor
    manager then frame locks, so adding publication under a held directory lock creates new ordering risks.
    Existing preflight checks peer links and frame presence, not required lesser-parent topology.
  EVIDENCE:
  - src/melder/aether/aether.py:1324-1404
  - src/melder/utilities/synchronization/load_gate.py:422-479
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:328-385
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:62-78
  - src/melder/aether/conduit/conduit.py:518-578
  - src/melder/aether/conduit/conduit.py:2395-2591
  - src/melder/aether/aetheric_frame/aetheric_frame.py:231-338
  - src/melder/nexus/frame_descriptor_manager.py:259-340
  - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py:273-398
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py:111-217
  - src/melder/crystallizer/crystal_analysis/preflight/link_integrity_strategy.py:73-103
  - src/melder/crystallizer/crystal_analysis/preflight/frame_posture_strategy.py:75-110
  IMPACT: Use short leaf directory critical sections with no user callbacks, sink publication or
    frame acquisition inside them. Publication ordering across cleanup/reuse needs an explicit
    named-path contract; a cloud dictionary lock does not make all subsystems atomic. Keep unrelated
    root lock inversions and transaction redesign out of scope. Decide named-cycle/load concurrency
    before claiming restore isolation; a one-time gate probe alone would not close the race.
  NEXT: Record bounded implementation steps and the exact regression matrix, leaving unresolved
    concurrency policy visible rather than silently adding global transactions to unnamed scopes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Deeper source investigation is recorded with an implementation and regression matrix. Settled:
frame-wide unique names, both-mode discovery, existing dynamic recording, creation-only naming,
pool retirement and required structural replay. No runtime edits, tests or generation.

New findings: lesser hooks suppress exceptions; disposal may abort pool return; checkpoints use
per-window final payloads; both replay drivers share the Book unit; Nexus retains compiled id sets;
automatic refresh inside a live command self-waits; LoadGate does not cover ordinary lesser cycles.
Next: finish named publication/retirement ordering and live-load coordination in the first patch
contract, then add focused regressions and implement the directory/lifecycle slice. Preserve the
four-story program and do not claim these source traces are concurrency or performance measurements.
