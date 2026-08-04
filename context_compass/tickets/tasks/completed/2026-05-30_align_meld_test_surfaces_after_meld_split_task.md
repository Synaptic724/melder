# Task: Align meld test surfaces after Meld split

## Metadata
- Task ID: TASK-2026-05-30-align-meld-test-surfaces-after-meld-split
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-30T19:56:01Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Read the current `Meld`, `ConduitMeld`, and `SpellSpaceMeld` surfaces, then
repair the direct meld unit drift so tests match the current class split and
creations ownership model.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a meld-focused read plus direct
  test repair after the meld surface changed.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/meld/conduit_meld.py`
  - `src/melder/aether/conduit/meld/spellspace_meld.py`
  - directly implicated meld tests:
    - `tests/unit/melder/aether/conduit/meld/test_meld.py`
    - `tests/unit/melder/aether/conduit/meld/test_meld_2.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-30_move_creation_extract_restore_contract_to_base_task.md`
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
- EXIT_GATE:
  - direct meld tests are aligned to the current abstract/base and subclass split
  - creations constructor drift is removed from the meld tests
  - focused meld validation is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if truthful repair requires
  runtime changes instead of test-side alignment.

## Scope Boundaries
- In scope:
  - direct meld test drift from abstract `Meld`
  - direct meld test drift from `ConduitCreations` / `SpellSpace` split
  - focused unit validation for the meld test surfaces
- Out of scope:
  - runtime redesign of meld behavior
  - broad conduit/runtime rewrites
  - unrelated creations tests outside the meld ring

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked for a meld-surface reread and
  test repair before anything else.

## Steps / Checklist
- [ ] Read `meld.py`, `conduit_meld.py`, and `spellspace_meld.py`.
- [ ] Read the directly failing meld test helpers and assertion surfaces.
- [ ] Align tests to the current base/subclass split and creations ownership.
- [ ] Run focused meld validation.
- [ ] Summarize the drift and any remaining runtime contradictions.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- aligned meld unit tests
- explicit test coverage for current meld class boundaries
- focused validation result

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/conduit_meld.py`
- `src/melder/aether/conduit/meld/spellspace_meld.py`
- `tests/unit/melder/aether/conduit/meld/test_meld.py`
- `tests/unit/melder/aether/conduit/meld/test_meld_2.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/test_meld_2.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld`

## Risks / Rollback Notes
- Risk: some failures may prove the runtime class split is still half-migrated.
- Rollback: stop at the first real runtime contradiction instead of massaging
  tests around broken behavior.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No runtime edits unless the tests prove a real runtime contradiction.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: direct meld drift, current class boundaries, and one-step continuation.
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
- DATETIME: 2026-05-30T19:56:01Z
  TYPE: PLAN
  CLAIM: The pasted failures already show two concrete drift classes:
    - tests still instantiate abstract `Meld` directly
    - tests still build the old spellspace-aware `Creations` shape
    The right cut is to read the current meld class split first, then align the
    direct test helpers and assertions to that runtime boundary instead of
    guessing from the failures alone.
  EVIDENCE:
  - user_provided_failure_output
  - src/melder/aether/conduit/meld/meld.py
  - src/melder/aether/conduit/meld/conduit_meld.py
  - src/melder/aether/conduit/meld/spellspace_meld.py
  IMPACT: The next step is class-boundary reread plus focused test repair, not
    runtime edits.
  NEXT: read the three meld files and the direct test helpers, then record the
    first exact mismatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T19:56:01Z
  TYPE: FACT
  CLAIM: The first exact mismatch is now explicit. `Meld` is abstract in
    current source and only owns shared lookup/validation/compiler helpers.
    `ConduitMeld` is the concrete conduit-facing front door and owns
    `ConduitCreations`; `SpellSpaceMeld` is the concrete spellspace-facing
    front door and owns both spellspace-local `Creations` and the owner
    conduit's `ConduitCreations`. The old tests are still built around one
    concrete `Meld(creations=..., spellbook=...)` helper plus one old
    spellspace-aware `Creations(conduit_id=..., spellspace_stack=...)`
    helper. That means the drift is not just constructor signatures. Some tests
    are exercising spellspace behavior through the wrong concrete meld class.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:42-215
  - src/melder/aether/conduit/meld/conduit_meld.py:13-62
  - src/melder/aether/conduit/meld/conduit_meld.py:248-440
  - src/melder/aether/conduit/meld/spellspace_meld.py:15-93
  - src/melder/aether/conduit/meld/spellspace_meld.py:269-459
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1-24
  - tests/unit/melder/aether/conduit/meld/test_meld.py:708-759
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:1-18
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:181-213
  IMPACT: The fix should be helper-first:
    - default meld helpers instantiate `ConduitMeld`
    - spellspace-specific behavior gets explicit `SpellSpaceMeld` helpers
    - old spellspace registration assertions that belonged to removed
      creations APIs should be deleted or rewritten
  NEXT: patch the helper layer in the two meld test files before touching
    individual assertions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T20:07:29Z
  TYPE: FACT
  CLAIM: The test repair stayed helper-first exactly as planned. The direct
    changes were:
    - `test_meld.py` and `test_meld_2.py` now build `ConduitMeld` instead of
      abstract `Meld`
    - conduit-facing creations helpers now build `ConduitCreations`
    - `SpellSpaceMeld` now has an explicit helper in `test_meld.py` for the
      spellspace-local behavior that no longer belongs on the conduit-facing
      meld tests
    - the spell stub now carries `requires_spellspace_request`
    - old spellspace-registration assertions that depended on removed
      spellspace APIs on conduit-owned creations were rewritten or removed
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1-24
  - tests/unit/melder/aether/conduit/meld/test_meld.py:308-324
  - tests/unit/melder/aether/conduit/meld/test_meld.py:708-807
  - tests/unit/melder/aether/conduit/meld/test_meld.py:2340-2568
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:1-18
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:97-105
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:181-218
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:553-609
  IMPACT: The meld tests now match the actual runtime boundary instead of
    pretending the old monolithic `Meld` / spellspace-aware `Creations`
    pairing still exists.
  NEXT: run the full focused meld unit directory and confirm there are no
    remaining runtime contradictions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T20:07:29Z
  TYPE: MEASURE
  CLAIM: The focused meld unit directory is green after the helper/class-boundary
    split. `py_compile` passed for the two touched test files, and
    `tests/unit/melder/aether/conduit/meld` now passes `437 passed, 1 warning`.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile tests\unit\melder\aether\conduit\meld\test_meld.py tests\unit\melder\aether\conduit\meld\test_meld_2.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld`
  IMPACT: The current meld class split is test-aligned on the focused unit
    surface, and no runtime changes were needed for this repair.
  NEXT: report the focused fix to the user and wait for the next seam or a
    broader validation request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T20:11:38Z
  TYPE: DECISION
  CLAIM: The user wants deeper direct coverage for the two concrete meld
    subclasses, not just repaired drift. The next slice should add one small
    shared support module plus dedicated `ConduitMeld` and `SpellSpaceMeld`
    test files so each concrete class has its own explicit contract ring
    instead of relying on generic `Meld`-era tests to imply the subclass
    behavior.
  EVIDENCE:
  - user_instruction
  - tests/unit/melder/aether/conduit/meld/test_meld.py:2345-2568
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:553-609
  IMPACT: The next implementation step is additive direct subclass coverage,
    not more runtime edits.
  NEXT: add shared subclass-test helpers, then add dedicated
    `test_conduit_meld.py` and `test_spellspace_meld.py` with explicit
    subclass cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T20:16:03Z
  TYPE: FACT
  CLAIM: The new direct subclass coverage surfaced one real runtime
    inconsistency in `ConduitMeld.meld()`. The conduit-facing front door is
    supposed to reject `requires_spellspace_request` spells, but the current
    check only runs inside the non-string / logical-resolution branch. When the
    caller passes a direct spell-id string, `ConduitMeld.meld()` resolves the
    spell through `_resolve_spell_by_id(...)` and then proceeds into
    creation-context build without ever applying the spellspace-request guard.
    That is inconsistent with the non-string branch and with the existing
    conduit-facing no-create probes.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:122-169
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:344-354
  IMPACT: This one direct subclass test should stay as a real contract test.
    The fix belongs in runtime, not in test relaxation.
  NEXT: patch `ConduitMeld.meld()` so the spellspace-request guard runs after
    target spell resolution for both string and non-string entry paths, then
    rerun the focused meld directory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T20:17:12Z
  TYPE: FACT
  CLAIM: The direct subclass coverage is now additive and explicit. A new
    `test_concrete_meld_subclasses.py` file carries:
    - `15` direct `ConduitMeld` tests
    - `16` direct `SpellSpaceMeld` tests
    The file covers init/cleanup, concrete storage routing, hooks vs no-hooks
    paths, existing-object retrieval, live-creation probes, and structured
    status payloads for both subclasses. The only runtime code change needed to
    make that coverage truthful was a one-line guard move in
    `ConduitMeld.meld()` so direct spell-id calls reject spellspace-request
    spells the same way logical-resolution calls already did.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:263-831
  - src/melder/aether/conduit/meld/conduit_meld.py:122-172
  IMPACT: The meld surface now has explicit subclass contract coverage instead
    of relying mostly on old generic `Meld`-era tests to imply concrete
    behavior.
  NEXT: keep this file as the direct subclass ring and use the existing
    generic files for shared inherited logic only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T20:17:12Z
  TYPE: MEASURE
  CLAIM: The full focused meld unit directory is green after the subclass
    coverage expansion and the small conduit-facing runtime fix.
    Current result: `468 passed, 1 warning`.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\conduit\meld\conduit_meld.py tests\unit\melder\aether\conduit\meld\test_concrete_meld_subclasses.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld`
  IMPACT: The direct meld drift is repaired, the new concrete subclass ring is
    in place, and the current meld unit surface is stable again.
  NEXT: report the new direct subclass coverage counts and the focused green
    ring to the user, then wait for the next seam or a broader validation ask.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to align the direct meld test surface after the meld and
creations class splits changed.

