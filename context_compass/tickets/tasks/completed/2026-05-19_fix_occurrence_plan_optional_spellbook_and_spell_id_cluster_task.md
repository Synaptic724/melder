# Task: fix occurrence plan optional spellbook and spell id cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-occurrence-plan-optional-spellbook-and-spell-id-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T11:57:58Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `occurrence_plan.py` mypy cluster by tightening local spell-id,
spellbook, and occurrence-spell optionality without widening support
interfaces.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded `occurrence_plan.py` mypy cluster.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
  - directly implicated support contracts only if required:
    - `src/melder/utilities/interfaces/ispell.py`
    - `src/melder/utilities/interfaces/ispellbook.py`
  - directly implicated tests only for bounded validation:
    - `tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
- DEPENDENCIES:
  - current occurrence-plan contract paths for SpellContract and mutation overrides
  - no casts, no shims, no fake local protocols
- EXIT_GATE:
  - the targeted `occurrence_plan.py` cluster is gone
  - any support-contract changes remain truthful and bounded
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the optionality proves to be
  a real support-contract ambiguity instead of local narrowing debt

## Scope Boundaries
- In scope:
  - local spell-id fallback handling
  - local spellbook/frame-config fail-fast narrowing
  - local occurrence-spell narrowing
  - local total-order sort-key correction for contracted spell candidates
- Out of scope:
  - unrelated blueprint or spell-crafter mypy debt
  - broader spellbook interface redesign beyond directly implicated needs

## Steps / Checklist
- [x] inspect the reported occurrence-plan residuals
- [x] patch the bounded local narrowings first
- [x] rerun targeted mypy on `occurrence_plan.py`
- [x] rerun the bounded occurrence-plan unit ring
- [x] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded occurrence-plan typing fix

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`

## Validation
- Ran:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spell_crafter\blueprints\occurrence_plan.py 2>&1 | Select-String 'src\\melder\\spellbook\\spell_crafter\\blueprints\\occurrence_plan.py:'`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_crafter\blueprints\test_occurrence_plan.py`
- Results:
  - no output
  - `9 passed, 1 warning`

## Risks / Rollback Notes
- Low to medium risk. The cluster was local optionality debt, but the danger
  was changing automatic/dynamic SpellContract provider semantics by accident.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
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
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T11:57:58Z
  TYPE: FACT
  CLAIM: The occurrence-plan cluster was local optionality debt. The main
    issues were nullable `spell_index.current` values being passed directly into
    `MeldExecutionError`, direct use of `_root_spell._spellbook` and
    `_aetheric_frame_configuration` without fail-fast narrowing, a sort key
    that returned `str | None`, and one tail path that used an
    `Optional[ISpell]` occurrence spell without proving it existed first.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1160-1244
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1320-1540
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1746-1773
  IMPACT: No support-interface changes were needed. The right fix was local
    spell-id fallback and fail-fast narrowing at the exact use sites.
  NEXT: record the bounded validation result and keep the lane in review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:57:58Z
  TYPE: MEASURE
  CLAIM: The targeted occurrence-plan cluster is green. `occurrence_plan.py`
    has no file-local mypy output after the local narrowings, and the
    occurrence-plan unit ring passes.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1-1698
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spell_crafter\blueprints\occurrence_plan.py 2>&1 | Select-String 'src\\melder\\spellbook\\spell_crafter\\blueprints\\occurrence_plan.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_crafter\blueprints\test_occurrence_plan.py` -> `9 passed, 1 warning`
  IMPACT: The user-supplied occurrence-plan cluster is fixed without shims or
    interface widening.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Bounded occurrence-plan lane. The fix was fully local: spell-id fallbacks,
spellbook/frame-config fail-fast narrowing, total-order candidate sorting, and
explicit occurrence-spell narrowing.
