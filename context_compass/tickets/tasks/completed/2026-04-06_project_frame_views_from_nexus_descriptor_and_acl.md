# Task: Project Frame Views From Nexus Descriptor And ACL
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-project-frame-views-from-nexus-descriptor-and-acl
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T03:45:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Expose the first real Nexus-side frame-surface projection bridge by letting
Nexus build `FrameView` and `FrameViewer` objects from descriptor truth plus
current ACL configuration.

## Ticket Contract
- ENTRY_GATE: the descriptor manager/canonical store exists, the compiled ACL
  contract exists, and the `FrameLink` / `FrameView` / `FrameViewer` layers
  now have real helper wiring.
- EXECUTION_BOUNDARY: Nexus-side projection bridge only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_wire_frame_link_and_frame_view_to_compiled_acl_contract.md
  - tickets/tasks/2026-04-06_wire_frame_viewer_to_projected_frame_views.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/acl/frame_acl_compiler.py
- EXIT_GATE: Nexus can build projected frame views/viewers from descriptor
  truth plus current ACL config and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a clean projection bridge
  requires a dedicated new manager instead of a bounded Nexus facade.

## Scope Boundaries
- In scope:
  - Nexus facade methods for building `FrameView`
  - Nexus facade methods for building `FrameViewer`
  - smallest supporting state/helpers for downstream contract profiles
  - focused tests
- Out of scope:
  - live update subscriptions
  - event propagation
  - full query DSL
  - a new standalone frame-surface manager

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the smallest Nexus facade for projecting views/viewers.
- [x] Implement the projection bridge.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- Nexus frame-view projection bridge
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: Nexus picks up too much projection-specific logic.
  Rollback: keep the facade thin and derive through existing compiler/view/viewer objects.

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
  - system_docs/patches/active/nexus_frame_surface_projection/architecture_patch.md
  - system_docs/patches/active/nexus_frame_surface_projection/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_surface_projection/code_description_patch_nexus_frame_projection.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T03:45:00Z
  TYPE: FACT
  CLAIM: The next real holding-zone bridge is Nexus-side projection, not
    another placeholder class. The canonical descriptor store already exists in
    `FrameDescriptorManager`, the current ACL config exists in
    `FrameACLManager`, and the frame-surface objects can already consume the
    compiled contract. The missing bridge is a thin Nexus facade that projects
    those pieces into `FrameView` / `FrameViewer` objects for consumers.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:1-573
  - src/melder/aether/nexus/nexus.py:176-180
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:1-270
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-350
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-281
  IMPACT: We can add a useful holding-zone-facing bridge without inventing a new manager yet.
  NEXT: create the patch-doc set, then implement thin Nexus projection helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:47:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this Nexus projection slice is
    now explicit. `architecture_patch.md` maps to keeping the bridge thin and
    derived-only. `component_patch_nexus.md` maps to adding Nexus facade
    helpers rather than a new manager. The
    `code_description_patch_nexus_frame_projection.md` doc maps to the
    descriptor -> compiler -> `FrameView` / `FrameViewer` flow and its fail-fast
    behavior.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/nexus_frame_surface_projection/architecture_patch.md:1-16
  - codex/context_compass/system_docs/patches/active/nexus_frame_surface_projection/component_patch_nexus.md:1-12
  - codex/context_compass/system_docs/patches/active/nexus_frame_surface_projection/code_description_patch_nexus_frame_projection.md:1-13
  IMPACT: The implementation can stay bounded to thin Nexus projection helpers
    instead of turning into a larger architecture rewrite.
  NEXT: implement the Nexus projection helpers and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:55:00Z
  TYPE: FACT
  CLAIM: The first focused Nexus projection run exposed one real facade
    contract bug. `create_frame_viewer(...)` validated `frame_names` entries
    too late, after it had already started projecting earlier frames. That
    meant bad input sequences could raise missing-descriptor errors before the
    intended invalid-input error. The helper needs to validate the whole
    `frame_names` sequence up front before it touches descriptor state.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1434-1459
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:223-231
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The fix belongs in the Nexus facade, not in the test.
  NEXT: validate the full `frame_names` sequence before projecting any views,
    then rerun the focused Nexus projection slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:58:00Z
  TYPE: FACT
  CLAIM: The thin Nexus projection bridge is now implemented. Nexus now has
    thin facade helpers that:
    - build a `FrameView` from one required descriptor plus the current ACL
      configuration
    - compile the effective ACL surface on demand
    - optionally apply one downstream frame-link contract profile by name
    - assemble one `FrameViewer` from multiple projected frame views
    The bridge stays facade-thin and does not create a new manager.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1353-1462
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-231
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:1-115
  IMPACT: The holding-zone substrate can now be consumed through a real Nexus
    projection path instead of manual descriptor/compiler wiring.
  NEXT: review whether the next frame-surface slice should add richer Nexus
    projection helpers or pause for the deeper holding-zone evolution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:58:00Z
  TYPE: MEASURE
  CLAIM: The focused Nexus projection slice is green. The projection unit and
    integration surface passed with 28 tests after the input-validation-order
    fix in `create_frame_viewer(...)`.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The Nexus projection bridge is stable enough to review as a bounded
    slice.
  NEXT: decide whether to keep iterating the Nexus projection helpers or move
    back to another lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to expose projected frame views/viewers from Nexus using the
existing descriptor and ACL layers.



