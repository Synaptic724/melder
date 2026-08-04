# Task: Investigate FrameView Removal Impacts And Payload Contract Gates
- Completed: 2026-04-09T21:59:36Z
- Summary: Documented the remove-FrameView impacts and staged the safe payload-validation then viewer-collapse order.


## Metadata
- Task ID: TASK-2026-04-06-investigate-frame-view-removal-impacts-and-payload-contract-gates
- Story: STORY-2026-04-06-validate-descriptor-acl-payload-contracts-and-collapse-frame-view
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T16:52:25Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Document the concrete consequences of removing `FrameView`, document the weak
descriptor<->ACL payload contract points, and define the safe implementation
order before any runtime edits begin.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a staged investigation-first pass.
- EXECUTION_BOUNDARY: investigation, documentation, and routing only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile_builder.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - src/melder/aether/nexus/frame_descriptor/
- EXIT_GATE: remove-`FrameView` impacts and payload-contract gaps are
  documented with evidence and the implementation order is clear.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the viewer still needs a
  hidden intermediate aggregate object.

## Scope Boundaries
- In scope:
  - `FrameView` runtime responsibilities
  - `FrameViewer` dependencies on `FrameView`
  - Nexus construction/caching dependence on `FrameView`
  - descriptor payload contract gaps
  - ACL payload validation gaps
- Out of scope:
  - runtime code edits
  - tests
  - codegen behavior

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the impact investigation and safe implementation order
  are documented, and the user approved moving into the first implementation
  tranche.

## Steps / Checklist
- [ ] Document what `FrameView` currently owns.
- [ ] Document what `FrameViewer` currently delegates to `FrameView`.
- [ ] Document where Nexus still constructs/caches `FrameView`.
- [ ] Document the current descriptor payload contract shape and its gaps.
- [ ] Document the current ACL payload validation limits.
- [ ] Recommend the safe implementation order.

## Deliverables
- evidence-backed impact notes
- recommended implementation order

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-06_investigate_frame_view_removal_impacts_and_payload_contract_gates.md
- codex/context_compass/attention_board.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: investigation understates how much state currently lives on `FrameView`.
  Rollback: keep the investigation task open until the dependency map is
  explicit.

## Applicable Anti-Patterns
- [ ] No implementation from partial impact analysis.
- [ ] No payload-validation claims without source evidence.
- [ ] No closure without user acceptance and board sync.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed
- [ ] Notes quality maintained
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: FACT
  CLAIM: Removing `FrameView` is a real architecture cut, not a cosmetic file
    delete. `FrameView` currently owns local active profile runtime,
    default-profile state, target grouping/order methods, and the
    `from_compiled_access_surface(...)` bridge from descriptor truth plus
    compiled ACL output. `FrameViewer` then stores `FrameView` objects by frame
    name and delegates target listing, target description, and view-profile
    selection down into those views. Nexus also still constructs `FrameView`
    directly in `create_frame_view(...)` and then uses that path in
    `create_frame_viewer(...)` and the Rift-facing viewer builders.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:35-214
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:422-476
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:706-784
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile.py:8-117
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile_builder.py:12-65
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:35-140
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:693-819
  - src/melder/aether/nexus/nexus.py:1477-1660
  IMPACT: We cannot remove `FrameView` safely until we first move or delete
    those responsibilities intentionally.
  NEXT: document the payload-contract gap so the implementation order is clear.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: FACT
  CLAIM: The descriptor<->ACL payload contract is still too weak for a direct
    descriptor-driven viewer path. Descriptor payloads do exist and are typed,
    but the handshake is loose:
    - `SpellDescriptorPayload` preserves a `profile_name` and rich payload
      sections, but no explicit version contract.
    - `ConduitDescriptorPayload` and `FrameDescriptorPayload` only advertise
      fixed family names (`conduit`, `frame`).
    - `CompiledFrameACLAccessSurface` carries visible field/section names and
      view/codegen profile name/version, but not projected payload bodies.
    - `FrameACLViewConfiguration` only declares
      `minimum_spell_payload_profile_name`.
    - `FrameACLValidator` still validates that minimum spell payload name
      against a hardcoded supported-name set; it does not validate a real
      frame/conduit/spell payload contract against descriptor truth.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:77-190
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:9-61
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:8-89
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:9-59
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:171-223
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:14-52
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:189-209
  - src/melder/aether/nexus/acl/frame_acl_validator.py:17-40
  - src/melder/aether/nexus/acl/frame_acl_validator.py:195-258
  IMPACT: Payload validation must land before `FrameView` is removed, or the
    viewer will just inherit a weak string-mapped contract directly.
  NEXT: recommend the implementation order and create the implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: DECISION
  CLAIM: The safe implementation order is:
    1) add descriptor<->ACL payload contract validation,
    2) gate viewer creation on that validation,
    3) only then remove `FrameView` and rewire `FrameViewer` to execute
       directly against descriptor-organized frame -> conduit -> spell data.
    Doing it in the opposite order would collapse the intermediate layer before
    the descriptor/ACL contract is strong enough to replace it cleanly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:214-328
  - src/melder/aether/nexus/acl/frame_acl_validator.py:195-258
  - user_instruction: "the descriptor and ACL must merry up"
  - user_instruction: "lets remove the view, as well we don't need that and lets just use the viewer"
  IMPACT: The next two tasks are now correctly ordered and should not be
    combined into one blind runtime rewrite.
  NEXT: create the payload-validation task and the runtime-collapse task, then
    reroute the board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This is the active investigation task for the remove-`FrameView` lane. It
exists to make the dependency map and implementation order explicit before any
runtime edits start.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

