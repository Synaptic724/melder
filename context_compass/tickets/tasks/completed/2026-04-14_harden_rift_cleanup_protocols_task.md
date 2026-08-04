# Task: Harden Rift Cleanup Protocols
- Completed: 2026-04-25T21:59:28Z
- Summary: Closed after the Rift/Nexus cleanup hardening sweep landed,
  validated green, and the Nexus-directory cleanup inventory no longer showed
  unlocked direct `cleanup()` implementations.

## Metadata
- Task ID: TASK-2026-04-14-harden-rift-cleanup-protocols
- Epic: EPIC-2026-04-13-investigate-april-11-12-aethericrift-history-and-next-steps
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-14T11:38:43Z
- Updated: 2026-04-25T21:59:28Z

## Objective
Bring the Rift-side cleanup chain up to the current ownership spec:
owned objects cleanup deterministically under lock, top-level owners actually
cleanup what they own, and the touched cleanup docstrings describe the real
teardown behavior.

## Ticket Contract
- ENTRY_GATE: the Nexus/static investigation already identified a concrete gap
  in the Rift ownership teardown, and the user explicitly requested cleanup
  hardening now.
- EXECUTION_BOUNDARY: Rift-side cleanup/ownership/docstring fixes only.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-13_investigate_nexus_static_space_and_creation_flow_task.md
  - codex/context_compass/system_docs/patches/active/rift_cleanup_protocol_hardening/architecture_patch.md
  - codex/context_compass/system_docs/patches/active/rift_cleanup_protocol_hardening/component_patch_rift.md
  - codex/context_compass/system_docs/patches/active/rift_cleanup_protocol_hardening/component_patch_room_stack.md
  - codex/context_compass/system_docs/patches/active/rift_cleanup_protocol_hardening/component_patch_support_managers.md
- EXIT_GATE: the Rift-side ownership chain cleans owned objects deterministically
  and the focused AR unit ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a required cleanup fix would
  cross the current AR boundary into lower Melder runtime semantics.

## Scope Boundaries
- In scope:
  - `Rift.cleanup()` ownership teardown
  - cleanup locking/ordering on touched Rift-side objects
  - touched cleanup docstrings/comments
  - focused AR validation
- Out of scope:
  - lower Melder runtime cleanup outside the Rift stack
  - codegen execution behavior
  - unrelated refactors

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the user directed closure for finished AR tickets and this
  task already had landed fixes, focused validation, and a clean Nexus cleanup
  inventory sweep in its note set.

## Steps / Checklist
- [ ] Stage and consume patch docs for the cleanup slice.
- [ ] Audit the owned cleanup chain in the Rift stack.
- [ ] Fix the concrete ownership/cleanup gaps with lock-disciplined teardown.
- [ ] Update touched cleanup docstrings to match behavior.
- [ ] Run focused AR validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- hardened Rift cleanup chain
- updated cleanup docstrings
- focused AR validation evidence

## Files / Paths Impacted
- src/melder/aether/nexus/rift/
- codex/context_compass/tickets/tasks/2026-04-14_harden_rift_cleanup_protocols_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: cleanup hardening drifts into non-Rift ownership layers.
  Rollback: keep the slice bounded to Rift-owned objects and documented manager
  teardown only.

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
  - system_docs/patches/active/rift_cleanup_protocol_hardening/architecture_patch.md
  - system_docs/patches/active/rift_cleanup_protocol_hardening/component_patch_rift.md
  - system_docs/patches/active/rift_cleanup_protocol_hardening/component_patch_room_stack.md
  - system_docs/patches/active/rift_cleanup_protocol_hardening/component_patch_support_managers.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the cleanup hardening is merged into canonical docs or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-14T11:38:43Z
  TYPE: PLAN
  CLAIM: The first concrete cleanup hardening target is the Rift ownership
    chain itself. The current investigation already proved that most lower
    Rift-side objects have explicit cleanup methods, but `Rift.cleanup()` drops
    owned room/config references without first cleaning the owned rooms or the
    owned per-Rift configuration snapshot.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-13_investigate_nexus_static_space_and_creation_flow_task.md:286-304
  - src/melder/aether/nexus/rift/rift.py:256-303
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:162-205
  IMPACT: We need an implementation slice, not another investigation pass.
  NEXT: stage patch docs, audit the immediate owned cleanup chain, and patch the
    concrete ownership gap first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T11:38:43Z
  TYPE: FACT
  CLAIM: The first implementation cut stayed narrow and matched the proved gap.
    `Rift.cleanup()` now cleans every owned room and the owned per-Rift
    configuration snapshot before dropping registry/data references. I did not
    widen the patch into the lower room-stack or manager cleanup methods because
    the source already showed those using explicit cleanup methods and instance
    locks. The only test fallout came from two `test_rift_runtime_contracts`
    cases registering `SimpleNamespace` room doubles that did not satisfy the
    room cleanup contract; those tests now use a tiny cleanup-capable room
    double instead of weakening `Rift.cleanup()`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:256-303
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:26-60
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:489-531
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:553-572
  IMPACT: The top-level AR ownership chain is now materially safer without
    inventing defensive cleanup probing or a broader unproven refactor.
  NEXT: record validation and return the cleanup hardening for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T11:38:43Z
  TYPE: MEASURE
  CLAIM: The cleanup hardening is green on the focused AR unit ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 128 passed
  IMPACT: The narrow Rift-side cleanup fix is stable enough to return for
    review instead of widening immediately into unrelated cleanup sweeps.
  NEXT: ask whether to close this task or continue auditing other non-Rift AR
    cleanup ownership layers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T22:02:12Z
  TYPE: FACT
  CLAIM: The hardening scope has now been widened to the Nexus-owned stack
    pieces that still violated the requested cleanup style. Beyond the
    `Rift.cleanup()` ownership fix, the remaining Nexus-side objects that still
    cleaned without an instance lock were:
    - `FrameACLConfiguration`
    - `FrameViewerProfile`
    - `RiftEventConfiguration`
    Those classes now own an instance `RLock` and use it in cleanup, while the
    already-locking Nexus managers/records/descriptors were left unchanged.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:49-89
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:366-393
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:16-57
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:760-789
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py:8-36
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py:76-96
  IMPACT: The Nexus-owned cleanup story is now materially closer to the spec
    you asked for instead of only fixing the top-level Rift owner.
  NEXT: return the Nexus-stack cleanup hardening for review instead of widening
    further without another proved gap.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T23:22:59Z
  TYPE: FACT
  CLAIM: A full Nexus-directory cleanup sweep now leaves one bounded remainder:
    twelve direct cleanup implementations still lack owned lock discipline or,
    in the case of the general viewer profile, explicit use of the inherited
    profile lock. The remaining set is:
    - `FrameACLCompiler`
    - `FrameACLRule`
    - `FrameACLSetCompatibilityReport`
    - `ConduitDescriptorPayload`
    - `ConduitRecord`
    - `FrameDescriptorPayload`
    - `FrameRecord`
    - `SpellDescriptorPayload`
    - `SpellRecord`
    - `GeneralFrameViewerProfile`
    - `GeneralViewConduit`
    - `GeneralViewSpell`
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:25-67
  - src/melder/aether/nexus/acl/configurations/profiles/rules/frame_acl_rule.py:8-91
  - src/melder/aether/nexus/acl/validator/compatibility/frame_acl_set_compatibility_report.py:8-77
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:9-102
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:9-112
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:8-116
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:9-107
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:85-263
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:11-162
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:23-191
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:11-61
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:17-68
  IMPACT: The remaining work is no longer an open-ended Nexus sweep. It is one
    same-pattern patch across ACL leaf classes, descriptor payload/record
    value objects, and the general viewer helper stack.
  NEXT: patch that bounded remainder to use instance-lock cleanup discipline,
    then rerun the focused AR validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T23:22:59Z
  TYPE: FACT
  CLAIM: The bounded Nexus remainder is now patched. The direct ACL leaf
    classes and descriptor payload/record objects now own instance `RLock`s
    for grouped cleanup, and the general viewer profile/helper stack now runs
    cleanup under explicit lock discipline instead of unguarded teardown.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:25-87
  - src/melder/aether/nexus/acl/configurations/profiles/rules/frame_acl_rule.py:8-108
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:9-132
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:11-184
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:23-191
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:11-74
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:17-81
  IMPACT: The cleanup hardening lane now has one consistent contract across the
    remaining Nexus leaf/helper objects instead of a mixed lock/no-lock teardown
    story.
  NEXT: run the focused AR validation ring and record the result before any
    closure decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T23:25:27Z
  TYPE: MEASURE
  CLAIM: The widened Nexus cleanup hardening patch is green on a targeted
    Nexus/ACL/viewer validation ring that exercises the changed cleanup
    classes directly, plus the older Rift/Nexus runtime-contract coverage.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/acl/frame_acl_compiler.py src/melder/aether/nexus/acl/configurations/profiles/rules/frame_acl_rule.py src/melder/aether/nexus/acl/validator/compatibility/frame_acl_set_compatibility_report.py src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/conduit_record.py src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/frame_record.py src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/spell_record.py src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_conduit_descriptor_payload.py tests/unit/melder/aether/test_conduit_record.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_spell_descriptor_payload.py tests/unit/melder/aether/test_spell_record.py tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 289 passed
  IMPACT: The cleanup hardening now has direct syntax coverage and a real unit
    ring over ACL, descriptor, viewer, Rift, and Nexus surfaces, so this task
    is in review territory rather than another blind sweep.
  NEXT: return the cleanup hardening for acceptance and decide whether to close
    the task or keep searching for another concrete Nexus-owned cleanup gap.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T23:25:55Z
  TYPE: MEASURE
  CLAIM: The post-patch Nexus inventory scan is clean. There are no remaining
    files under `src/melder/aether/nexus` that define `cleanup()` without any
    `_lock` usage.
  EVIDENCE:
  - validation_result: `Get-ChildItem src/melder/aether/nexus -Recurse -Filter *.py | ... if (($content -match '^\s*def cleanup\(') -and -not ($content -match '\b_lock\b')) ...` -> no output
  IMPACT: The requested Nexus-directory cleanup sweep is complete at the
    mechanical inventory level, not just the unit-test level.
  NEXT: return the cleanup sweep for acceptance and decide whether to close the
    task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the current Rift-side cleanup hardening slice.
