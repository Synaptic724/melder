# Task: Implement Frame ACL Compiled Access Surface
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-implement-frame-acl-compiled-access-surface
- Story: STORY-2026-04-06-frame-acl-compiled-access-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T00:11:45Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement the compiled ACL access surface over payload-backed descriptor
records, suitable to feed `FrameLinkContract`.

## Ticket Contract
- ENTRY_GATE: typed ACL config and rule-aware validator are landed.
- EXECUTION_BOUNDARY: compiled access surface and compiler only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_implement_frame_acl_typed_configuration_foundation.md
  - tickets/tasks/2026-04-06_implement_frame_acl_validator_rule_validation.md
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- EXIT_GATE: compiled access surface exists, compiler consumes descriptor
  payloads + typed config, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the slice requires live
  viewer/event wiring first.

## Scope Boundaries
- In scope:
  - compiled access surface object
  - compiler over frame/conduit/spell descriptor payloads
  - focused tests
- Out of scope:
  - viewer implementation
  - event/update model
  - codegen executor integration

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Implement compiled access surface object.
- [x] Implement compiler over payload-backed descriptor records.
- [x] Shape output for later `FrameLinkContract` consumption.
- [x] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- compiled ACL access surface
- compiler implementation
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/
- src/melder/aether/nexus/rift/frame_link/
- tests/unit/melder/aether/

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py src/melder/aether/nexus/acl/frame_acl_compiler.py src/melder/aether/nexus/rift/frame_link/frame_link_contract.py src/melder/aether/nexus/rift/frame_link/profiles/frame_link_view_profile.py src/melder/aether/nexus/rift/frame_link/profiles/frame_link_codegen_profile.py src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile.py src/melder/aether/nexus/rift/frame_link/profiles/safe_profile.py src/melder/aether/nexus/rift/frame_link/profiles/hybrid_profile.py src/melder/aether/nexus/rift/frame_link/profiles/permissive_profile.py src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile_builder.py tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py`

## Risks / Rollback Notes
- Risk: compiler leaks raw config instead of effective answers.
  Rollback: keep compiled output strictly derived and consumer-facing.

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
  - system_docs/patches/active/frame_acl_compiled_access_surface/architecture_patch.md
  - system_docs/patches/active/frame_acl_compiled_access_surface/component_patch_frame_acl_compiler.md
  - system_docs/patches/active/frame_acl_compiled_access_surface/component_patch_frame_link_contract.md
  - system_docs/patches/active/frame_acl_compiled_access_surface/code_description_patch_compiled_access_surface.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T00:15:58Z
  TYPE: PLAN
  CLAIM: The compiled access tranche is now patch-gated. The correct abstraction
    point is the compiler boundary, not a giant generic ACL framework. So the
    next implementation should add:
    - one compiled access surface object
    - one compiler over payload-backed descriptor records + typed ACL config
    - one `FrameLinkContract` shaping path from compiled output
    while keeping the rules/profile/config model concrete.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-138
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:1-260
  - user_instruction: "the FrameLinkContract should properly define the configuration we have in the rift against the ACLs we have and the descriptor"
  IMPACT: The slice is now concretely bounded and patch-gated instead of drifting into vague compiler talk.
  NEXT: implement the compiled surface and align `FrameLinkContract` to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:15:58Z
  TYPE: DECISION
  CLAIM: The compiled access slice should also add a downstream
    `FrameLinkContract` profile foundation similar in spirit to the ACL profile
    catalog. The ACL compiler remains the source of effective access truth, but
    downstream contract profiles should shape how that effective truth is
    projected for Rift/view/codegen consumers. That means:
    - ACL compiler produces effective access truth
    - frame-link contract profiles shape downstream projection posture
    - `FrameLinkContract` is created from both compiled access truth and an
      optional downstream contract profile
    This keeps the downstream side extensible without letting it become a
    second ACL truth owner.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-138
  - user_instruction: "I think we should have FrameContractLink Profiles too and ultimately I think we might end up rebuilding this after we build the methods in the viewer and codegen"
  IMPACT: The compiled access slice now owns both the compiled access surface
    and the first downstream contract-profile foundation.
  NEXT: add a real `frame_link/profiles/` package and make `FrameLinkContract`
    consumable from compiled access output plus an optional downstream profile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:36:14Z
  TYPE: FACT
  CLAIM: The compiled access slice is now implemented in code. It now has:
    - `CompiledFrameACLAccessSurface`
    - `FrameACLCompiler`
    - `FrameLinkContract.from_compiled_access_surface(...)`
    - a downstream `frame_link/profiles/` package with reusable contract
      profiles
    The first focused compiler/contract tests passed.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:1-214
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:1-270
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-203
  - src/melder/aether/nexus/rift/frame_link/profiles/frame_link_view_profile.py:1-127
  - src/melder/aether/nexus/rift/frame_link/profiles/frame_link_codegen_profile.py:1-91
  - src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile.py:1-115
  - src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile_builder.py:1-137
  - tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py:1-171
  IMPACT: The ACL lane no longer stops at config + validator; it now has its
    first real downstream-facing effective contract output for frame-link
    consumers.
  NEXT: review whether the next ACL slice should wire this into `FrameLink` /
    `FrameView` or do another quality hardening pass on the new compiler and
    frame-link profile files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:36:14Z
  TYPE: MEASURE
  CLAIM: The compiled ACL access slice is green on its focused test surface.
    The focused compiler/frame-link contract tests passed with 2 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py
  IMPACT: The compiled access surface is now stable enough to be reviewed as a
    bounded slice instead of staying conceptual.
  NEXT: decide the next downstream ACL/frame-link step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task exists to implement the compiled ACL access surface after the typed
config and validator slices.



