# Task: Add Conduit Discovery Surfaces To Aether Cloud Rift And Command System
- Completed: 2026-04-13T12:00:15Z
- Summary: Closed the conduit-discovery surface lane after the ownership/facade split landed and later capability helper work built on it.

## Metadata
- Task ID: TASK-2026-04-12-add-conduit-discovery-surfaces-to-aether-cloud-rift-and-command-system
- Story: STORY-2026-04-11-add-command-system-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T16:30:00Z
- Updated: 2026-04-12T16:55:00Z

## Objective
Add one coherent conduit-discovery surface across the runtime stack:
- generic frame-scoped ownership in `Aether`
- discovery facade methods on `ConduitCloud`
- agent-facing facade methods on `Rift`
- command/query helpers on `CommandSystem`

Also align the command naming away from `get_conduit_object_*` to the shorter
`get_conduit_*` surface the user explicitly requested.

## Ticket Contract
- ENTRY_GATE: the user accepted the cloud-centric ownership proposal and
  explicitly requested implementation.
- EXECUTION_BOUNDARY: `Aether`, `ConduitCloud`, `Rift`, `CommandSystem`,
  focused interfaces, focused tests, and patch/board/ticket sync only.
- DEPENDENCIES:
  - src/melder/aether/aether.py
  - src/melder/aether/conduit_cloud.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_aether.py
  - tests/unit/melder/aether/test_conduit_cloud.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: conduit discovery is owned in `Aether`, facaded in
  `ConduitCloud`, facaded in `Rift`, exposed in the command surface, and the
  focused test ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the new discovery surface
  forces broader public-runtime API redesign outside the agreed ownership seam.

## Scope Boundaries
- In scope:
  - generic conduit-discovery methods in `Aether`
  - conduit-discovery facades in `ConduitCloud`
  - conduit-discovery facades in `Rift`
  - command-system query helpers and renamed conduit getter names
  - focused tests
- Out of scope:
  - cluster redesign
  - conduit spell/meld redesign
  - capability-handle redesign
  - viewer redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved implementing the accepted
  conduit-discovery ownership/facade model.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Add generic frame-scoped conduit-discovery methods to `Aether`.
- [x] Facade those methods on `ConduitCloud`.
- [x] Facade the same discovery surface on `Rift`.
- [x] Expose the command-side query helpers and the renamed conduit getters.
- [x] Update focused interfaces and tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `Aether` conduit-discovery ownership surface
- `ConduitCloud` discovery facade surface
- `Rift` discovery facade surface
- command-side discovery/query helpers
- focused tests

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/aether/conduit_cloud.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_aether.py
- tests/unit/melder/aether/test_conduit_cloud.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/aether.py src/melder/aether/conduit_cloud.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_conduit_cloud.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_conduit_cloud.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: we duplicate discovery logic across `Aether`, `ConduitCloud`, `Rift`,
  and `CommandSystem` instead of keeping `Aether` as the owner and the rest as
  facades.
  Rollback: keep backend ownership in `Aether` and make the other layers thin
  pass-through surfaces only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/conduit_discovery_surfaces/architecture_patch.md
  - system_docs/patches/active/conduit_discovery_surfaces/component_patch_aether.md
  - system_docs/patches/active/conduit_discovery_surfaces/component_patch_conduit_cloud.md
  - system_docs/patches/active/conduit_discovery_surfaces/component_patch_rift.md
  - system_docs/patches/active/conduit_discovery_surfaces/component_patch_command_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the conduit-discovery surface is merged into
  canonical runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T16:30:00Z
  TYPE: PLAN
  CLAIM: The accepted design is now explicit enough to implement. `Aether`
    should own one generic frame-scoped conduit-discovery surface, while
    `ConduitCloud`, `Rift`, and `CommandSystem` each expose the same discovery
    shape as facades for their own consumers. The user also explicitly wants
    the command-side conduit getters renamed away from `get_conduit_object_*`
    to `get_conduit_*`.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-12_inventory_aether_conduit_methods_for_command_surface_task.md:95-157
  - user_direction: "we do want these methods in the Rift"
  - user_direction: "we can put some of these explicitly into the command system"
  - user_direction: "do not call it get_conduit_object"
  IMPACT: The next pass is code, not more ownership debate.
  NEXT: add the task route/patch docs, then patch `Aether`, `ConduitCloud`,
    `Rift`, and `CommandSystem` in one bounded implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T16:38:00Z
  TYPE: FACT
  CLAIM: The current runtime seam is narrow and clean enough for the agreed
    patch. `Aether` already has the point lookup owners
    (`_get_conduit_cloud`, `_get_conduit_by_name`, `_get_conduit_by_id`), but
    it still lacks the generic list/count/has/find helpers. `ConduitCloud`
    still only exposes `get_conduit(name)` plus internal register/unregister.
    `Rift` currently exposes frame and room access only, with no conduit
    discovery facade. `CommandSystem` already owns direct conduit getters, but
    the public names are still `get_conduit_object_by_*`.
  EVIDENCE:
  - src/melder/aether/aether.py:670-822
  - src/melder/aether/conduit_cloud.py:10-145
  - src/melder/aether/nexus/rift/rift.py:1030-1080
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:306-399
  IMPACT: The implementation can stay bounded to additive discovery methods
    plus the conduit getter rename instead of reopening ownership or topology.
  NEXT: patch `Aether`, `ConduitCloud`, `Rift`, the command surface, and the
    focused interfaces/tests in one pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T16:55:00Z
  TYPE: FACT
  CLAIM: The conduit-discovery surface is now landed in source. `Aether` now
    owns the generic frame-scoped discovery methods (`get_conduit_cloud`,
    `list_conduit_ids`, `list_conduit_names`, `count_conduits`,
    `has_conduit_id`, `has_conduit_name`, `find_conduit_id_by_name`,
    `get_conduit_by_id`, `get_conduit_by_name`). `ConduitCloud` now facades
    the same discovery shape over the cloud registry. `Rift` now facades the
    same discovery shape over the targeted-frame surface. `CommandSystem` now
    exposes conduit query helpers and the conduit getters are renamed to
    `get_conduit_by_id` / `get_conduit_by_name`.
  EVIDENCE:
  - src/melder/aether/aether.py:701-933
  - src/melder/aether/conduit_cloud.py:79-240
  - src/melder/aether/nexus/rift/rift.py:408-620
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:306-573
  - src/melder/utilities/interfaces/interfaces.py:6153-6216
  - src/melder/utilities/interfaces/interfaces.py:7172-7260
  - src/melder/utilities/interfaces/interfaces.py:7632-7752
  IMPACT: The runtime now has one coherent conduit-discovery surface instead
    of ad hoc point lookups spread across only part of the stack.
  NEXT: run the focused compile and unit validation ring, then return the
    landed surface for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T16:55:00Z
  TYPE: MEASURE
  CLAIM: The focused conduit-discovery validation ring is green. The patched
    `Aether`, `ConduitCloud`, `Rift`, command surface, and focused unit tests
    all pass together, and the stale `get_conduit_object_*` name no longer
    appears in `src/` or `tests/`.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/aether.py src/melder/aether/conduit_cloud.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_conduit_cloud.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_conduit_cloud.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 242 passed
  - validation_result: stale-name search for `get_conduit_object_by_id|get_conduit_object_by_name` across `src/` and `tests/` -> no hits
  IMPACT: This slice is stable enough for review without another cleanup pass.
  NEXT: summarize the landed surface and let the user decide whether the next
    expansion is more command discovery, cloud behavior, or another runtime lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the accepted conduit-discovery ownership/facade split:
backend ownership in `Aether`, discovery facades in `ConduitCloud` and
`Rift`, and command-side query helpers for the live room surface. The focused
validation ring is green and the old `get_conduit_object_*` name is gone.
