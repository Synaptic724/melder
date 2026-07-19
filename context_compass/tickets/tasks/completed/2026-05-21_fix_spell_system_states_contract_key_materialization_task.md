# Task: fix spell system states contract key materialization

- Completed: 2026-05-22T00:19:54Z
- Summary: Closed during board cleanup after the contract-key materialization slice was accepted and removed from active routing.


## Metadata
- Task ID: TASK-2026-05-21-fix-spell-system-states-contract-key-materialization
- Story: none
- Status: done
- Owner: codex
- Agent Name: refactor_1
- Priority: p2
- Created: 2026-05-21T21:10:11Z
- Updated: 2026-05-22T00:19:54Z

## Objective
Replace the filtered `contract_keys` generator in
`SpellSystemStates.mark_contract_dependents_dirty(...)` with an explicit
realized container so the src-level mypyc checker stops warning without
changing contract-dependent invalidation behavior.

## Ticket Contract
- ENTRY_GATE: active board row points at this task and the warning site plus
  direct `SpellSystemStates` tests are recorded in `## Notes` before code edits.
- EXECUTION_BOUNDARY: only
  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`,
  this task, and the routing row/detail in `attention_board.md`.
- DEPENDENCIES: current src-level mypyc checker output and the focused
  `test_spell_system_states.py` surface covering
  `mark_contract_dependents_dirty(...)`.
- EXIT_GATE: the generator is replaced with explicit realized input, the
  focused checker no longer reports this file, and the direct `SpellSystemStates`
  unit surface stays green.
- FAILURE_ESCALATION: raise `BLOCKER` if the explicit container changes
  contract-key filtering or if the focused checker still reports the warning.

## Scope Boundaries
- In scope:
  - `mark_contract_dependents_dirty(...)` contract-key iteration
  - focused `SpellSystemStates` unit tests
- Out of scope:
  - unrelated `SpellSystemStates` warnings or errors
  - broader control-plane refactors
  - behavior changes in dirty-marking semantics

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the filtered `contract_keys` input is now materialized
  explicitly, the focused checker no longer reports this file, and the direct
  `SpellSystemStates` unit surface is green.

## Steps / Checklist
- [x] Record the warning site and the direct contract tests in notes.
- [x] Replace the filtered generator with an explicit realized container.
- [x] Run focused validation on the warning site.
- [x] Record the validation result in notes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- explicit `contract_keys` materialization in `SpellSystemStates`
- focused validation evidence for the warning outcome

## Files / Paths Impacted
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`
- `codex/context_compass/attention_board.md`
- this task file

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe tests\experimentation\mypyc\mypy_checker_src.py`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_states.py`
- Result:
  - focused checker filter: `NO_MATCH_FOR_spell_system_states.py`
  - pytest: `30 passed, 1 warning`

## Risks / Rollback Notes
- Low risk if the explicit container preserves the same truthy-key filtering.
- Roll back if the focused tests regress or if the checker still reports the
  warning.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-21T21:10:11Z
  TYPE: FACT
  CLAIM: The reported `SpellSystemStates` mypyc warning comes from the filtered
    generator assigned to `key_iter` in `mark_contract_dependents_dirty(...)`:
    `(key for key in contract_keys if key)`. The direct tests only care that
    explicit contract keys mark the matching lineages and that `contract_keys=None`
    fans out across the whole spellbook index.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1202-1208
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py:511-519
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py:574-612
  IMPACT: We can silence the warning by materializing the filtered key container
    explicitly without changing the truthy-key filter or the all-keys path.
  NEXT: replace the generator with an explicit realized container and run the
    src-level checker plus the focused `SpellSystemStates` unit file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T21:12:03Z
  TYPE: MEASURE
  CLAIM: `SpellSystemStates` now materializes the filtered `contract_keys`
    input explicitly before iterating dependents in
    `mark_contract_dependents_dirty(...)`. The focused src-level checker no
    longer reports `spell_system_states.py`, and the direct unit file remains
    green.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1202-1209
  - validation_result: focused checker filter -> `NO_MATCH_FOR_spell_system_states.py`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py` -> `30 passed, 1 warning`
  IMPACT: The warning slice is cleared without changing the explicit-key or
    all-keys invalidation behavior asserted by the direct `SpellSystemStates`
    tests.
  NEXT: wait for user acceptance, then either close this slice or continue to
    the next warning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is a narrow mypyc cleanup slice in `SpellSystemStates`. The only
intended runtime change is explicit materialization of the filtered contract-key
iteration input inside `mark_contract_dependents_dirty(...)`. Focused validation
shows `spell_system_states.py` no longer appears in the checker output, and the
direct unit ring is green.
