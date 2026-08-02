# Epic: Migrate FrameViewer To Projection-Backed Rift-Owned Model
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-19-migrate-frame-viewer-to-projection-backed-rift-owned-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T15:27:26Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-04-19
- Related Program/Initiative: AetherRift viewer/runtime ownership cleanup

## Problem / Opportunity
`FrameViewer` is still architected like a self-contained snapshot host instead
of a thin Rift-owned view surface.

Current wrong shape:
- `Nexus` already compiles `ViewProjection` as the bundled viewer-facing state:
  descriptor + detached ACL config + compiled access surface.
- `Rift` already owns current projection state.
- `FrameViewer` then clones that state again into:
  - `_frame_descriptors_by_name`
  - `_frame_acl_configurations_by_frame_name`
  - `_compiled_access_surfaces_by_frame_name`
  - `_selected_profiles_by_frame_name`
- `FrameViewer` also owns:
  - a local profile builder seam
  - a local active-profile registry
  - a viewer-local default profile selector
  - per-frame selected profile state
- The shipped viewer profile stack only contains `general`, but the viewer is
  still designed for multi-template local registries and per-frame selection.

That leaves the viewer over-responsible and architecturally inconsistent with
the thinner `CommandSystem` model, which reads live command projection truth
from `Rift` instead of hosting replicated snapshot state.

## MRP Alignment (Most Reasonable Product)
The most reasonable product is:
- make `FrameViewer` a durable asset that owns only viewer-local state
- keep projection truth on `Rift`
- make `ViewProjection` the single bundled source of descriptor/ACL/surface
  truth for viewer work
- collapse viewer profile selection to one Rift/viewer-level profile instead of
  per-frame selection
- strip the viewer constructor down to what the viewer actually owns

## Ticket Contract
- ENTRY_GATE: the user explicitly challenged the current `FrameViewer`
  constructor/state model and requested a holistic source-backed migration plan.
- EXECUTION_BOUNDARY: viewer/profile/projection/Nexus/Rift investigation,
  architecture planning, and ticket/doc staging only until implementation is
  explicitly approved.
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
- EXIT_GATE: one source-backed migration plan exists for a projection-backed
  viewer with Rift-owned profile selection and stripped constructor/state
  seams.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a required viewer/profile
  behavior would be lost by collapsing per-frame profile selection to one
  viewer-level profile.

## Goals (Outcomes)
- Strip `FrameViewer.__init__` down to real viewer-owned state.
- Stop duplicating descriptor/config/surface maps inside the viewer.
- Keep projection-derived state in `ViewProjection` / `Rift`.
- Move viewer profile selection to Rift/RiftConfiguration.
- Keep viewer profiles and helper surfaces, but bind them to `ViewProjection`
  instead of decomposed snapshot maps.

## Current Ownership Summary
- `Nexus` builds the first median layer:
  - `FrameDescriptorManager` owns descriptor truth
  - `FrameACLManager` owns selected ACL state
  - `FrameACLCompiler` produces one compiled access surface
  - `Nexus._create_frame_projection_set(...)` clones ACL/config/surface into
    `ViewProjection`, `CommandProjection`, and `CodegenProjection`
- `Rift` owns the current projection registry and the sync/apply flow for
  hosted assets.
- `RiftSpace` owns the durable viewer/workstation/command/memory/event assets.
- `FrameViewer` is currently a second median layer because it decomposes
  `ViewProjection` back into local descriptor/config/surface maps and rebuilds
  selected bound profiles from those copies.
- `FrameViewerProfile` and the `general` helper trio are already borrowed
  consumers over descriptor truth plus `CompiledFrameACLAccessSurface`.

## Source-Proven Current Chain
### Projection generation
1. `FrameDescriptorManager` owns descriptor truth and passive publication.
2. `FrameACLManager` resolves the selected family contracts and assembles one
   `FrameACLConfiguration` snapshot through `FrameACLContainer`.
3. `FrameACLCompiler.compile_frame_access_surface(...)` derives one
   `CompiledFrameACLAccessSurface`.
4. `Nexus._create_frame_projection_set(...)` clones the selected ACL snapshot
   and compiled access surface into each projection family and returns one
   `FrameProjectionSet`.

Evidence:
- src/melder/aether/nexus/frame_descriptor_manager.py:36-45
- src/melder/aether/nexus/frame_acl_manager.py:320-352
- src/melder/aether/nexus/acl/frame_acl_container.py:750-782
- src/melder/aether/nexus/acl/frame_acl_compiler.py:89-202
- src/melder/aether/nexus/nexus.py:1545-1699

### Refresh/update flow
1. ACL change enters `Nexus._on_frame_acl_changed(...)`.
2. `Nexus._refresh_rift_projection_sets_for_frames(...)` computes impacted
   `Rift`s by frame-contract membership.
3. With gating enabled, `Nexus` disables the impacted `RiftGate`s, waits for
   active tickets to drain, refreshes each Rift once for its changed-frame
   subset, then re-enables the gates.
4. `Rift.refresh_runtime_projections(...)` asks `Nexus` for fresh projection
   sets, stores them in the Rift-owned projection registry, and applies them to
   hosted assets.

Evidence:
- src/melder/aether/nexus/nexus.py:1914-1984
- src/melder/aether/nexus/nexus.py:1795-1840
- src/melder/aether/nexus/rift/rift.py:469-521

### Viewer sync and helper rebuild
1. `Rift.refresh_runtime_projections(...)` gets fresh projection sets from
   `Nexus`, stores them in `_projection_sets_by_frame_name`, then calls
   `space.frame_viewer.sync_from_projection_sets(...)`.
2. `FrameViewer.sync_from_projection_sets(...)` decomposes the incoming
   `ViewProjection` bundle into local descriptor/config/surface maps, clones
   ACL config and compiled surfaces into viewer-owned state, resolves selected
   profile names, and rebuilds one selected bound profile per frame.
3. `GeneralFrameViewerProfile.bind_to_frame(...)` rebuilds:
   - `GeneralViewFrame`
   - `GeneralViewConduit`
   - `GeneralViewSpell`
4. `GeneralViewConduit` and `GeneralViewSpell` then consume the borrowed
   `GeneralViewFrame`, which in turn consumes descriptor truth plus the
   compiled access surface.

Evidence:
- src/melder/aether/nexus/rift/rift.py:464-563
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:74-198
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:319-433
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3038-3213
- src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:107-225
- src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:97-176
- src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:73-1073
- src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:77-1798

## Projection Ownership Model (MRP Target)
Keep these on projections:
- descriptor reference
- compiled access surface
- generation / selected-contract metadata
- any other consumer-facing derived access answers produced by Nexus

Keep these on Rift:
- current projection registry
- one selected viewer profile for the viewer
- default frame policy / runtime frame choice
- refresh orchestration and asset application

Keep these on FrameViewer:
- viewer id
- gate reference
- default frame pointer
- selected viewer profile name
- lightweight metadata

De-emphasize or remove from the viewer path:
- viewer-owned descriptor maps
- viewer-owned ACL configuration maps
- viewer-owned compiled-surface maps
- local active-profile registry
- per-frame selected profile names

Raw `FrameACLConfiguration` handling:
- Current projections clone and carry it.
- Current shipped `general` helper code barely uses it.
- For the MRP viewer migration, treat raw ACL configuration as projection-owned
  carry-through state, not viewer-owned primary truth.
- If later cleanup proves the helpers never need it directly, remove it from
  the live viewer binding path in a follow-on simplification.

## Non-Goals (Explicit Exclusions)
- Do not redesign `CommandSystem` here.
- Do not redesign ACL compilation in `Nexus`.
- Do not invent multiple shipped viewer profiles just to preserve current
  generality.
- Do not force a broader explicit-frame cleanup lane into this epic.

## Scope Boundaries
- In scope:
  - `FrameViewer` constructor/state model
  - profile builder/profile binding shape
  - Rift-owned viewer profile selection
  - `ViewProjection` as the viewer-facing bundle
  - focused architecture/component doc follow-on planning
- Out of scope:
  - command/codegen redesign
  - unrelated AR room/workstation changes
  - implementation until the plan is accepted

## Success Metrics
- The migration plan removes per-frame profile selection from the viewer.
- The plan removes decomposed descriptor/config/surface constructor args.
- The plan keeps current helper behavior while relocating state ownership.
- The plan uses `ViewProjection` as the viewer-facing state carrier.

## Requirements (Functional + Non-Functional)
- Add one Rift-level viewer profile selection concept, likely in
  `RiftConfiguration`.
- `FrameViewer` should own only:
  - gate reference
  - default frame pointer
  - selected viewer profile name
  - lightweight metadata
- `FrameViewerProfile.bind_to_frame(...)` should consume `ViewProjection` (or
  a tiny wrapper over it), not three decomposed arguments.
- Keep `CompiledFrameACLAccessSurface` as the primary derived access contract
  for the helper stack.
- Because `Nexus` compiles and clones the access surface into
  `ViewProjection`, the compiled surface should remain projection-owned state
  instead of being copied again into viewer-owned maps.
- Treat raw `FrameACLConfiguration` as projection-owned metadata unless a
  proven helper/view contract still requires it directly.
- Preserve the current Nexus ACL-refresh pipeline and only change the viewer
  consumption/binding layer.
- The shipped `general` helper stack must keep current behavior.
- Any retained multi-profile machinery must be justified by real shipped use,
  not hypothetical flexibility.

## MRP Implementation Plan
1. Add one viewer-profile property to `RiftConfiguration`.
2. Move viewer profile selection to `Rift` and remove per-frame selected
   profile state from `FrameViewer`.
3. Strip `FrameViewer.__init__` down to viewer-local state only.
4. Change `FrameViewerProfile.bind_to_frame(...)` to bind from
   `ViewProjection` instead of decomposed descriptor/config/surface args.
5. Rework `FrameViewer` so it asks `Rift` for the current `ViewProjection`
   when it needs frame truth, while preserving durable viewer identity.
6. Keep `CompiledFrameACLAccessSurface` projection-owned and feed it through
   the bound helper stack.
7. Leave the Nexus refresh/orchestration path intact; only the viewer
   consumption layer changes.

## Milestones (Track Progress)
- [ ] Milestone 1: Investigation completes
      The live chain from Nexus compilation through viewer/profile/helper
      binding is explicit and source-backed.
- [ ] Milestone 2: Migration contract is staged
      Epic/story/task describe the target viewer model and MRP cut.
- [ ] Milestone 3: Implementation plan is accepted
      The user accepts or redirects the proposed migration before code changes.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-19-plan-frame-viewer-projection-backed-rift-owned-migration

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-04-19-investigate-and-plan-frame-viewer-projection-backed-rift-owned-migration

## Acceptance Criteria (Epic Done)
- The repo has one accepted plan for migrating `FrameViewer` away from
  snapshot-host ownership and toward Rift-owned projection truth.
- The plan explicitly explains:
  - why the current builder/profile stack exists
  - what state moves to `Rift`
  - what state stays on `FrameViewer`
  - what state stays inside `ViewProjection`
  - what constructor/state APIs are removed

## Risks / Mitigations
- Risk: some helper/profile code may quietly depend on raw
  `FrameACLConfiguration`.
  Mitigation: prove actual helper usage before planning removal.
- Risk: one-profile-per-viewer may break an unstated multi-profile use case.
  Mitigation: verify shipped profiles and current call sites before committing.
- Risk: the migration plan accidentally collapses the first median layer
  (`ViewProjection`) together with the second median layer (`FrameViewer`) and
  widens into a projection-family redesign.
  Mitigation: keep `Nexus` projection generation intact and target only the
  removal of viewer-side duplicate ownership in this epic.

## Applicable Anti-Patterns
- [ ] No preserving fake flexibility seams without shipped use.
- [ ] No decomposed descriptor/config/surface constructor args when
      `ViewProjection` already bundles that state.
- [ ] No per-frame profile selection kept alive without a proven requirement.

## Validation / Test Approach
- Not run. Planning/discovery only.

## Open Questions
- Whether the viewer should read `ViewProjection` live from `Rift` on every
  call or maintain a tiny generation-aware bound-profile cache keyed by frame.

## Decision Log
- Pending investigation outcome and user review.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T15:27:26Z
  TYPE: FACT
  CLAIM: The shipped viewer stack already proves the current shape is more
    generic than the live product needs. The builder only seeds `general`, the
    viewer creates a local reusable-profile registry on top of that, and then
    creates bound profile clones per frame. The general helper stack then
    rebuilds `view_frame`, `view_conduit`, and `view_spell` from bound
    descriptor/ACL/surface references.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py:54-109
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:175-213
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3502-3514
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:571-705
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:124-159
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:199-225
  IMPACT: The migration can target real overreach instead of arguing about an
    imaginary minimal viewer.
  NEXT: verify which pieces of raw ACL/config state are actually used by the
    shipped helper stack.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:27:26Z
  TYPE: FACT
  CLAIM: `ViewProjection` already bundles the viewer-facing runtime truth, and
    the shipped general helper surface leans heavily on
    `CompiledFrameACLAccessSurface` while barely using raw
    `FrameACLConfiguration`.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1613-1699
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-90
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:1-89
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:215-236
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:361-375
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:496-554
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1541-1606
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:39-112
  IMPACT: The MRP plan can move descriptor/config/surface ownership under
    `ViewProjection` / `Rift` without inventing a new state carrier.
  NEXT: stage the migration plan around `ViewProjection` as the single viewer
    state bundle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:32:00Z
  TYPE: FACT
  CLAIM: The deeper Nexus trace confirms the correct ownership boundary:
    `FrameDescriptorManager` owns descriptor truth, `FrameACLManager` owns the
    selected ACL snapshot, `FrameACLCompiler` builds the compiled access
    surface, and `Nexus._create_frame_projection_set(...)` already clones the
    ACL config and compiled surface into projection-owned state before `Rift`
    ever touches it.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:36-45
  - src/melder/aether/nexus/frame_acl_manager.py:320-352
  - src/melder/aether/nexus/nexus.py:1545-1699
  IMPACT: The migration should move viewer binding onto `ViewProjection` /
    `Rift` and not reopen Nexus-side ownership.
  NEXT: keep the plan centered on shrinking the viewer/profile stack rather
    than rewriting projection generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:32:00Z
  TYPE: FACT
  CLAIM: The shipped helper stack mostly depends on descriptor truth plus
    `CompiledFrameACLAccessSurface`; the raw `FrameACLConfiguration` is
    currently carried through the bind chain but does not appear to be a
    primary helper dependency in the shipped `general` profile path.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:39-112
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:215-236
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:496-554
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:165-168
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:175-179
  IMPACT: The MRP plan can likely de-emphasize raw ACL config in the viewer
    stack and keep the compiled surface as the main access vehicle.
  NEXT: preserve this as a constraint in the migration plan instead of keeping
    raw ACL config just because it is currently threaded through the API.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:32:00Z
  TYPE: FACT
  CLAIM: `RiftConfiguration` currently has no viewer-profile property, so the
    one-profile-per-viewer design requires adding a new Rift-level config seam
    instead of reusing an existing one.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_configuration.py:47-62
  - src/melder/aether/nexus/configuration/rift_configuration.py:211-219
  IMPACT: The migration plan needs an explicit config addition rather than just
    saying "move it to Rift" abstractly.
  NEXT: make the RiftConfiguration change part of the MRP implementation order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:38:43Z
  TYPE: DECISION
  CLAIM: The migration plan should treat `CompiledFrameACLAccessSurface` as
    projection-owned state. Nexus already compiles it and clones it into
    `ViewProjection`, so the viewer stack should consume that bundled surface
    instead of maintaining another viewer-owned copy.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1573-1699
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-90
  IMPACT: This keeps the migration bounded to the viewer/profile stack and
    avoids reopening Nexus-side surface ownership.
  NEXT: carry this rule into the story/task plan and any later implementation
    proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The deeper Nexus refresh trace proves the viewer migration does not
    need any Nexus-side architecture change. The current ACL refresh pipeline
    already does the right thing: Nexus recompiles projections, Rift stores
    them, then Rift applies them to hosted assets.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1914-1984
  - src/melder/aether/nexus/rift/rift.py:469-521
  IMPACT: The implementation can stay tightly focused on viewer/profile
    consumption and constructor/state simplification.
  NEXT: preserve the refresh pipeline and avoid reopening the Nexus runtime
    lane in this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The current projection families already duplicate descriptor/config/
    surface state across `ViewProjection`, `CommandProjection`, and
    `CodegenProjection`. That duplication is separate from the viewer problem.
    The viewer migration should stop at removing viewer-side duplication and
    not broaden into a second projection-family normalization refactor.
  EVIDENCE:
  - src/melder/aether/nexus/rift/projection/view_projection.py:8-88
  - src/melder/aether/nexus/rift/projection/command_projection.py:7-80
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:7-80
  IMPACT: The epic stays MRP-sized instead of collapsing multiple ownership
    cleanups into one uncontrolled rewrite.
  NEXT: keep any projection-family deduplication as a potential later follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level viewer ownership direction, cross-file design
  synthesis, and migration tradeoffs.
- Add notes when the proposed target model or migration order changes.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic stages the next viewer cleanup after the Rift-owned projection move:
strip `FrameViewer` down to a real viewer, keep projection truth on `Rift`,
and bind profiles/helpers to `ViewProjection` instead of duplicated snapshot
state.