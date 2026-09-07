# Task: Map named conduit implementation without changing runtime code

## Metadata
- Task ID: TASK-2026-09-07-named-conduit-implementation-map
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Story: none (cross-cutting implementation planning)
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-07T17:02:25Z
- Updated: 2026-09-07T17:22:45Z

## Objective
Assess general implementation difficulty and produce an ordered, source-backed implementation map
covering runtime naming, pooling, structural recording/replay, Nexus, validation and documentation.
The owner explicitly requested planning without implementing the feature.

## Ticket Contract
- ENTRY_GATE: Owner requested the implementation map; the epic and prior source discovery are available.
- EXECUTION_BOUNDARY: Read source/tickets and write ContextCompass planning records only.
- DEPENDENCIES: Parent epic, its four stories, and the cross-system discovery task.
- EXIT_GATE: Difficulty, remaining decisions, affected paths, ordered steps, validation and rollout are mapped.
- FAILURE_ESCALATION: Keep unverified details explicit; no runtime/test/codegen edits or execution of the feature plan.

## Scope Boundaries
- In scope: implementation planning, scoped evidence verification and durable planning records.
- Out of scope: runtime implementation, test implementation/execution, asset regeneration, commits and publication.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: The owner-requested difficulty assessment and ordered implementation map are complete and checked.

## Steps / Checklist
- [x] Re-anchor to the confirmed epic requirements and source discovery.
- [x] Check remaining root-registration/upgrade boundaries and inventory relevant test/doc surfaces.
- [x] Write the complete implementation sequence, dependencies, decisions and verification requirements.
- [x] Check the planning document and synchronize ticket/board routing for review.

## Deliverables
- This ticket's implementation map and difficulty assessment.
- A concise owner-facing explanation of the sequence and its principal risks.

## Difficulty Assessment
Engineering judgment: moderate implementation complexity with substantial correctness work across
subsystems. The optional name and pool reset are straightforward. Structural persistence, nested
ancestry, failure handling and compatibility account for most of the difficulty.

| Work area | Relative difficulty | Reason |
| --- | --- | --- |
| Creation-only name and pooled reuse | Low to medium | Existing fields and pool paths are present; names initialize each use. |
| Cloud directory and root bridge | Medium | Shared namespace and atomic publication must preserve root ownership. |
| Recording, removal and structural replay | High | Parent edges, pooled id reuse, both drivers and old-reader safety must agree. |
| Nexus integration | Medium | Fields exist; live records, compiled ids and final resolution have different boundaries. |
| Verification and documentation | Medium to high | Failures cross acquisition, teardown, checkpoint windows and restored hierarchy. |

This extends existing pools, twins, public replay verbs and Nexus records. It does not require a new
instance-lifetime model. A precise time estimate would depend on the decisions below and the existing
upgrade ownership issue; the phase/risk map is more defensible than an unverified hour count.

## Requirements Already Fixed By The Owner
- A lesser receives its optional name only in its creation call; no later public naming or renaming.
- Prewarmed shells stay unnamed until acquired for an application scope.
- Only named conduits enter cloud discovery. Unnamed scope cycles skip cloud register/unregister work.
- Named scope release unregisters and clears the name before the shell can be reused.
- Crystallizer saves/rebuilds named lesser STRUCTURE, including its role and relationships.
- Previously created objects and their mutable instance state are not serialized/restored by this feature.

## Decisions Needed Before Implementation
These are planning proposals or open details, not newly approved requirements.

| Decision | Proposed direction / constraint | Effect on the plan |
| --- | --- | --- |
| Namespace and validation | Prefer frame-wide unique active names, shared by roots and named lessers; validate nonempty strings and exact matching once at creation. | Parent-qualified repeats need a different lookup key and consumer API. |
| Runtime modes | Decide naming in automatic/dynamic mode and recording coverage separately. | Automatic recording requires consistent frame/book/conduit capture; emitting an orphan child is insufficient. |
| Unnamed ancestry | Preserve the necessary unnamed ancestor chain for faithful named-child restoration, without adding those ancestors to cloud discovery. | Choose how supporting ancestors are recorded, deduplicated and removed. |
| Hook/publication order | Specify when activation/post-create hooks can observe the name, directory entry and structural record. | Determines acquisition rollback boundaries and reentrant behavior. |
| Nexus pooled records | Reuse current fields/ids; choose retained unnamed pooled records or removal with coherent compiled membership. | Same-id payload changes can avoid needless recompilation; removed ids cannot remain compiled-visible. |
| Restore collisions/version | Refuse or explicitly report incompatible collisions; protect child-bearing records with a version policy old readers reject. | The existing major-version gate makes a minor-only format extension unsafe for old root-only readers. |
| Upgrade ownership | Resolve the existing ignored new-Spellbook return and intended parent/book transition. | A bounded prerequisite for claiming faithful named-lesser-to-root replay. |

## Planned Implementation Sequence
All steps below are future work. Tests accompany each code phase; phase 11 combines the full contract.

### 01. Finalize The Contract And Acceptance Cases
- Resolve the decision table, preserving every owner-fixed requirement.
- Define active unnamed, active named, pooled idle, upgraded normal and permanently cleaned states.
- State what is visible at each successful boundary and what must be undone on failure.
- Define checkpoint meaning: an earlier seal retains its historical structure; a later seal reflects removal.
- Convert the phases into scoped implementation tasks under the existing four stories once decisions are settled.
Deliverable: one approved contract and an acceptance matrix with no hidden setter or persistence choices.

### 02. Prepare Patch Design And A Reproducible Baseline
- Read the relevant generated graph slices through their verified index, then the complete implementation
  units and test bodies about to be changed. Prior source reads identify targets, not permission to skip this.
- Write the required architecture, component and control-flow patch contracts in one named patch lane.
- Map every patch section to implementation and validation; include lock order, failure handling and rollback.
- Establish the focused existing tests and warmed unnamed-scope performance baseline on the repo's supported runtime.
- Check named publication/release against existing DevOps/LoadGate admission. Choose any required named-only
  coordination explicitly; do not add a new transaction or broad lock to every unnamed scope by assumption.
Deliverable: approved patch design and baseline evidence before behavior changes.

### 03. Introduce The Named Directory And Bridge Root Registration
- Give ConduitCloud an explicit named-scope directory with name and id lookup for eligible live objects.
- Keep AethericFrame root maps and Spellbook/DevOps ownership root-only.
- Route named root creation/removal through the directory too, so roots and lessers cannot race into the same name.
- Make collision check plus insertion atomic; make removal verify the expected conduit identity.
- Define list/count/id APIs clearly: named directory views versus existing root-only queries.
- Keep directory cleanup limited to its references; scope owners retain lifecycle responsibility.
Targets:
- `src/melder/aether/aetheric_frame/conduit_cloud.py`
- `src/melder/aether/aetheric_frame/aetheric_frame.py`
Proof: duplicate root/lesser names fail without partial registration; removing a lesser changes no root ownership.

### 04. Wire Creation-Time Naming Into Both Acquisition Paths
- Add an optional name to create_lesser_conduit while preserving existing logger-call compatibility.
- Validate the request before destructive or published work.
- Acquire a prepared shell from the root pool, or construct one on a pool miss, through the existing specialized path.
- Initialize the name for that use, attach the actual parent/root relationship and publish the directory entry
  in the agreed order. Do not depend on __init__ or AbstractElasticPool.prepare_object running on reuse.
- Apply the same behavior with and without hooks; reject post-creation lesser setter assignments.
- On collision, parent cleanup or hook failure, remove any partial publication and return/destroy the shell safely.
Targets:
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_pool.py` (review; change only if the specialized pool contract needs it)
Proof: prewarmed and cold named creation agree; unnamed calls perform no cloud mutation; failed calls leak no name.

### 05. Complete Release, Parent Teardown And Promotion
- Remove the old named directory entry and clear its per-use name before publishing the shell back to the pool.
- Preserve existing cleanup of creations, spellspaces, local hooks and ward links; unnamed release skips cloud work.
- Cover explicit cleanup, ancestor/root cleanup, pool overflow destruction and permanent cleanup.
- Validate/reserve promotion names before the upgrade changes role/name; support same-object existing-name handling.
- Resolve the bounded upgrade book/parent ownership issue and preserve creation-store ownership during promotion.
- Ensure successful promotion updates the final directory role, structural record and Nexus data exactly once;
  failed promotion must leave a defined, recoverable state.
Targets:
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/spellbook/spellbook.py` (bounded upgrade ownership prerequisite)
Proof: no stale name, duplicate pool return or accidental shared-book/root cleanup across the transition matrix.

### 06. Define And Read The Structural Record Format
- Extend the conduit-twin contract to distinguish roots from named lessers and carry the immediate parent,
  root identity, shared-book reference, name and relevant posture as values.
- Define supporting unnamed ancestor representation without serializing Creations entries or live references.
- Keep old root-only input understandable by the new reader; reject malformed new child topology explicitly.
- Select the format/version policy before enabling production writers. Verify every durable boundary preserves it.
- Review checkpoint/formation/remote-envelope round trips; the generic payload carrier may need no schema edits.
Targets:
- `src/melder/crystallizer/crystals/conduit_crystal.py`
- `src/melder/crystallizer/persistence/record_version.py`
- `src/melder/crystallizer/persistence/persistence_crystal.py` (round-trip verification)
Proof: structural values survive serialization; old readers refuse unsupported child-bearing records.

### 07. Implement Current-Record Lifecycle, Folding And Formation Closure
- Add the conduit-level removal route through Crystallizer, PersistenceSystem and PersistenceProfile.
- Journal/capture its removal event and teach folding to remove that scope without removing its borrowed book.
- Preserve replace-by-id semantics across release and reacquisition under a new name.
- Define ancestor-support retention and cleanup so records neither orphan a named child nor retain dead support forever.
- Extend conduit/frame formation selection to include the required parent/root/child structure.
- Add preflight for missing/cyclic parents, role/root/book mismatches and duplicate names; keep peer links distinct.
Targets:
- `src/melder/crystallizer/crystallizer.py`
- `src/melder/crystallizer/persistence/persistence_system.py`
- `src/melder/crystallizer/persistence/persistence_profile.py`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py` (folding)
- `src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py`
- A child-lineage preflight strategy in the existing preflight package (new file only if warranted).
Proof: emit/remove/re-emit sequences fold correctly within one seal and across seals; formation anchors remain complete.

### 08. Rebuild Roots And Lesser Hierarchies Correctly
- Replace first-matching-row root selection with explicit root classification and legacy-root handling.
- Rebuild the owning book/root once, then create each lesser under its restored parent in dependency order.
- Use the public lesser-creation API and map recorded ids to fresh runtime ids; preserve names and shared-book use.
- Prefer one shared per-book hierarchy routine for both drivers where the contract permits; otherwise add explicit
  child dependency nodes. Do not implement different semantics in sequential and parallel paths.
- Extend live-handle bookkeeping, built counts, rollback and named collision outcomes to children.
- Verify restored structure resolves fresh objects normally rather than rehydrating previous instances.
Targets:
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
- `src/melder/crystallizer/crystal_loader_system/load_admission.py`
- `src/melder/crystallizer/crystal_loader_system/load_plan.py` (review if plan shape changes)
Proof: one book/root with multiple/nested named children restores identically through both drivers and unwinds cleanly.

### 09. Connect Runtime Emission And Removal After Readers Are Ready
- Emit named lesser structure only after successful creation-time naming and parent attachment.
- Emit the current-scope removal before reset/reuse; emit the final structural role after successful upgrade.
- Apply the chosen recorder activation/mode policy consistently with required frame/book/ancestor records.
- Keep prewarming and unnamed directory paths free of named publication; supporting ancestor capture follows its
  explicit contract rather than recording every idle shell as an active scope.
- Preserve passive recording and normal re-emission during restore; handle failures with the agreed lifecycle policy.
Targets:
- `src/melder/aether/conduit/conduit.py`
- Crystallizer facade/record methods introduced in phases 6-7.
- Frame/book recording gates only if the selected automatic-mode contract requires their expansion.
Proof: directory state, live named structure and the current structural record agree after every completed transition.

### 10. Integrate Nexus Using Its Existing Fields
- Update name/state/parent/root payloads and affected frame cloud-name summaries on named lifecycle transitions.
- Preserve frame eligibility, view/command ACLs and normal-only operations.
- Route published named command lookups through a lesser-aware final resolver after the existing permission checks.
- Forward the optional creation-time name through supported command wrappers.
- Distinguish same-id payload replacement from additions/removals of compiled ids; implement the chosen pooled-record
  policy and reconcile membership without unnecessary full refreshes for simple payload changes.
- Exercise the same publication flow for restored named lesser structure.
Targets:
- `src/melder/nexus/frame_descriptor_manager.py`
- `src/melder/nexus/nexus.py`
- `src/melder/nexus/rift/command_system/command_system.py`
- `src/melder/nexus/rift/command_system/capability_command_system.py`
- `src/melder/nexus/rift/command_system/codegen_command_system.py`
- Viewer/projection/ACL code only where the selected membership policy requires it.
Proof: cloud, published named queries and existing Rift projections agree while denied access remains denied.

### 11. Complete Behavioral, Concurrency And Performance Validation
- Add focused contract tests with each phase; then run the combined regression matrix below.
- Use real minimal wiring for pooling, checkpoint/restore and projection boundaries;
  mock only genuine external boundaries.
- Test concurrent same-name acquisition, lookup versus release, parent cleanup and promotion failures.
- Compare cold versus prewarmed paths, named versus unnamed, and recorder/Nexus off versus enabled.
- Measure warmed unnamed scope cycles before/after; measure named lifecycle overhead separately from meld throughput.
- Run the repository's required unit/component/integration, typing and broader platform checks using supported runtimes.
Proof: source-backed behavior and measured overhead, with exact commands/results retained when implementation occurs.

### 12. Update Public/System Documentation, Build Assets And Handoff
- Document creation-only naming, borrowing/lifetime semantics, pool reset and structural persistence examples.
- Explain faithful hierarchy replay, record compatibility, collisions and any required Nexus refresh behavior.
- Update the authored architecture/components and their indexes; refresh changed graph descriptors and reassemble
  graph plus index together. Regenerate affected packaged assets through the existing build pipeline.
- Re-run checks affected by generated/documentation changes and prepare the complete reviewed change with evidence.
- Include upgrade/rollback guidance for the record format and preserve readable older checkpoint fixtures.
- Obtain owner acceptance before closing the implementation tickets; publication remains a separate authorized action.
Proof: public examples and packaged documents describe exactly the implemented contract.

## Dependency Order And Delivery Boundaries
Contracts and patch design precede everything. Directory ownership precedes lifecycle wiring.
Record format/removal/fold support precedes child replay; both precede enabling new structural writers.
Nexus integration follows the settled lifecycle/id contract. Final validation covers the combined feature.
Do not ship only the optional name parameter while recording/replay still loses named lesser structure.

## Validation Matrix And Existing Locations
Paths below are verified inventory targets; their complete test bodies must be read before editing.
No new tests have been written or run for this planning task.

| Contract | Required cases | Existing test area |
| --- | --- | --- |
| Creation/pool | Cold/prewarmed, name omitted/present, no later setter, reuse A -> B -> unnamed. | tests/unit/melder/aether/conduit/ and tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py |
| Directory/root | Root/lesser collisions, name/id/list/count parity, unnamed exclusion, borrowed ownership. | tests/unit/melder/aether/test_conduit_cloud.py and tests/component/melder/aether/test_conduit_cloud_component.py |
| Teardown/upgrade | Parent/root/overflow/permanent cleanup; promotion collision and unchanged Creations ownership. | tests/unit/melder/aether/conduit/test_conduit_upgrade_validate_before_mutate_regression.py and tests/component/melder/aether/conduit/ |
| Record lifecycle | Active seal, later removal, same-id replacement within/across windows, historical seal immutability. | tests/unit/melder/crystallizer/persistence/test_persistence_profile.py and test_persistence_system.py |
| Replay | One root plus nested children, unnamed support, fresh ids, same/different drivers, failures/rollback. | tests/unit/melder/crystallizer/crystal_loader_system/ and tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py |
| Compatibility | Old root records, unsupported new major, malformed parents, formation anchor closure, collisions. | tests/unit/melder/crystallizer/persistence/test_record_version_and_json_contract.py and restore tests |
| Nexus | Same-id name/state changes, new/removed compiled ids, published vs raw lookup, denied modes/ACLs. | tests/unit/melder/aether/test_frame_viewer_projection.py, test_frame_descriptor_manager.py and test_command_system_direct.py |
| Performance | Warm unnamed baseline, named registration/removal, recording and Nexus increments. | benchmarks/testing_other_di/profile_scope_cycle_contention.py |

Documentation entry points:
- `docs/intermediate/scopes.md`
- `docs/expert/persistence.md`
- `docs/expert/restore.md`
- `UX_and_AIX_experiences/02_intermediate/07_lesser_conduits_child_scopes.py`
- `UX_and_AIX_experiences/02_intermediate/37_the_frame_conduit_cloud.py`
- `UX_and_AIX_experiences/02_intermediate/29_scoped_cleanup_lesser_conduits.py`

## Scope Guard And Rollback Strategy
- Keep ordinary meld execution and Existence/Creations semantics outside the naming change.
- Review Aether root queries, cluster/transfer consumers and LoadGate interactions without broad rewrites.
- Record any required upgrade ownership repair as a distinct bounded prerequisite.
- Within a failed scope operation, unwind directory/record/parent publication before pool reuse.
- Within a failed restore, unwind child structure before roots/books through the agreed hard/soft cleanup contract.
- Build compatible readers before enabling new writers. A software downgrade must not reinterpret a newer
  child-bearing checkpoint; retain older readable checkpoints or use an explicitly designed migration.
- Exact source-file count depends on mode, ancestry and Nexus decisions; audit-only files should remain unchanged
  when their current generic behavior already satisfies the new contract.

## Files / Paths Impacted
- This planning task, the parent epic's links, and attention/mailbox routing.
- Planned implementation targets are listed in the phases above; those files are not edited by this task.

## Validation
- Runtime tests: Not run. This is planning only.
- Planning checks: all 27 backticked source/documentation paths resolve; no trailing whitespace or merge markers.
- Source boundaries and future-versus-completed wording reviewed; ticket/epic/board links synchronized.

## Risks / Rollback Notes
- Unnamed ancestor support, recording mode and Nexus membership policy affect the final implementation size.
- Earlier ephemeral-only persistence advice is superseded by the owner's structural persistence requirement.
- The map specifies operation, restore and record-version rollback boundaries for the future implementation.

## Applicable Anti-Patterns
- [x] No implementation from unapproved planning assumptions.
- [x] No created-object serialization or replay added to the structural feature.
- [x] No public post-creation lesser naming or renaming.
- [x] No replacement of root ownership maps with a generic scope directory.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none (the implementation map is part of this task)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record source refinements and planning decisions here. Prior behavioral evidence remains in the linked discovery task.

## Notes
- DATETIME: 2026-09-07T17:02:25Z
  TYPE: PLAN
  CLAIM: Owner requested a general difficulty assessment and every implementation step without making
    the change. Reuse the existing deep source trace; verify root registration and upgrade seams,
    then write a dependency-ordered plan with proposed choices clearly separated from owner decisions.
  EVIDENCE:
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md
  - tickets/tasks/2026-09-06_named_conduit_cross_system_discovery_task.md
  - Owner's implementation-mapping request in this conversation.
  IMPACT: Only planning records are writable in this task's authorized scope.
  NEXT: Inspect root-registration and upgrade transitions to complete the implementation boundary map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T17:12:06Z
  TYPE: FACT
  CLAIM: Frame root registration requires normal state and a nonempty name, updates root id/name
    maps under the frame lock, and registers Spellbook ownership in DevOps. Root cleanup tears down
    its ward and pool before root-map removal, then cleans its book. Upgrade changes state/name and
    creates a new pool before late root registration; ward conversion requires a parent and no children.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:340-416
  - src/melder/aether/conduit/conduit.py:756-871
  - src/melder/aether/conduit/conduit.py:1753-1777
  - src/melder/aether/conduit/conduit.py:1960-2141
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:526-580
  IMPACT: The implementation must bridge root registration into the named directory without admitting
    lessers as roots. Reserve/validate names before promotion mutation and keep release, rollback,
    ownership accounting and recorded role transitions consistent.
  NEXT: Include root/upgrade handling as an explicit implementation phase rather than hiding it in pooling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T17:12:06Z
  TYPE: RISK
  CLAIM: The existing upgrade calls create_new_preset_spellbook() without using its return value.
    The factory constructs and returns a separate new empty Spellbook; it does not attach that book
    to a conduit. This is a pre-existing ownership concern that affects the named-lesser-to-root
    persistence contract, not an already-repaired behavior.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1960-2141
  - src/melder/aether/spellbook/spellbook.py:6226-6264
  IMPACT: Verify and resolve the upgrade's intended book/parent ownership before claiming faithful
    upgraded-root replay. Track any repair explicitly; do not silently expand this planning task into it.
  NEXT: Mark this as a bounded prerequisite in the implementation map and difficulty assessment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T17:22:45Z
  TYPE: PLAN
  CLAIM: Completed the implementation map: difficulty by work area, fixed requirements, remaining
    decisions, twelve ordered phases, explicit source targets, existing test/doc locations, validation
    matrix and rollback order. The existing upgrade ownership concern is a bounded prerequisite.
    All 27 explicitly backticked source/documentation paths resolve; document whitespace checks pass.
  EVIDENCE:
  - tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md
  - tickets/tasks/2026-09-06_named_conduit_cross_system_discovery_task.md
  - Source readings and path validation recorded during this planning task.
  IMPACT: The owner has a reviewable implementation map; no runtime, test or generated-asset implementation occurred.
  NEXT: Review the map and settle its remaining contract choices before creating implementation patches/tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation map is complete and in review. Twelve phases cover contract/design, directory, creation/pool,
teardown/promotion, structural format/removal/fold/replay, emission wiring, Nexus, tests/performance and docs.
Difficulty is moderate overall; structural replay, compatibility, ancestry and upgrade ownership carry the risk.
Owner-fixed requirements are preserved; other design choices remain explicit. No runtime implementation was requested.
