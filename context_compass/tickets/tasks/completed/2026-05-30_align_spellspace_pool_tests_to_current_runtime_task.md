# Task: Align spellspace pool tests to current runtime

## Metadata
- Task ID: TASK-2026-05-30-align-spellspace-pool-tests-to-current-runtime
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-30T20:19:43Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Update the direct `SpellSpace` and `SpellSpacePool` unit tests so they match
the current constructor/runtime shape where `SpellSpace` owns its own local
`Creations`, constructs a dedicated `SpellSpaceMeld`, and receives a
`ConduitMeld` plus `ConduitCreations` from the pool.

## Ticket Contract
- ENTRY_GATE: the user provided the failing spellspace-pool test output and
  asked for test repair before widening farther.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py`
  - `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py`
  - directly implicated runtime references only for understanding the current
    constructor/cleanup contract:
    - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
    - `src/melder/aether/conduit/spell_space/spell_space.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-30_move_creation_extract_restore_contract_to_base_task.md`
  - `tickets/tasks/2026-05-30_align_meld_test_surfaces_after_meld_split_task.md`
- EXIT_GATE:
  - the direct `SpellSpace` + `SpellSpacePool` unit files match the current
    runtime shape
  - focused validation is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the failing expectations prove
  a real runtime contradiction instead of stale constructor/ownership drift.

## Scope Boundaries
- In scope:
  - `SpellSpacePool` constructor drift
  - direct `SpellSpace` constructor/ownership/assertion drift
  - focused validation of the direct spellspace unit files
- Out of scope:
  - runtime code changes unless the tests prove a real contradiction
  - broader spellspace or conduit test churn

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to fix the current
  spellspace-pool test drift.

## Steps / Checklist
- [ ] Read the current `SpellSpacePool` and `SpellSpace` constructor/cleanup surfaces.
- [ ] Patch `test_spell_space_pool.py` to the current runtime contract.
- [ ] Run focused validation on the direct spellspace-pool unit file.
- [ ] Summarize the resulting alignment and any remaining drift.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- aligned `SpellSpacePool` unit tests
- aligned `SpellSpace` unit tests
- focused validation result

## Files / Paths Impacted
- `tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py`
- `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Ran:
  - `.venv_new\Scripts\python.exe -m py_compile tests/unit/melder/aether/conduit/spell_space/test_spell_space.py tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py`
  - `.venv_new\Scripts\python.exe -m pytest -q tests/unit/melder/aether/conduit/spell_space/test_spell_space.py tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py`
- Result:
  - `11 passed, 1 warning`

## Risks / Rollback Notes
- Risk: some failing expectations may hide a real runtime mismatch rather than
  simple constructor drift.
- Rollback: keep the patch localized and stop at the first contradiction that
  requires runtime changes.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No runtime edits unless the focused test proves a real contradiction.

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
- Note focus: direct constructor/ownership drift and one-step continuation.
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
- DATETIME: 2026-05-30T20:19:43Z
  TYPE: PLAN
  CLAIM: The failing spellspace-pool tests are still asserting the old pool
    constructor shape (`owner_conduit_id`, `meld`, `creations`) and the old
    spellspace ownership model where the pool injected one reused meld object
    and one shared creations object directly into `SpellSpace`. Current runtime
    now wants `conduit_meld` plus `owner_conduit_creations`, while `SpellSpace`
    builds its own local `Creations` and its own `SpellSpaceMeld`.
  EVIDENCE:
  - user_provided_failure_output
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:14-106
  - src/melder/aether/conduit/spell_space/spell_space.py:18-188
  IMPACT: The next step is a localized test update, not a runtime patch.
  NEXT: patch `test_spell_space_pool.py` to assert the current collaborator and
    cleanup shape, then run the focused file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T21:46:00Z
  TYPE: FACT
  CLAIM: The current `SpellSpacePool` test drift is narrower than a runtime
    bug. `SpellSpace` now constructs a dedicated `SpellSpaceMeld` from the
    incoming conduit meld and immediately passes through the conduit meld's
    spellbook maps and conduit ids. That means the unit stub must supply the
    spellbook map surface `Meld.__init__` reads, and the current test file also
    needs the missing `SimpleNamespace` import to build that stub.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:97-107
  - src/melder/aether/conduit/meld/meld.py:137-146
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py:22-36
  IMPACT: The next step is still a localized test-file repair, not a
    `SpellSpacePool` or `SpellSpace` runtime patch.
  NEXT: patch the direct test file import/stub drift, then rerun the focused
    spellspace-pool unit file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T21:49:00Z
  TYPE: MEASURE
  CLAIM: The first focused validation attempt was not a useful signal for
    `SpellSpacePool`. Running the file through plain `python` hit an unrelated
    interpreter/runtime mismatch first: import-time annotation evaluation in
    `scan.py` raised `NameError: Spellbook is not defined` before the target
    test file loaded. The compile step for the touched unit file itself passed.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py:1-147
  - tests/unit/melder/aether/conduit/conftest.py:6-6
  - src/melder/aether/spellbook/bind/scan.py:220-220
  IMPACT: Focused validation needs to use the repo's `.venv_new` interpreter
    instead of the plain shell `python` path so the test result reflects the
    intended 3.14t runtime surface.
  NEXT: rerun `py_compile` and the focused spellspace-pool pytest file through
    `.venv_new\\Scripts\\python.exe`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T21:50:00Z
  TYPE: MEASURE
  CLAIM: The localized spellspace-pool drift fix is validated. The direct unit
    file now passes under the repo's `.venv_new` interpreter after adding the
    missing `SimpleNamespace` import and keeping the current conduit-meld /
    conduit-creations ownership assertions.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py:1-147
  - codex/context_compass/tickets/tasks/2026-05-30_align_spellspace_pool_tests_to_current_runtime_task.md:65-70
  IMPACT: This lane is now resolved at the focused-file level; no runtime patch
    was needed.
  NEXT: report the bounded test-file alignment and focused validation result to
    the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T21:55:00Z
  TYPE: FACT
  CLAIM: The new failure cluster stays in the same spellspace ownership split.
    `test_spell_space.py` is still building `SpellSpace` and `SpellSpacePool`
    with the pre-split constructor shape (`meld`, `creations`) and therefore
    fails before any behavior assertions run. This is adjacent drift, not new
    contradictory runtime behavior.
  EVIDENCE:
  - user_provided_failure_output_2026_05_30_second_cluster
  - src/melder/aether/conduit/spell_space/spell_space.py:54-67
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:29-42
  IMPACT: The active ticket boundary needs to widen from the pool-only file to
    the direct spellspace unit file in the same subsystem before continued
    implementation.
  NEXT: patch `test_spell_space.py` to the current `SpellSpace` /
    `SpellSpacePool` constructor contract, then rerun the focused spellspace
    unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:00:00Z
  TYPE: FACT
  CLAIM: `SpellSpace.meld(...)` no longer enforces an explicit
    "active spellspace" guard itself. The wrapper delegates straight to the
    owned `SpellSpaceMeld`, while `SpellSpaceScopeError` now belongs deeper in
    creation-context execution paths. The old direct `SpellSpace` unit
    expectation for `SpellSpaceScopeError` is therefore stale.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:182-188
  - src/melder\aether\conduit\meld\creation_context\creation_context.py:305-355
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:175-211
  IMPACT: The direct `SpellSpace` unit file should test wrapper delegation and
    cleanup behavior, not a removed active-scope gate.
  NEXT: rewrite the direct spellspace meld tests around delegation to the owned
    front door and update cleanup assertions to the new local-creations model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:06:00Z
  TYPE: FACT
  CLAIM: The direct `SpellSpace` unit file is now rewritten to the current
    contract. The stubs now model `ConduitMeld` shared-core construction inputs
    plus conduit-owned creations, the dead `SpellSpaceScopeError` expectation is
    removed, `SpellSpace.meld(...)` is tested as a front-door delegator, and
    cleanup assertions now target local-creations clearing, pool reuse, and
    permanent-teardown field deletion.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:1-317
  - src/melder/aether/conduit/spell_space/spell_space.py:54-188
  IMPACT: The remaining step is focused validation of the direct spellspace
    files under the repo interpreter.
  NEXT: run `.venv_new\\Scripts\\python.exe -m py_compile` and the focused
    spellspace pytest ring for `test_spell_space.py` and
    `test_spell_space_pool.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:07:00Z
  TYPE: MEASURE
  CLAIM: The widened direct spellspace test surface is green under the repo
    interpreter. The rewritten `SpellSpace` file plus the already-aligned
    `SpellSpacePool` file passed together after the constructor, delegation,
    cleanup, and reuse expectations were shifted to the current runtime model.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:1-317
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py:1-147
  IMPACT: This lane is now ready for user review; no runtime patch was needed.
  NEXT: report the direct test-file alignment and focused `11 passed` result to
    the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task exists to repair the direct `SpellSpacePool` unit drift after the
spellspace and meld ownership split changed.

