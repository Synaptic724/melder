# Task: Move Creation Extract Restore Contract To Base

## Metadata
- Task ID: TASK-2026-05-30-move-creation-extract-restore-contract-to-base
- Story: none
- Status: done
- Owner: codex
- Agent Name: guard_check_0
- Priority: p0
- Created: 2026-05-30T08:16:46Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Move the generic local creation extract/restore contract into base `Creations`
and keep `ConduitCreations` as the conduit/root specialization layer that only
overrides where conduit-specific behavior is actually needed, then align the
direct unit tests to that split and add explicit `ConduitCreations` coverage.

## Ticket Contract
- ENTRY_GATE: certification is active for `guard_check_0`, the user explicitly
  requested this bounded implementation slice, and the active board routes to
  this ticket before edits begin.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/creations/creations.py`
  - `src/melder/aether/conduit/creations/conduit_creations.py`
  - `tests/unit/melder/aether/conduit/creations/test_creations.py`
  - `tests/unit/melder/aether/conduit/creations/test_conduit_creations.py`
  - `tests/unit/melder/aether/conduit/creations/test_lesser_creations.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-27_investigate_spellspace_owned_creations_and_meld_lane_task.md`
  - current `ConduitCreations` transfer/restore contract
- EXIT_GATE:
  - base `Creations` defines the generic extract/restore contract
  - `ConduitCreations` overrides it intentionally instead of being the only owner
  - direct unit tests are aligned to the new base/subclass contract
  - explicit `ConduitCreations` coverage exists
  - focused validation is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the contract cannot move into
  the base class without widening into runtime rewiring or additional files.

## Scope Boundaries
- In scope:
  - base `Creations` extract/restore contract
  - `ConduitCreations` override shape
  - direct test drift caused by the split
  - focused `ConduitCreations` tests
- Out of scope:
  - runtime caller rewiring
  - spellspace runtime fixes
  - unrelated conduit/meld/runtime tests

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested moving the
  extract/restore contract into the base creations class while keeping conduit
  specialization explicit.

## Steps / Checklist
- [ ] Move generic local extract/restore behavior into base `Creations`.
- [ ] Keep `ConduitCreations` as the explicit conduit/root override layer.
- [ ] Align the old base `Creations` tests to the new base-only contract.
- [ ] Add direct `ConduitCreations` coverage.
- [ ] Run focused validation on the creations test ring.
- [ ] Summarize the resulting contract shape and any remaining runtime drift.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- base `Creations` extract/restore contract
- explicit `ConduitCreations` override surface
- aligned base and subclass unit tests
- focused validation result

## Files / Paths Impacted
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/conduit_creations.py`
- `tests/unit/melder/aether/conduit/creations/test_creations.py`
- `tests/unit/melder/aether/conduit/creations/test_conduit_creations.py`
- `tests/unit/melder/aether/conduit/creations/test_lesser_creations.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/conduit/creations/creations.py src/melder/aether/conduit/creations/conduit_creations.py tests/unit/melder/aether/conduit/creations/test_creations.py tests/unit/melder/aether/conduit/creations/test_conduit_creations.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/creations`

## Risks / Rollback Notes
- Risk: moving the contract into the base class could blur the difference
  between spellspace/common scoped storage and conduit/root specialization if
  the override is not kept explicit.
- Rollback: restore the old base/subclass split inside these two files only.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No drive-by refactors outside the two creations files.
- [ ] No widening into runtime rewiring without an explicit new request.

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
- CLEANUP_TRIGGER: user-directed after review

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-30T08:16:46Z
  TYPE: PLAN
  CLAIM: The user wants a narrow class-contract implementation slice only:
    move the generic extract/restore surface into base `Creations`, keep
    `ConduitCreations` as the explicit conduit/root specialization, and avoid
    widening into runtime rewiring in this pass.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/creations/creations.py:10-251
  - src/melder/aether/conduit/creations/conduit_creations.py:9-142
  IMPACT: The edit can stay constrained to the two creations files while still
    aligning the class hierarchy with the current design direction.
  NEXT: patch `creations.py` and `conduit_creations.py` so the base class owns
    the generic extract/restore contract and the subclass overrides it
    explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T08:16:46Z
  TYPE: FACT
  CLAIM: The generic local extract/restore contract now lives on base
    `Creations`, and `ConduitCreations` keeps explicit conduit/root override
    methods that currently delegate to the base behavior. The subclass is no
    longer the only owner of that storage-move logic.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:149-281
  - src/melder/aether/conduit/creations/conduit_creations.py:48-68
  - src/melder/aether/conduit/creations/conduit_creations.py:70-87
  IMPACT: The class hierarchy now matches the intended model better: base
    scoped storage defines the common move surface, while conduit/root-specific
    behavior still has an explicit override seam.
  NEXT: run narrow syntax validation on the two touched files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T08:19:01Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed for the two touched creations files.
    `python -m py_compile src/melder/aether/conduit/creations/creations.py
    src/melder/aether/conduit/creations/conduit_creations.py` completed
    successfully.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:149-281
  - src/melder/aether/conduit/creations/conduit_creations.py:48-87
  IMPACT: The class-contract change parses cleanly. Runtime and test rewiring
    remain out of scope for this slice.
  NEXT: summarize the resulting base/subclass contract and the remaining
    runtime drift outside these two files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-30T19:48:28Z
  TYPE: FACT
  CLAIM: The next drift is entirely on the test side. The old
    `test_creations.py` still builds base `Creations` with the retired
    `(conduit_id, spellspace_stack)` constructor and still asserts the removed
    spellspace-specific surface (`register_spellspace_creation(...)`,
    `get_spellspace_creation(...)`, `clear_spellspace_instances(...)`) on the
    base class. Under the new split, base `Creations` is scoped singleton/many
    storage only, while conduit/root behavior lives on `ConduitCreations`.
    There is no current `test_conduit_creations.py`, and the small legacy
    `test_lesser_creations.py` is also pinned to the old base constructor.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:10-366
  - src/melder/aether/conduit/creations/conduit_creations.py:9-60
  - tests/unit/melder/aether/conduit/creations/test_creations.py:1-493
  - tests/unit/melder/aether/conduit/creations/test_lesser_creations.py:1-70
  IMPACT: The clean fix is to keep base tests on base-only behavior, move
    conduit/root-specific coverage into a new `test_conduit_creations.py`, and
    retire or repurpose the legacy lesser-creations test file.
  NEXT: patch the base test file to the new constructor/behavior contract, add
    the dedicated `ConduitCreations` test file, and remove or rewrite the
    legacy lesser-creations drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T19:51:51Z
  TYPE: FACT
  CLAIM: The direct creations test split is now landed. Base
    `test_creations.py` now covers only the real base contract:
    - scoped singleton/many storage
    - extract/restore for `unique` and `many`
    - `clear_all()` / `reset_for_pool()`
    - cleanup/disposal behavior
    The spellspace-only assertions are gone from the base file. A new
    `test_conduit_creations.py` now covers the subclass seam directly:
    - conduit id used as both owner and scope id
    - inherited extract/restore behavior
    - no old spellspace bucket API on the subclass
    The old `test_lesser_creations.py` is reduced back to the legacy removed
    module assertion it still meaningfully owns.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/creations/test_creations.py:1-378
  - tests/unit/melder/aether/conduit/creations/test_conduit_creations.py:1-88
  - tests/unit/melder/aether/conduit/creations/test_lesser_creations.py:1-15
  IMPACT: The unit surface now matches the actual class split instead of
    pretending the base class still owns spellspace behavior.
  NEXT: run focused validation on the creations test directory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T19:51:51Z
  TYPE: MEASURE
  CLAIM: The focused creations unit ring is green after the test split.
    `py_compile` passed for the three touched test files, and
    `tests/unit/melder/aether/conduit/creations` now passes
    `25 passed, 1 warning`.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile tests\unit\melder\aether\conduit\creations\test_creations.py tests\unit\melder\aether\conduit\creations\test_conduit_creations.py tests\unit\melder\aether\conduit\creations\test_lesser_creations.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\creations`
  IMPACT: The direct drift from the base/subclass split is repaired, and the
    new `ConduitCreations` seam has explicit unit coverage.
  NEXT: report the focused fix and validation result to the user, then wait
    for the next seam or a wider validation request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to move the generic local extract/restore contract into base
`Creations` while keeping `ConduitCreations` as the explicit conduit/root
specialization layer. Runtime rewiring remains out of scope, but direct unit
test alignment is now part of the accepted slice.

