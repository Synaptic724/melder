# Epic: Atomic ACL Projection Refresh Barrier
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-19-atomic-acl-projection-refresh-barrier
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T10:01:33Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-04-19
- Related Program/Initiative: AetherRift projection refresh correctness

## Problem / Opportunity
The live ACL refresh path is only atomic for one changed frame at a time.

Current behavior:
- `Nexus._on_frame_acl_changed(frame_name)` calls
  `_refresh_rift_projection_sets_for_frame(frame_name)`.
- That method finds impacted `Rift` instances by checking whether the changed
  `frame_name` appears in each Rift's assigned frame-contract set.
- When refresh gating is enabled, `Nexus` disables each impacted Rift gate,
  waits for active tickets to drain, refreshes that single frame on each Rift,
  and then re-enables the gates.
- `Rift.refresh_runtime_projections(...)` still accepts only one optional
  `frame_name`, asks `Nexus.create_frame_projection_sets_for_rift(...)` for
  one single-frame subset, merges that subset into the room, and rebuilds the
  viewer immediately afterward.

That is correct for one frame, but it is not yet the full refresh model.

If multiple frames change together:
- the same Rift can be frozen and reopened multiple times,
- the same room can merge projections and rebuild its viewer multiple times,
- refresh work is repeated even when the changed frames hit the same Rift,
- there is no single batch primitive that freezes the union of impacted Rifts
  once, drains once, refreshes all changed frames, and then reopens once.
- the room-side primitives are underused even though
  `RiftSpace.replace_projection_sets(..., merge=True)` can already merge more
  than one incoming projection set in one call and `_rebuild_frame_viewer(...)`
  already performs one viewer rebuild from the installed map.

Important precision:
- `RiftGate` is Rift-scoped, not frame-scoped.
- So the real implementation target is:
  freeze every Rift whose frame-contract membership intersects the changed
  frame set, not "lock one frame object."

## MRP Alignment (Most Reasonable Product)
The most reasonable product is one explicit batch refresh barrier:
- block new entrants on every impacted Rift,
- wait for in-flight guarded work to leave,
- refresh every changed projection set needed by that Rift,
- merge once into the room,
- rebuild the viewer once,
- reopen admission.

That keeps projection refresh coherent under live ACL mutation without
reopening the older fake multi-space or viewer-owned correctness models.

## Ticket Contract
- ENTRY_GATE: source review proves that the current implementation is correct
  only for the single-frame ACL callback path, and the user explicitly wants a
  program-level epic for the missing atomic batch behavior.
- EXECUTION_BOUNDARY: Nexus refresh orchestration, Rift batch projection
  refresh, room projection merge/rebuild behavior, focused tests, and matching
  architecture/component docs only.
- DEPENDENCIES:
  - tickets/epics/2026-04-18_rehome_frame_viewer_ownership_to_rift_space_epic.md
  - tickets/tasks/2026-04-18_implement_configurable_rift_gate_projection_refresh_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/configuration/nexus_configuration.py
- EXIT_GATE: ACL refresh can batch multiple changed frames under one RiftGate
  barrier per impacted Rift, projection merges happen once per Rift per batch,
  viewer rebuild happens once per Rift per batch, and docs/tests match the
  live model.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the runtime needs a stronger
  global transaction model than one per-Rift barrier and batch refresh.

## Goals (Outcomes)
- Introduce one Nexus batch refresh primitive for a set of changed frame names.
- Freeze impacted Rifts once per batch, not once per frame.
- Refresh the changed projections per Rift in one pass.
- Merge updated projection sets into each room once per batch.
- Rebuild each room-owned viewer once per batch.
- Keep the current config-backed gate timing surface as the governing barrier
  configuration.
- Reuse the existing room merge/rebuild primitives instead of inventing a new
  room-level batch state machine.

## Non-Goals (Explicit Exclusions)
- Do not redesign `RiftGate` itself in this epic.
- Do not redesign `CommandSystem`, `FrameViewer`, or `Workstation` APIs in
  this epic.
- Do not reopen explicit `frame_name` enforcement in this epic.
- Do not add a second refresh coordination system outside `Nexus`.

## Scope Boundaries
- In scope:
  - Nexus batch refresh orchestration for multiple changed frames
  - Rift batch projection refresh entrypoint
  - room-level projection merge and one-shot viewer rebuild per batch
  - focused unit/integration tests for overlapping impacted Rifts
  - architecture/component doc sync for the batch barrier model
- Out of scope:
  - unrelated ACL design work
  - command/codegen surface redesign
  - viewer profile redesign
  - multi-space runtime redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the implementation story/task landed, the focused
  validation ring is green, and the epic is waiting on review.

## Success Metrics
- One batch refresh entrypoint exists on `Nexus` for multiple changed frames.
- One impacted Rift is disabled and drained at most once per batch.
- One impacted Rift merges refreshed projections at most once per batch.
- One impacted Rift rebuilds its viewer at most once per batch.
- The single-frame ACL callback path delegates to the batch primitive instead
  of maintaining separate refresh logic.
- `Nexus.create_frame_projection_sets_for_rift(...)` and Rift refresh
  orchestration no longer force single-frame batching at the API seam.

## Requirements (Functional + Non-Functional)
- `Nexus` must expose one internal batch refresh path that accepts a sequence
  of changed frame names.
- The batch path must compute the union of impacted Rifts by frame-contract
  membership.
- `Nexus._on_frame_acl_changed(frame_name)` must become a thin delegate into
  the new batch primitive instead of owning separate orchestration logic.
- When `projection_refresh_gate_enabled` is true, the batch path must:
  - disable each impacted Rift gate before refresh work starts,
  - wait for each impacted Rift to drain active tickets,
  - refresh all changed projections needed by that Rift,
  - reopen the gates after refresh completes.
- `Nexus.create_frame_projection_sets_for_rift(...)` must support a
  multi-frame scope for one Rift instead of only one optional `frame_name`.
- `Rift` must support refreshing multiple frame projections in one call for
  one impacted Rift.
- `RiftSpace` must merge refreshed projection sets once per batch and rebuild
  the viewer once per batch.
- The batch path must preserve current viewer profile-selection state the same
  way the current single-frame refresh path does.
- The single-frame ACL callback path must reuse the batch primitive.
- The implementation must not leave duplicate single-frame and multi-frame
  orchestration logic in parallel.

## Constraints / Assumptions
- `RiftGate` guards Rift-scoped work, so the barrier is applied per impacted
  Rift, not per frame object.
- Current config fields remain the timing/configuration authority:
  `projection_refresh_gate_enabled`,
  `projection_refresh_gate_timeout_seconds`, and
  `projection_refresh_gate_poll_interval_seconds`.
- `FrameLinkContract` membership is the correct way to determine whether a Rift
  is impacted by a frame ACL change.
- `RiftSpace` already owns installed projections and room-local viewer rebuild.
- `RiftSpace.replace_projection_sets(..., merge=True)` already supports
  replacing more than one named incoming projection set in one call.
- The missing batch behavior is concentrated in the Nexus and Rift API seams,
  not in the room merge path.

## Dependencies / External References
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- existing viewer-ownership and refresh-config tickets listed above

## Milestones (Track Progress)
- [ ] Milestone 1: Batch refresh design is staged
      The exact Nexus -> Rift -> RiftSpace batch contract is documented and
      accepted.
- [x] Milestone 2: Nexus batch barrier lands
      Multiple changed frames can freeze the union of impacted Rifts once,
      drain once, and dispatch one refresh call per impacted Rift.
- [x] Milestone 3: Rift batch refresh lands
      Each impacted Rift requests a multi-frame projection subset from Nexus,
      merges once into the room, and rebuilds its viewer once.
- [x] Milestone 4: Single-frame callback is normalized
      The existing ACL callback path delegates to the batch primitive.

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-19-implement-atomic-acl-projection-refresh-batch -
      implement Nexus batch impacted-Rift refresh orchestration plus Rift
      multi-frame projection refresh

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-04-19-implement-atomic-acl-projection-refresh-batch
- [ ] Task: Verify Ticket Microcycle enforcement across the staged tickets.

## Acceptance Criteria (Epic Done)
- A batch ACL refresh can take multiple changed frame names and freeze the
  union of impacted Rifts once.
- New guarded work is blocked before batch projection refresh begins.
- In-flight guarded work is allowed to leave before projection swaps occur.
- Each impacted Rift updates all needed projections in one pass.
- Each impacted room merges projections once and rebuilds its viewer once.
- The old single-frame callback path is implemented as a thin delegate to the
  batch primitive.
- The batch path preserves current viewer profile-selection state across the
  one-shot rebuild.
- Focused tests and AR docs describe the live batch barrier accurately.

## Risks / Mitigations
- Risk: the same Rift may own many changed frames, and repeated single-frame
  refresh calls could accidentally survive inside the new batch path.
  Mitigation: require one Rift-side batch entrypoint and one room merge/rebuild
  per batch.
- Risk: timeout handling may reopen some gates after partial work.
  Mitigation: make failure behavior explicit in the batch orchestration tests
  and docs.
- Risk: a second orchestration path may linger beside the batch primitive.
  Mitigation: make the single-frame ACL callback delegate to the batch method.

## Applicable Anti-Patterns
- [ ] No new batch path that leaves the old single-frame logic as a second
      first-class refresh implementation.
- [ ] No claim of frame-level locking when the actual primitive is Rift-scoped.
- [ ] No closure while the room still rebuilds multiple times for one logical
      ACL refresh batch.

## Validation / Test Approach
- Focused Nexus unit tests for:
  - overlapping changed-frame sets,
  - union-of-impacted-Rifts computation,
  - one disable/drain/refresh/open cycle per impacted Rift.
- Focused Rift/RiftSpace tests for:
  - one multi-frame projection-builder call per impacted Rift batch,
  - batch projection merge,
  - one viewer rebuild per batch,
  - single-frame callback delegation to the batch path.

## Rollout / Adoption Plan
1. Stage the implementation story/task set behind this epic.
2. Land the Nexus batch primitive first:
   - collect and dedupe changed frame names,
   - compute impacted Rifts,
   - disable/drain/open once per impacted Rift.
3. Land the Rift multi-frame refresh path second:
   - request one multi-frame projection subset from Nexus,
   - merge once,
   - rebuild viewer once.
4. Normalize the current single-frame callback onto the batch path.
5. Re-sync architecture/component docs after the runtime path is live.

## Open Questions
- Should the batch entrypoint accept any `Iterable[str]`, or should it require
  a normalized immutable sequence to keep ordering/deduplication explicit?
- Should timeout during drain abort the full batch before any projection swap,
  or allow unaffected Rifts to continue?
- Should the batch path preserve viewer profile selection state exactly as the
  current single-frame refresh path does?

## Decision Log
- Pending user review of the epic framing and later staging of the first story
  and task set.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T10:01:33Z
  TYPE: FACT
  CLAIM: The live implementation already applies the correct RiftGate barrier
    for one changed frame: find impacted Rifts by frame-contract membership,
    disable their gates, wait for active tickets to drain, refresh that single
    frame, then reopen the gates.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1900-1954
  - src/melder/aether/nexus/configuration/nexus_configuration.py:63-79
  IMPACT: The missing work is not "invent refresh gating." It is "lift the
    correct single-frame barrier into one reusable batch primitive."
  NEXT: stage the batch design and implementation stories behind this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T10:01:33Z
  TYPE: FACT
  CLAIM: `Rift.refresh_runtime_projections(...)` still refreshes only one
    optional `frame_name` per call, merges by `merge=(frame_name is not None)`,
    and rebuilds the room viewer immediately after that single-scope refresh.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:463-529
  IMPACT: Without a Rift-side batch entrypoint, multi-frame ACL refresh would
    still reopen the same merge/rebuild path repeatedly.
  NEXT: stage a Rift batch refresh story/task under this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T10:01:33Z
  TYPE: PLAN
  CLAIM: The clean implementation is one Nexus batch refresh method plus one
  Rift batch projection refresh method. The single-frame ACL callback should
    become a thin delegate into that batch primitive.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1900-1954
  - src/melder/aether/nexus/rift/rift.py:463-529
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:373-463
  IMPACT: This avoids duplicated orchestration logic and keeps refresh
    correctness centralized.
  NEXT: wait for epic acceptance, then stage the first story/task set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T10:51:28Z
  TYPE: FACT
  CLAIM: The concrete single-frame bottlenecks are now explicit. `Nexus`
    still exposes only `_refresh_rift_projection_sets_for_frame(...)`, and
    `create_frame_projection_sets_for_rift(...)` still accepts only one
    optional `frame_name`. `Rift.refresh_runtime_projections(...)` mirrors
    that same single-frame scope.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1797-1836
  - src/melder/aether/nexus/nexus.py:1914-1984
  - src/melder/aether/nexus/rift/rift.py:463-529
  IMPACT: The missing batch behavior is concentrated in the Nexus and Rift API
    seams, not spread randomly across the room/viewer layer.
  NEXT: stage the implementation stories around those two seams directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T10:51:28Z
  TYPE: FACT
  CLAIM: `RiftSpace` already has the room-side primitives needed for a
    one-shot batch refresh. `replace_projection_sets(..., merge=True)` can
    merge more than one incoming frame projection in one call, and
    `_rebuild_frame_viewer(...)` already rebuilds the viewer once from the
    installed projection map.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:493-524
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:584-624
  IMPACT: We do not need a new room-level batch coordinator. The correct work
    is to batch the Nexus and Rift orchestration above the existing room
    primitives.
  NEXT: keep the implementation plan focused on Nexus batch orchestration and
    Rift multi-frame refresh.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T10:55:02Z
  TYPE: DECISION
  CLAIM: The implementation lane is now staged behind one concrete story, one
    concrete task, and one patch-doc set. The active implementation target is
    no longer generic planning; it is the bounded Nexus/Rift batch refresh cut.
  EVIDENCE:
  - tickets/stories/2026-04-19_implement_atomic_acl_projection_refresh_batch_story.md:1-86
  - tickets/tasks/2026-04-19_implement_atomic_acl_projection_refresh_batch_task.md:1-100
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/architecture_patch.md:1-24
  IMPACT: Patch-gated implementation can proceed without inventing more
    planning layers.
  NEXT: consume the patch docs and patch Nexus first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:01:58Z
  TYPE: FACT
  CLAIM: The epic implementation slice is landed. Nexus now batches impacted
    Rift refresh orchestration across changed frame sets, Rift now refreshes a
    multi-frame projection subset in one call, and the single-frame callback
    path is only a thin delegate into the batch primitive.
  EVIDENCE:
  - tickets/tasks/2026-04-19_implement_atomic_acl_projection_refresh_batch_task.md:1-168
  - src/melder/aether/nexus/nexus.py:1797-2064
  - src/melder/aether/nexus/rift/rift.py:463-579
  IMPACT: The epic is back in review and no longer needs active implementation
    work unless a follow-on is requested.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level refresh semantics, cross-story sequencing, and
  correctness boundaries.
- Add notes when the batch contract, failure semantics, or rollout order
  changes.
- Reference child story/task evidence once those tickets exist.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic tracks the missing batch refresh layer for ACL-driven projection
updates. The live runtime already gates one changed frame correctly; this epic
exists to make that refresh atomic across a set of changed frames by freezing
impacted Rifts once, draining once, refreshing once per Rift, and reopening
once. The current investigation also proves the room merge/rebuild layer is
already sufficient; the missing seams are the Nexus batch API and the Rift
multi-frame refresh API.