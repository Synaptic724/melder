# Task: Implement Rooted Spellbook-Mediated Nexus Creation
- Completed: 2026-04-22T11:14:18Z
- Summary: Closed during the 2026-04-22 rebaseline after the Spellbook-mediated rooted Nexus creation contract landed, validated, and survived the first fallout cleanup pass.

## Metadata
- Task ID: TASK-2026-04-22-implement-rooted-spellbook-mediated-nexus-creation
- Story: STORY-2026-04-22-design-and-implement-rooted-spellbook-mediated-nexus-creation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-22T00:02:36Z
- Updated: 2026-04-22T11:14:18Z

## Objective
Refactor Nexus-managed creation so the public Nexus/Rift-facing path creates a
Spellbook, conjures a root conduit by default, allows the caller to name that
root conduit, and returns the rooted conduit instead of the frame.

## Ticket Contract
- ENTRY_GATE: the epic and story are active, and the current broken creation
  chain is source-backed.
- EXECUTION_BOUNDARY: Nexus/Rift/frame-manager/frame-builder/frame-configuration
  creation surfaces, directly affected interfaces/tests/docs, and the active
  patch-doc set only.
- DEPENDENCIES:
  - tickets/epics/2026-04-21_refactor_nexus_frame_realization_into_spellbook_mediated_rooted_creation_epic.md
  - tickets/stories/2026-04-22_design_and_implement_rooted_spellbook_mediated_nexus_creation_story.md
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/architecture_patch.md
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/component_patch_nexus_frame_manager.md
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/component_patch_rift.md
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/component_patch_nexus.md
- EXIT_GATE: the Nexus/Rift-facing creation path is Spellbook-mediated, rooted
  by default, root-conduit-nameable, conduit-returning, and the bounded tests/docs
  are green/current.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if preserving lower raw manager
  internals while changing the public return shape proves contradictory.

## Scope Boundaries
- In scope:
  - `NexusFrameManager`
  - `NexusFrameBuilder`
  - `NexusFrameConfiguration`
  - `Nexus.create_nexus_frame_for_rift(...)`
  - `Rift.create_nexus_frame(...)`
  - directly affected interfaces/tests/docs
- Out of scope:
  - unrelated ACL/viewer work
  - auto-provisioning policy
  - unrelated lower-runtime redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the rooted Spellbook-mediated creation contract is
  implemented, docs are updated, and the bounded validation ring is green.

## Steps / Checklist
- [x] Read the current creation call chain and direct callers fully enough to patch without cheating.
- [x] Define the default root-conduit naming rule and the explicit caller override.
- [x] Refactor Nexus-managed creation to go through `Spellbook` + `conjure(...)`.
- [x] Change the public Nexus/Rift-facing return shape from frame to conduit.
- [x] Keep descriptor/ACL/publication state aligned with the rooted result.
- [x] Update interfaces, docs, and focused tests.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- rooted Spellbook-mediated Nexus-managed creation
- caller-nameable root conduit
- conduit-returning public Nexus/Rift creation surface
- updated focused docs/tests

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/nexus_frame_manager.py
- src/melder/aether/nexus/nexus_frame_builder.py
- src/melder/aether/nexus/nexus_frame_configuration.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_builder.py tests/unit/melder/aether/test_nexus_frame_configuration.py tests/unit/melder/aether/test_nexus_frame_manager.py tests/unit/melder/aether/test_nexus_frame_authoring.py tests/unit/melder/aether/test_nexus.py -k "nexus_frame or create_nexus_frame or get_nexus_frame or accessible_nexus_frame or one_per_workspace or shared_nexus_frame or external_aether_frame_cleanup" tests/component/melder/aether/test_nexus_frame_authoring_component.py tests/integration/melder/aether/test_nexus_frame_authoring_integration.py`
- Result:
  - `230 passed, 101 deselected, 2 warnings`

## Risks / Rollback Notes
- Risk: changing the return type from frame to conduit will break more callers than expected.
  Rollback: keep the change bounded to the Nexus/Rift-facing creation surface and patch every direct caller/test in the same lane.
- Risk: default root-conduit naming becomes implicit and uninspectable.
  Rollback: make the naming contract explicit in config/builder docs and tests.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/architecture_patch.md
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/component_patch_nexus_frame_manager.md
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/component_patch_rift.md
  - system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/component_patch_nexus.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: apply closure disposition after acceptance.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-22T00:02:36Z
  TYPE: PLAN
  CLAIM: This task implements the corrected creation grammar under the new epic.
    It should not cheat by leaving the frame-first path in place and just slapping
    on an optional root bootstrap afterward.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:200-317
  - src/melder/spellbook/spellbook.py:3379-3473
  - user_instruction: "make sure the agent gets a chance to fucken name the root conduit"
  - user_instruction: "it must go through the spellbook and then conjure the conduit and then return the fucken conduit not the frame"
  IMPACT: The implementation must change both realization order and public result shape, not just add a default root name.
  NEXT: inspect all direct callers/tests of `create_nexus_frame(...)` and the builder/configuration surfaces before patching.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T00:02:36Z
  TYPE: FACT
  CLAIM: The return-shape migration is wide but bounded. `Rift.create_nexus_frame(...)`
    is used across unit/component/integration Nexus frame-authoring tests, and
    the current builder/configuration layer still models `root_conduit_name` as
    optional while the interface layer still advertises `IAethericFrame`
    return types.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:948-972
  - src/melder/utilities/interfaces/interfaces.py:7926-7941
  - src/melder/aether/nexus/nexus_frame_builder.py:165-187
  - src/melder/aether/nexus/nexus_frame_configuration.py:55-79
  - tests/unit/melder/aether/test_nexus.py:4299-4520
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:143-326
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:69-317
  IMPACT: The implementation must update the public return contract, builder/config root semantics,
    and the direct caller expectations together in one lane.
  NEXT: inspect the rest of the interface/Nexus call chain and then patch the
    realization order plus return type in one pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T00:02:36Z
  TYPE: FACT
  CLAIM: The public implementation path should use the public Spellbook API
    directly: build `Configuration`, create `Spellbook`, then call
    `spellbook.conjure(name=..., automatic=False)`. Wiring against
    `SpellbookCreationSystem` directly would be the wrong abstraction level for
    this lane.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:136-193
  - src/melder/spellbook/spellbook.py:3379-3473
  - user_instruction: "your job is literally just to use spellbook.conjure not Spellbookcreation"
  IMPACT: The Nexus creation refactor should target the public Spellbook API,
    not an internal helper path.
  NEXT: patch the Nexus-facing creation flow around `Spellbook(...).conjure(...)`
    and update the return-shape callers/tests in the same change set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T00:02:36Z
  TYPE: MEASURE
  CLAIM: The bounded implementation ring is green. Nexus/Rift-facing managed
    creation is now Spellbook-mediated, rooted by default, caller-nameable,
    conduit-returning, and the returned root conduit now collapses the frame and
    Nexus-managed state when it is the last conduit in the frame.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:183-985
  - src/melder/aether/nexus/rift/rift.py:929-976
  - src/melder/aether/nexus/nexus.py:2023-2098
  - src/melder/aether/conduit/conduit.py:359-383
  - src/melder/utilities/interfaces/interfaces.py:7925-7941
  - codex/context_compass/system_docs/src_architecture.md:323-324
  - codex/context_compass/system_docs/src_architecture.md:396-404
  - codex/context_compass/system_docs/src_components.md:506-524
  - codex/context_compass/system_docs/src_components.md:1896-1909
  IMPACT: The public Nexus creation grammar is now aligned with the repo’s
    Spellbook/conjure model instead of exposing frame-first empty-shell
    creation.
  NEXT: review the landed contract cut and decide whether to accept this lane
    or open follow-on cleanup around remaining frame-returning helper surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T00:02:36Z
  TYPE: FACT
  CLAIM: The first direct stale-fallout pass after the rooted creation cut did
    not expose another code-path regression. The remaining obvious fallout was
    stale tests/docs/patch-doc wording around frame-returning or root-optional
    assumptions, and that bounded set has been updated.
  EVIDENCE:
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_nexus_frame_authoring.py
  - tests/unit/melder/aether/test_nexus_frame_builder.py
  - tests/unit/melder/aether/test_nexus_frame_configuration.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - codex/context_compass/system_docs/patches/active/nexus_rooted_spellbook_mediated_creation/component_patch_rift.md
  IMPACT: The contract cut is now coherent across the bounded source/test/doc
    surfaces exercised by the Nexus frame-authoring lane.
  NEXT: use the fallout epic only if another stale seam directly downstream of
    this creation contract appears.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T10:41:57Z
  TYPE: DECISION
  CLAIM: The bounded implementation slice owned by this task is complete. The
    core rooted creation contract landed, the executed Nexus frame-authoring ring
    is green, and the remaining direct downstream cleanup has been split into the
    separate fallout epic instead of being left as implicit extra scope here.
  EVIDENCE:
  - tickets/epics/2026-04-22_cleanup_stale_fallout_from_rooted_nexus_creation_refactor_epic.md:1-152
  - tickets/tasks/2026-04-22_cleanup_rooted_nexus_creation_fallout_task.md:1-76
  IMPACT: This task should remain in review for acceptance, not in disguised
    implementation mode.
  NEXT: review the task outcome and either accept it or identify a new explicit
    follow-on seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the new rooted Spellbook-mediated Nexus creation contract
under the epic and story created for that lane. The implementation and bounded
validation ring are complete; only user acceptance or a new explicit follow-on
lane remains.
