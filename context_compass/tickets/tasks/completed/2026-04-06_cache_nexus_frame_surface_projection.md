# Task: Cache Nexus Frame Surface Projection
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-cache-nexus-frame-surface-projection
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T04:25:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Add a small Nexus-owned cache for projected `FrameView` objects with explicit
invalidation on descriptor and ACL changes so frame-surface projection stops
recomputing from scratch on every call.

## Ticket Contract
- ENTRY_GATE: Nexus can already project `FrameView` / `FrameViewer` from
  descriptor truth plus current ACL config, and the user explicitly asked to
  keep moving on the frame-surface lane.
- EXECUTION_BOUNDARY: cached frame-view projection only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_project_frame_views_from_nexus_descriptor_and_acl.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_link/frame_link.py
- EXIT_GATE: Nexus caches projected frame views, invalidates them on relevant
  descriptor/ACL changes, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if clean caching requires a
  separate long-lived manager instead of a bounded Nexus-local cache.

## Scope Boundaries
- In scope:
  - cached `FrameView` projection
  - clone support required for safe cache returns
  - targeted invalidation on descriptor and ACL transitions
  - focused tests
- Out of scope:
  - cached `FrameViewer` projection
  - subscription/update push model
  - holding-zone redesign

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the smallest safe cached projection shape.
- [x] Implement cache storage, clone returns, and invalidation points.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- cached Nexus frame-view projection
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/rift/frame_viewer/frame_view.py
- src/melder/aether/nexus/rift/frame_link/frame_link.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_link_runtime_contracts.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: returning shared cached view objects would create cleanup/use-after-clean hazards.
  Rollback: cache one canonical projection and return detached clones only.
- Risk: invalidation misses would serve stale views.
  Rollback: keep invalidation broad and explicit on every descriptor/ACL mutation path touched in this slice.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_frame_surface_projection_cache/architecture_patch.md
  - system_docs/patches/active/nexus_frame_surface_projection_cache/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_surface_projection_cache/component_patch_frame_view.md
  - system_docs/patches/active/nexus_frame_surface_projection_cache/code_description_patch_projection_cache_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T04:25:00Z
  TYPE: PLAN
  CLAIM: The next bounded improvement is cached Nexus frame-view projection.
    The on-demand bridge works, but it recompiles and reprojects every time.
    The smallest useful upgrade is a Nexus-local cache for projected
    `FrameView` objects keyed by frame name, current ACL configuration id, and
    downstream contract profile name, with explicit invalidation on descriptor
    and ACL changes.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1353-1462
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-350
  - user_instruction: "yep keep moving"
  IMPACT: We can improve the holding-zone bridge without widening into a full
    manager or subscription model yet.
  NEXT: create the patch-doc set, then inspect the current projection and
    mutation paths to place the cache and invalidation hooks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:27:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this cached projection slice is
    now explicit. `architecture_patch.md` maps to keeping the cache Nexus-local
    and returning clones only. `component_patch_nexus.md` maps to cache storage
    and invalidation hooks in `nexus.py`. `component_patch_frame_view.md` maps
    to clone support for safe cache returns. The
    `code_description_patch_projection_cache_flow.md` doc maps to hit/miss and
    invalidation control flow.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/nexus_frame_surface_projection_cache/architecture_patch.md:1-20
  - codex/context_compass/system_docs/patches/active/nexus_frame_surface_projection_cache/component_patch_nexus.md:1-10
  - codex/context_compass/system_docs/patches/active/nexus_frame_surface_projection_cache/component_patch_frame_view.md:1-6
  - codex/context_compass/system_docs/patches/active/nexus_frame_surface_projection_cache/code_description_patch_projection_cache_flow.md:1-9
  IMPACT: The implementation can stay bounded to cached `FrameView`
    projection instead of drifting into a larger projection architecture.
  NEXT: implement clone support, cache storage, and invalidation hooks with
    focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:32:00Z
  TYPE: FACT
  CLAIM: Cached Nexus frame-view projection is now implemented. Nexus now owns
    a small `FrameView` cache keyed by:
    - `frame_name`
    - current ACL `configuration_id`
    - downstream `contract_profile_name`
    and returns detached clones instead of the cache-owned view object.
    `FrameLink` and `FrameView` now support cloning, and Nexus explicitly
    invalidates cached frame views on the descriptor publish/remove paths and
    on ACL insert/select/rollback transitions touched in this slice.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:72-87
  - src/melder/aether/nexus/nexus.py:171-181
  - src/melder/aether/nexus/nexus.py:217-243
  - src/melder/aether/nexus/nexus.py:863-977
  - src/melder/aether/nexus/nexus.py:1269-1328
  - src/melder/aether/nexus/nexus.py:1362-1497
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-242
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-374
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-270
  IMPACT: Nexus no longer has to fully reproject frame views from scratch on
    every call, and the returned objects remain cleanup-safe.
  NEXT: review whether the next frame-surface slice should cache viewers too,
    add richer projection helpers, or move to a different lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:32:00Z
  TYPE: MEASURE
  CLAIM: The cached projection slice is green on the focused frame-surface
    validation surfaces. The focused projection tests passed with 21 tests, and
    the broader frame-link/view/viewer/projection slice passed with 42 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_runtime_contracts.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The cache layer is stable enough to review as a bounded slice.
  NEXT: decide whether to keep iterating the frame-surface caching/projection
    layer or switch to another lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to add cached Nexus frame-view projection after the on-demand
projection bridge landed.



