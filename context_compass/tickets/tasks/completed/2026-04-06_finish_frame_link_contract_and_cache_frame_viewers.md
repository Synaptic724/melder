# Task: Finish FrameLink Contract And Cache FrameViewers
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-finish-frame-link-contract-and-cache-frame-viewers
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T04:40:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Finish the current contract/viewer layer by adding real `FrameLinkContract`
helper APIs and cached Nexus `FrameViewer` projection on top of the existing
cached `FrameView` bridge.

## Ticket Contract
- ENTRY_GATE: `FrameLinkContract`, `FrameLink`, `FrameView`, `FrameViewer`,
  Nexus projection, and cached `FrameView` projection are already landed.
- EXECUTION_BOUNDARY: contract-helper APIs plus cached `FrameViewer`
  projection only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_cache_nexus_frame_surface_projection.md
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: `FrameLinkContract` exposes real helper APIs, Nexus can cache
  projected viewers safely, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the next useful improvement
  requires a larger frame-surface architecture step.

## Scope Boundaries
- In scope:
  - `FrameLinkContract` helper/query methods
  - `FrameViewer` clone support
  - cached Nexus `FrameViewer` projection
  - explicit invalidation of cached viewers on touched frame/ACL mutation paths
  - focused tests
- Out of scope:
  - search DSL
  - subscriptions/update push model
  - holding-zone redesign

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the smallest useful contract-helper API set.
- [x] Implement the helper methods plus viewer clone support.
- [x] Implement cached Nexus viewer projection and invalidation.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- richer `FrameLinkContract` helper layer
- cached Nexus `FrameViewer` projection
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: cached viewers could return shared mutable state.
  Rollback: cache one canonical viewer and return detached clones only.
- Risk: contract helpers could just mirror raw metadata without real value.
  Rollback: keep only helpers that encode stable consumer-facing contract logic.

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
  - system_docs/patches/active/frame_link_contract_and_viewer_cache/architecture_patch.md
  - system_docs/patches/active/frame_link_contract_and_viewer_cache/component_patch_frame_link_contract.md
  - system_docs/patches/active/frame_link_contract_and_viewer_cache/component_patch_nexus.md
  - system_docs/patches/active/frame_link_contract_and_viewer_cache/component_patch_frame_viewer.md
  - system_docs/patches/active/frame_link_contract_and_viewer_cache/code_description_patch_contract_and_viewer_cache_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T04:40:00Z
  TYPE: PLAN
  CLAIM: The next bounded frame-surface slice is to finish the current
    contract/viewer layer, not to jump to a new subsystem. The most useful
    remaining gaps are:
    - `FrameLinkContract` still exposes mostly raw metadata with no real helper
      API
    - Nexus caches `FrameView` objects but not `FrameViewer` objects
    - `FrameViewer` lacks clone support needed for safe cached return paths
    The next cut should finish those pieces before another architecture jump.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-219
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-426
  - src/melder/aether/nexus/nexus.py:1362-1497
  - user_instruction: "finish off the contract and the viewer"
  IMPACT: We can still deliver meaningful contract/viewer value without
    widening into a larger holding-zone rewrite.
  NEXT: create the patch-doc set, then inspect the current contract/viewer
    surfaces for the smallest safe helper/cache additions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:42:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this finishing slice is now
    explicit. `architecture_patch.md` maps to keeping the helper/cache work
    bounded. `component_patch_frame_link_contract.md` maps to contract helper
    APIs. `component_patch_frame_viewer.md` maps to clone support. The
    `component_patch_nexus.md` doc maps to cached viewer projection. The
    `code_description_patch_contract_and_viewer_cache_flow.md` doc maps to the
    viewer cache hit/miss/invalidation flow.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_link_contract_and_viewer_cache/architecture_patch.md:1-17
  - codex/context_compass/system_docs/patches/active/frame_link_contract_and_viewer_cache/component_patch_frame_link_contract.md:1-11
  - codex/context_compass/system_docs/patches/active/frame_link_contract_and_viewer_cache/component_patch_nexus.md:1-11
  - codex/context_compass/system_docs/patches/active/frame_link_contract_and_viewer_cache/component_patch_frame_viewer.md:1-7
  - codex/context_compass/system_docs/patches/active/frame_link_contract_and_viewer_cache/code_description_patch_contract_and_viewer_cache_flow.md:1-10
  IMPACT: The implementation can stay on the current contract/viewer layer
    instead of drifting into a larger architecture move.
  NEXT: implement the contract helper APIs, viewer clone support, and cached
    Nexus viewer projection with focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:48:00Z
  TYPE: FACT
  CLAIM: The first focused finishing run exposed one real contract gap.
    `FrameLinkContract` helper APIs were added, but the base
    `from_compiled_access_surface(...)` path still only injected
    `frame_payload_fields`, `conduit_payload_sections_by_id`, and
    `spell_payload_sections_by_key` into metadata when a downstream contract
    profile was present. That makes the helper APIs weak on the default
    contract path. The fix belongs in the runtime contract construction, not in
    the test.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:74-159
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:468-495
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The contract should always carry the effective payload-section maps,
    even before any downstream narrowing profile is applied.
  NEXT: inject the base compiled payload-section maps into contract metadata by
    default, then rerun the finishing slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:50:00Z
  TYPE: FACT
  CLAIM: The current contract/viewer layer is now materially more complete.
    `FrameLinkContract` now has real helper APIs for:
    - `allows_kind(...)`
    - `allows_command(...)`
    - `get_frame_payload_fields()`
    - `get_conduit_payload_sections(...)`
    - `get_spell_payload_sections(...)`
    - `describe()`
    and those helpers now work both on the base compiled contract path and the
    narrowed downstream-profile path. `FrameViewer` now supports cloning, and
    Nexus now caches projected `FrameViewer` objects with explicit invalidation
    alongside the cached `FrameView` projection path.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-338
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-453
  - src/melder/aether/nexus/nexus.py:72-88
  - src/melder/aether/nexus/nexus.py:176-183
  - src/melder/aether/nexus/nexus.py:217-244
  - src/melder/aether/nexus/nexus.py:863-977
  - src/melder/aether/nexus/nexus.py:1269-1328
  - src/melder/aether/nexus/nexus.py:1419-1567
  IMPACT: The contract/viewer layer is now much closer to "finished enough" for
    current architectural purposes.
  NEXT: review whether to keep iterating on viewer richness or switch lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:50:00Z
  TYPE: MEASURE
  CLAIM: The focused finishing slice is green. The contract helper, viewer
    clone/cache, and Nexus projection validation surface passed with 58 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The current contract/viewer layer is stable enough to review as a
    bounded slice.
  NEXT: decide whether to continue iterating the frame-surface helpers or move
    back to another lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to finish the current contract/viewer layer before a larger
frame-surface architecture jump.



