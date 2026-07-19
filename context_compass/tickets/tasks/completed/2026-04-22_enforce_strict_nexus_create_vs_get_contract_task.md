# Task: Enforce Strict Nexus Create Vs Get Contract
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the strict create/get contract landed and the lane moved on.

## Metadata
- Task ID: TASK-2026-04-22-enforce-strict-nexus-create-vs-get-contract
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-22T11:14:18Z
- Updated: 2026-04-24T01:03:27Z

## Objective
Make Nexus-managed frame creation strict-create only: if the target frame
already exists, creation must raise, while recovery remains getter-only and
still returns the rooted conduit.

## Ticket Contract
- ENTRY_GATE: the rooted-conduit return contract is already landed, but the
  source and tests still preserve create-or-recover semantics in the Nexus
  create path.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aether.py`
  - `src/melder/spellbook/spellbook.py` only if required by the strict-create
    enforcement seam
  - `src/melder/aether/nexus/nexus_frame_manager.py`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/rift/rift.py`
  - directly affected Nexus frame-authoring tests
  - directly affected docs if the contract wording changes materially
- DEPENDENCIES:
  - tickets/tasks/completed/2026-04-22_implement_rooted_spellbook_mediated_nexus_creation_task.md
  - tickets/epics/completed/2026-04-21_refactor_nexus_frame_realization_into_spellbook_mediated_rooted_creation_epic.md
- EXIT_GATE: create paths raise when the frame already exists, getter paths
  recover rooted conduits only, and the focused test ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if enforcing strict-create in
  Aether requires a broader Spellbook/public-runtime contract change than this
  bounded pass should own.

## Scope Boundaries
- In scope:
  - strict-create behavior for Nexus-managed frame creation
  - Aether-side strict frame-create helper
  - removal of create-or-recover behavior from Nexus create paths
  - tests that currently encode recovery-through-create
- Out of scope:
  - unrelated viewer/ACL/runtime cleanup
  - changing getter semantics away from rooted-conduit recovery
  - broad lower-runtime frame-model redesign beyond the create helper seam

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the strict-create runtime/test/doc pass is complete and
  the focused validation ring is green.

## Steps / Checklist
- [x] Audit the current create-vs-get seams in Aether, NexusFrameManager, Nexus, and Rift.
- [x] Add or use a strict Aether frame-create path that raises when the frame already exists.
- [x] Remove create-or-recover behavior from the Nexus create path.
- [x] Keep getter paths rooted-conduit-returning and recovery-only.
- [x] Update unit/component/integration tests that currently encode recovery-through-create.
- [x] Update docs/docstrings where the strict contract changed materially.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- strict-create Nexus-managed frame contract
- getter-only recovery contract
- updated focused tests

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/spellbook/spellbook.py
- src/melder/aether/nexus/nexus_frame_manager.py
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/rift/rift.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_nexus_frame_manager.py tests/unit/melder/aether/test_nexus_frame_authoring.py tests/unit/melder/aether/test_nexus.py -k "create_nexus_frame or get_nexus_frame or create_frame_for_rift or _create_frame or shared_mode_exposes_the_same_frame_to_any_rift_while_create_stays_strict" tests/component/melder/aether/test_nexus_frame_authoring_component.py tests/integration/melder/aether/test_nexus_frame_authoring_integration.py`
- Result:
  - `48 passed, 365 deselected, 2 warnings`

## Risks / Rollback Notes
- Risk: shared/indexed mode callers may currently depend on create-or-recover behavior.
  Rollback: move those callers to `get_*` explicitly and keep create strict.
- Risk: Aether strict-create enforcement may collide with Spellbook init if the
  strict helper is wired at the wrong level.
  Rollback: keep `_ensure_frame(...)` as the general attach path and use a new
  explicit strict-create helper only for true creation flows.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-22T11:14:18Z
  TYPE: FACT
  CLAIM: The rooted-creation lane closed with the conduit-returning contract
    landed, but current source and tests still preserve create-or-recover
    behavior. `NexusFrameManager.create_frame_for_rift(...)` returns an
    existing root conduit when the frame already exists, and tests still
    assert repeated `create_nexus_frame()` calls succeed in shared modes.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:453-502
  - src/melder/aether/nexus/nexus.py:2054-2098
  - src/melder/aether/nexus/rift/rift.py:949-981
  - tests/unit/melder/aether/test_nexus.py:4430-4430
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:123-148
  IMPACT: The repo still violates the stricter contract the user wants:
    `create` should raise if the frame already exists, while `get` should be
    the only recovery path.
  NEXT: patch a strict Aether frame-create helper and remove create-or-recover
    behavior from the Nexus create path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T22:31:04Z
  TYPE: MEASURE
  CLAIM: The strict-create correction is landed. Aether now has an explicit
    `_create_frame(...)` helper that raises on duplicates, Nexus-managed create
    paths no longer recover existing frames, getter paths still return rooted
    conduits, and the focused Nexus frame-authoring ring is green.
  EVIDENCE:
  - src/melder/aether/aether.py:429-481
  - src/melder/aether/nexus/nexus_frame_manager.py:37-42
  - src/melder/aether/nexus/nexus_frame_manager.py:454-506
  - src/melder/aether/nexus/nexus_frame_manager.py:983-1010
  - src/melder/aether/nexus/nexus.py:2054-2081
  - src/melder/aether/nexus/rift/rift.py:949-977
  - tests/unit/melder/aether/test_aether.py:254-266
  - tests/unit/melder/aether/test_nexus_frame_manager.py:598-667
  - tests/unit/melder/aether/test_nexus.py:4419-4434
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:310-336
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:163-183
  - codex/context_compass/system_docs/src_architecture.md:323-329
  - codex/context_compass/system_docs/src_components.md:515-518
  IMPACT: The repo now matches the stricter contract you wanted:
    `create_*` raises on existing frames, and `get_*` is the only recovery
    path.
  NEXT: review the strict-create pass and decide whether to accept it or open
    another bounded follow-on seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the strict-create correction for Nexus-managed frame creation.
The runtime, tests, and docs now align on create-only creation and getter-only
recovery.
