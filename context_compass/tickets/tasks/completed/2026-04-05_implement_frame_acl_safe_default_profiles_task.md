# Task: Implement Frame ACL Named Default Profile Catalog
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-05-implement-frame-acl-safe-default-profiles
- Story: STORY-2026-04-05-frame-acl-profile-builder-foundation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T23:45:34Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement a named reusable ACL profile catalog in the manager-owned profile
builder/library by replacing the single placeholder default with curated
`safe`, `permissive`, and `hybrid` view/codegen profiles plus ACL profile
version metadata.

## Ticket Contract
- ENTRY_GATE: the ACL profile builder/library foundation is landed and the user
  explicitly asked to replace the generic default with real named profiles:
  `safe`, `permissive`, and `hybrid`.
- EXECUTION_BOUNDARY: named reusable view/codegen profile content, ACL profile
  version metadata, and focused ACL profile/manager tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_implement_frame_acl_profile_builder_foundation.md
  - src/melder/aether/nexus/acl/frame_acl_profile.py
  - src/melder/aether/nexus/frame_acl_manager.py
- EXIT_GATE: reusable view/codegen profile registries are seeded with
  `safe`, `permissive`, and `hybrid`, those profiles carry curated non-empty
  rule content, ACL profiles expose version metadata, and focused validation
  passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the safe-default rule content
  forces typed `FrameACLConfiguration` work immediately.

## Scope Boundaries
- In scope:
  - default reusable view profile rules
  - default reusable codegen profile rules
  - ACL profile version metadata
  - focused ACL profile/manager/Nexus profile tests
- Out of scope:
  - typed `FrameACLConfiguration`
  - validator rewrite against descriptor payloads
  - codegen AST validation model
  - compiled access-surface implementation

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Implement `safe`, `permissive`, and `hybrid` view rulesets.
- [x] Implement `safe`, `permissive`, and `hybrid` codegen rulesets.
- [x] Add ACL profile version metadata.
- [x] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- named reusable view profile catalog
- named reusable codegen profile catalog
- ACL profile version metadata
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_profile.py
- tests/unit/melder/aether/test_frame_acl_profile.py
- tests/unit/melder/aether/test_nexus_frame_acl_profiles.py

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_profile.py src/melder/aether/nexus/frame_acl_manager.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py`

## Risks / Rollback Notes
- Risk: the named profile ladder overexposes deep spell/member surfaces or
  codegen powers too early.
  Rollback: keep `safe` restrictive, let `hybrid` be the middle tier, and keep
  the strongest permissions isolated to `permissive`.

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
  - system_docs/patches/active/frame_acl_safe_defaults/architecture_patch.md
  - system_docs/patches/active/frame_acl_safe_defaults/component_patch_frame_acl_profile.md
  - system_docs/patches/active/frame_acl_safe_defaults/code_description_patch_default_acl_profiles.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T23:45:34Z
  TYPE: FACT
  CLAIM: The default reusable ACL profiles are currently structurally present
    but behaviorally empty. The builder seeds `"default"` view and codegen
    profiles immediately, but the corresponding rulesets are empty lists across
    frame/conduit/spell/member and capability categories. The user has now
    explicitly requested safe defaults so the next slice should fill those
    defaults with restrictive view and codegen rule content instead of leaving
    them as placeholders.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:748-752
  - src/melder/aether/nexus/acl/frame_acl_profile.py:867-869
  - src/melder/aether/nexus/acl/frame_acl_profile.py:1020-1021
  - tests/unit/melder/aether/test_frame_acl_profile.py:96-117
  - user_instruction: "yeah lets do safe defaults"
  IMPACT: The reusable ACL profile substrate is not useful enough yet for real
    typed configuration work until the default profile content exists.
  NEXT: encode the safe default view/codegen rules and add version metadata to
    the ACL profiles while keeping the slice bounded.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:45:34Z
  TYPE: DECISION
  CLAIM: The single seeded `"default"` profile is no longer the right target.
    The user explicitly wants the reusable ACL profile catalog to use real
    names and tiers:
    - `safe`
    - `permissive`
    - `hybrid`
    and wants those built out for both view and codegen. So this task is now
    widened from "fill one safe default" to "seed a real named profile
    catalog", while still staying bounded to reusable profile content and not
    drifting into typed `FrameACLConfiguration` yet.
  EVIDENCE:
  - user_instruction: "you should give the acl profiles you made the real names like safe, permissive, hybrid"
  - user_instruction: "build them all out for both codegen and the other one"
  - src/melder/aether/nexus/acl/frame_acl_profile.py:996-1084
  IMPACT: The builder should stop assuming one generic default and should seed a
    named reusable profile ladder instead.
  NEXT: update the patch docs and ACL profile code so the builder seeds
    `safe`, `permissive`, and `hybrid` for both view and codegen, with tests
    asserting the new catalog.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:51:00Z
  TYPE: MEASURE
  CLAIM: The named reusable ACL profile catalog is green on the focused ACL
    surface. The builder now seeds `safe`, `hybrid`, and `permissive` for both
    view and codegen, those profiles carry curated non-empty rule content,
    ACL profiles expose version metadata, and the focused ACL profile/manager
    tests passed.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:683-1084
  - src/melder/aether/nexus/frame_acl_manager.py:712-735
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py
  IMPACT: The reusable ACL profile substrate now has real named tiers instead
    of an empty generic default, so typed configuration work can build on a
    meaningful baseline.
  NEXT: review whether the next ACL slice should be typed
    `FrameACLConfiguration` / `FrameACLViewConfiguration`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to add the first curated safe default rule content on top of
the landed ACL profile builder/library foundation.



