# Task: Add Command-Level Spell Query And Snapshot Helpers
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the spell-query and snapshot-helper slice after the shared wrappers landed and the focused validation rings passed.

## Metadata
- Task ID: TASK-2026-04-12-add-command-level-spell-query-and-snapshot-helpers
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-12T22:06:36Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Add shared command-level wrappers for high-value read/query spell and conduit
diagnostic helpers without opening another mutation or creation policy seam.

## Ticket Contract
- ENTRY_GATE: the shared command surface, naming alignment, meld helpers, and
  conduit/runtime introspection slices are already landed and green.
- EXECUTION_BOUNDARY: base command helpers, protocol updates, focused tests,
  and board sync only.
- DEPENDENCIES:
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: the selected read/query helpers exist on `CommandSystem`
  with the same lower-runtime names and the focused unit/runtime ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any helper requires broader
  room/runtime semantics instead of a direct wrapper.

## Scope Boundaries
- In scope:
  - `find_spell_id(...)`
  - `find_spell_key(...)`
  - `get_spell_permissions(...)`
  - `snapshot_state(...)`
  - `get_active_spellspace(...)`
- Out of scope:
  - `create_spellspace(...)`
  - binding/scan helpers
  - mutation-research helpers
  - new static deny policy

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the next low-risk capability/runtime slice after
  the conduit introspection helpers, and it stays fully outside mutation work.

## Steps / Checklist
- [x] Stage the task and route it from the board.
- [x] Add the selected read/query spell helpers to `CommandSystem`.
- [x] Update `ICommandSystem`.
- [x] Add one focused delegation test block.
- [x] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- widened command-level spell query/snapshot surface
- focused unit/runtime coverage

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`
  - `python -m pytest -q tests/integration/melder/aether/rift`

## Risks / Rollback Notes
- Risk: `inspect_spell(...)` and similar helpers would pull arbitrary-object
  semantics into the command surface too early.
  Rollback: keep this slice to the selected direct query/snapshot helpers only.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T22:06:36Z
  TYPE: PLAN
  CLAIM: The next useful non-mutation slice is the read/query spell and
    snapshot helpers that already exist on `Conduit`. These are low semantic
    risk because they are direct lower-runtime queries:
    - `find_spell_id(...)`
    - `find_spell_key(...)`
    - `get_spell_permissions(...)`
    - `snapshot_state(...)`
    - `get_active_spellspace(...)`
    None of them require mutation policy or new static-deny semantics.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:527-558
  - src/melder/aether/conduit/conduit.py:1700-1784
  - src/melder/aether/conduit/conduit.py:2263-2288
  - src/melder/aether/conduit/conduit.py:3855-3891
  IMPACT: We can widen capability’s diagnostic/lookup surface again without
    touching mutation or creation controls.
  NEXT: patch the shared command surface with the selected helpers and prove
    them on the focused unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-12T22:08:38Z
  TYPE: MEASURE
  CLAIM: The read/query spell and snapshot helper slice is green on both the
    focused unit/runtime ring and the shared `rift/` integration folder.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 126 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 210 passed
  IMPACT: Capability gained another low-risk batch of direct query/snapshot
    helpers without destabilizing the existing room/runtime surfaces.
  NEXT: summarize this helper slice and pick the next genuinely new
    capability/runtime seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task adds the next batch of read/query spell and conduit snapshot helpers
to the shared capability command surface. The slice is now landed and green.
