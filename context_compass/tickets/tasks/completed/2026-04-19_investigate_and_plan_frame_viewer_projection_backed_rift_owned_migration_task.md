# Task: Investigate And Plan FrameViewer Projection-Backed Rift-Owned Migration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-investigate-and-plan-frame-viewer-projection-backed-rift-owned-migration
- Story: STORY-2026-04-19-plan-frame-viewer-projection-backed-rift-owned-migration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T15:27:26Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Produce one source-backed MRP migration plan for shrinking `FrameViewer` into
a projection-backed Rift-owned viewer with one viewer-level profile choice.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an epic, research pass, and
  migration proposal for the oversized viewer stack.
- EXECUTION_BOUNDARY: viewer/profile/projection/RiftConfiguration research and
  planning only.
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/projection/view_projection.py
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py
  - src/melder/aether/nexus/configuration/rift_configuration.py
- EXIT_GATE: the task yields one source-backed migration plan with explicit
  state ownership changes and implementation order.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if shipped code proves a real
  requirement for multi-profile or per-frame profile selection.

## Scope Boundaries
- In scope:
  - builder/profile stack behavior
  - viewer constructor/state overreach
  - `ViewProjection` as bundled viewer truth
  - Rift configuration hook for one viewer profile choice
- Out of scope:
  - implementation
  - command/codegen redesign
  - unrelated room/workstation changes

## Steps / Checklist
- [ ] Trace the full `Nexus -> ViewProjection -> FrameViewer -> profile/helper`
      chain.
- [ ] Prove what the builder does and does not do.
- [ ] Prove what `active_profiles_by_name` and per-frame selected profiles add.
- [ ] Prove what the shipped helper surfaces actually use.
- [ ] Propose the MRP migration shape and order.

## Deliverables
- source-backed chain explanation
- judgment on the current constructor/state design
- MRP migration plan
- explicit ownership rule for `CompiledFrameACLAccessSurface`

## Validation
- Not run. Planning only.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The full `Nexus` reread confirms the far end of the chain precisely.
    `Nexus` is the object that takes descriptor truth from
    `FrameDescriptorManager`, selected ACL state from `FrameACLManager`, and
    one compiled access surface from `FrameACLCompiler`, then splits that into
    three detached consumer bundles inside `FrameProjectionSet`. So the
    projection families are already the first median layer between root-side
    truth and room-side assets.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1545-1840
  - src/melder/aether/nexus/nexus.py:1914-1984
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:8-89
  IMPACT: The artifact and migration plan can treat `Nexus` projection
    assembly as settled and focus the change on removing the viewer's second
    local snapshot layer.
  NEXT: deliver the artifact-backed chain summary to the user and use that as
    the base for any next viewer migration decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The full object-chain read has been packaged into one artifact so the
    migration discussion no longer depends on replaying the raw source read.
    The artifact captures the current `Nexus -> FrameProjectionSet -> Rift ->
    RiftSpace -> FrameViewer -> bound profile -> helper` chain and explains why
    the viewer currently acts as a second median layer over projection-owned
    state.
  EVIDENCE:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md:1-236
  IMPACT: Future discussion about the viewer migration can use the artifact as
    the durable source-backed explanation instead of reconstructing the chain
    from scattered notes.
  NEXT: sync the artifact board entry and then report the chain findings back
    to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The full helper trio confirms that the helper side is already a
    borrowed consumer tree. `GeneralViewConduit` and `GeneralViewSpell` only
    hold a borrowed `GeneralViewFrame` reference; they do not own descriptor or
    ACL state themselves. All conduit/spell visibility and payload shaping
    still ultimately flows through `GeneralViewFrame`, which is itself driven
    by descriptor truth plus the compiled access surface.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:12-39
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:73-277
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:17-45
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:77-649
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1457-1798
  IMPACT: The artifact can safely describe the helper stack as a median
    consumer tree over one frame-local compiled-surface/descriptor binding,
    which strengthens the case for removing viewer-owned duplicate copies
    rather than preserving them for helper isolation.
  NEXT: reread the full `Nexus` object in compliant chunks so the artifact can
    describe the far end of the chain where projection bundles are assembled
    and cloned before `Rift` takes ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: `GeneralViewFrame` confirms the real helper contract. It is a
    borrowed-reference frame-local helper that consumes the bound descriptor and
    `CompiledFrameACLAccessSurface` to build visible `FrameLink` objects, then
    derives inventory, topology, search, collision, and payload-field answers
    from descriptor truth plus those ACL-filtered links. The raw
    `FrameACLConfiguration` is stored on the helper, but the live helper logic
    is centered on the compiled access surface and descriptor records.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:12-39
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:97-176
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:245-376
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1247-1426
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1505-1623
  IMPACT: The artifact should describe the helper stack as "compiled-surface
    consumer over descriptor truth" rather than as a second ACL/config owner.
  NEXT: read `GeneralViewConduit` and `GeneralViewSpell` in full so the
    artifact can describe how the rest of the helper stack rides on the same
    frame-local compiled-surface contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The full `FrameViewer` object proves the viewer is still a real
    snapshot host, not just a thin facade with a few stray fields. It owns
    descriptor/ACL/surface maps, owns an active-profile registry, owns
    per-frame selected bound profiles, clones ACL configs and compiled surfaces
    out of incoming projections during sync, and clones them again on viewer
    clone. It then routes descriptor-only host methods directly on itself while
    using `execute_method(...)` to dispatch frame-local behavior through the
    selected bound profile.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:28-61
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:74-198
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:319-433
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2538-2698
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3038-3213
  IMPACT: The artifact should describe `FrameViewer` as a median layer that
    currently re-hosts projection-owned truth and then builds bound helper
    assets on top of those local copies.
  NEXT: read the full `GeneralViewFrame`, `GeneralViewConduit`, and
    `GeneralViewSpell` helper objects and the full `Nexus` object so the
    artifact can explain what those bound helper assets actually consume.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The first large `FrameViewer` tranche proves the exact redundant layer
    the epic is targeting. `FrameViewer` still owns local
    `_frame_descriptors_by_name`, `_frame_acl_configurations_by_frame_name`,
    `_compiled_access_surfaces_by_frame_name`, `_active_profiles_by_name`, and
    `_selected_profiles_by_frame_name`, and `sync_from_projection_sets(...)`
    still clones ACL configs and compiled surfaces out of the incoming
    `ViewProjection` bundle before rebuilding per-frame bound profiles.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:29-61
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:74-198
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:319-433
  IMPACT: The artifact should call out that the current viewer is not just a
    thin host with bad docs; it is actively recreating projection-owned state
    inside itself during sync.
  NEXT: read the remainder of `FrameViewer` so the artifact can explain how
    that duplicated state is consumed by the host methods and selected-profile
    routing surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The full `Rift` and `FrameViewerProfile` objects make the current
    viewer chain explicit. `Rift` already owns the live
    `_projection_sets_by_frame_name` registry, applies refreshed projection
    sets, and then synchronizes the durable viewer asset with
    `sync_from_projection_sets(...)` plus Rift-built metadata. Meanwhile
    `FrameViewerProfile` is already documented and implemented as a
    borrowed-reference binder over `FrameDescriptor`,
    `FrameACLConfiguration`, and `CompiledFrameACLAccessSurface`; it does not
    own those objects and its cleanup only clears profile metadata.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:75-91
  - src/melder/aether/nexus/rift/rift.py:203-250
  - src/melder/aether/nexus/rift/rift.py:464-563
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:17-32
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:325-455
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:501-545
  IMPACT: The artifact should frame the problem as: the ownership contract is
    already projection-on-Rift plus borrowed profile binding, but `FrameViewer`
    still inserts a redundant viewer-owned snapshot/cache layer in between.
  NEXT: read the full `FrameViewer` object to map exactly where that redundant
    snapshot/cache layer is created and rebuilt.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The small object read confirms the bundle/host split directly. One
    `FrameProjectionSet` owns one `ViewProjection`, one `CommandProjection`,
    and one `CodegenProjection` for a frame; `RiftSpace` owns the durable
    viewer/workstation/command/memory/event assets; and the viewer-profile
    builder still only seeds `general`. So the current viewer-local template
    registry is broader than the shipped profile surface, while the actual
    per-frame bundle already exists as `FrameProjectionSet` / `ViewProjection`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:8-89
  - src/melder/aether/nexus/rift/projection/view_projection.py:6-90
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:26-384
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py:12-110
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:21-367
  IMPACT: The artifact should describe `FrameProjectionSet` as the owned
    per-frame bundle and `RiftSpace` as the asset host, then explain why the
    current viewer-local profile machinery is now the suspicious layer.
  NEXT: read the full `FrameViewer`, `FrameViewerProfile`, `GeneralViewFrame`,
    `GeneralViewConduit`, `GeneralViewSpell`, `Rift`, and `Nexus` objects in
    compliant chunks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: PLAN
  CLAIM: The updated epic now requires a deeper full-object reread before the
    migration plan is trustworthy. The next pass must read the full live
    `Nexus`, `Rift`, `RiftSpace`, `FrameViewer`, profile, and projection chain
    and then capture that object-ownership/asset-build story in a dedicated
    artifact instead of relying on the earlier partial spot checks.
  EVIDENCE:
  - tickets/epics/2026-04-19_migrate_frame_viewer_to_projection_backed_rift_owned_model_epic.md:1-140
  - user_instruction: "reread the epic please and it was updated"
  - user_instruction: "read the nexus, and frameviewer, and the rift, and rift space read all the objects involved"
  - user_instruction: "document these in an artifact"
  IMPACT: The active task should pause plan-finalization and switch into a full
    object-chain source read plus artifact write-up.
  NEXT: read the full object chain in compliant chunks, then write the artifact
    and sync its ticket links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T15:27:26Z
  TYPE: FACT
  CLAIM: The builder is not the same thing as the viewer's active-profile
    registry. The builder is only a template registry that seeds `general`,
    while the viewer creates a second local reusable-profile registry on top of
    it and then creates bound profile clones per frame.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py:54-109
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:175-213
  IMPACT: The constructor is doing more than "builder stuff"; it is carrying a
    second layer of profile management that can likely be removed.
  NEXT: verify whether the shipped helper stack actually needs per-frame bound
    profile state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:27:26Z
  TYPE: FACT
  CLAIM: The shipped helper stack is centered on `CompiledFrameACLAccessSurface`
    plus descriptor truth. In the current `general` helper implementation, the
    raw `FrameACLConfiguration` is stored on `GeneralViewFrame` but not used by
    the helper methods themselves.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:39-112
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:215-236
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:361-375
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:496-554
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1541-1606
  IMPACT: The MRP migration can likely remove raw ACL config from the live
    helper/viewer path and keep the compiled surface as the real derived access
    contract.
  NEXT: plan the target model around `ViewProjection` as the single bound
    viewer-state bundle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:27:26Z
  TYPE: FACT
  CLAIM: There is only one shipped viewer profile family in the repo:
    `general`. The current multi-profile, active-profile-registry, and
    per-frame selected-profile design is therefore more generic than the live
    product currently needs.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py:54-109
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:1-235
  IMPACT: A one-profile-per-viewer MRP cut is source-supported today.
  NEXT: include a RiftConfiguration-backed viewer profile selection in the
    migration plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:32:00Z
  TYPE: FACT
  CLAIM: `Nexus` already owns the right bundling boundary. It builds one
    `FrameProjectionSet` per frame by assembling descriptor truth from
    `FrameDescriptorManager`, one selected `FrameACLConfiguration` snapshot
    from `FrameACLManager`, and one compiled access surface from
    `FrameACLCompiler`, then cloning the ACL config and compiled surface into
    each projection family. So the compiled surface already lives as
    projection-owned state, not as viewer-owned truth.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:36-45
  - src/melder/aether/nexus/frame_acl_manager.py:320-352
  - src/melder/aether/nexus/nexus.py:1545-1699
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-90
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:1-89
  IMPACT: The migration should keep `ViewProjection` as the bundled viewer
    state carrier instead of inventing another state holder.
  NEXT: verify whether the shipped viewer helpers actually need the raw ACL
    configuration or mostly live off descriptor + compiled surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:32:00Z
  TYPE: FACT
  CLAIM: The shipped `general` helper stack barely uses the raw
    `FrameACLConfiguration`. `GeneralViewFrame` stores it, but the live helper
    methods overwhelmingly read `CompiledFrameACLAccessSurface` plus descriptor
    truth. `GeneralViewConduit` and `GeneralViewSpell` use the frame helper and
    compiled surface only.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:39-112
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:215-236
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:361-375
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:496-554
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1541-1606
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:165-168
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:175-179
  IMPACT: The MRP cut can likely remove raw ACL config from the live helper
    path and keep the compiled surface as the real derived access contract.
  NEXT: check whether `RiftConfiguration` already has a viewer-profile concept
    or whether that must be introduced in the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:32:00Z
  TYPE: FACT
  CLAIM: `RiftConfiguration` does not currently carry any viewer-profile
    setting. It only owns `space_type`, `space_name`,
    `auto_activate_on_program`, and `validation_mode`.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_configuration.py:47-62
  - src/melder/aether/nexus/configuration/rift_configuration.py:211-219
  - src/melder/aether/nexus/configuration/rift_configuration.py:330-405
  IMPACT: A one-profile-per-viewer model would require a new Rift-level viewer
    profile property rather than reusing an existing config seam.
  NEXT: fold that into the migration plan and the epic requirements.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:38:43Z
  TYPE: DECISION
  CLAIM: The task should carry one explicit ownership rule into the final plan:
    `CompiledFrameACLAccessSurface` remains projection-owned. Nexus compiles it
    and clones it into `ViewProjection`; the viewer migration should consume it
    from there, not create another viewer-owned copy.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1573-1699
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-90
  IMPACT: This constrains the migration to the viewer/profile stack and keeps
    the projection boundary coherent.
  NEXT: include this rule directly in the final recommendation to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The ACL refresh path is now explicit and clean: `Nexus` responds to
    ACL changes, batches impacted `Rift`s, gates and drains them, then
    refreshes one changed-frame subset per Rift. Each `Rift` asks `Nexus` for
    fresh projection sets, stores them, and then applies them to hosted assets.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1914-1984
  - src/melder/aether/nexus/nexus.py:1795-1840
  - src/melder/aether/nexus/rift/rift.py:469-521
  IMPACT: The migration plan should preserve this control flow and only change
    how viewer state is consumed from the refreshed projections.
  NEXT: fold the refresh-chain details into the epic and keep the viewer cut
    scoped away from Nexus orchestration changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The current projection classes still duplicate more than the viewer
    actually needs. `ViewProjection`, `CommandProjection`, and
    `CodegenProjection` each currently own:
    - one live descriptor reference
    - one detached ACL configuration clone
    - one detached compiled access-surface clone
    The viewer migration should not add more duplication on top of that.
  EVIDENCE:
  - src/melder/aether/nexus/rift/projection/view_projection.py:8-88
  - src/melder/aether/nexus/rift/projection/command_projection.py:7-80
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:7-80
  IMPACT: The MRP plan should keep viewer state thin and may later justify a
    second cleanup around projection-family duplication, but that is separate
    from this viewer cut.
  NEXT: state clearly in the epic which projection-owned fields are required
    now and which ones are only provisional carry-through state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is the bounded discovery lane for shrinking `FrameViewer` into a
real projection-backed viewer instead of a snapshot host.