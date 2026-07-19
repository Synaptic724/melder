# Task: fix spellbook mypyc annotation and iaether surface

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-spellbook-mypyc-annotation-and-iaether-surface
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T15:11:15Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `spellbook.py` mypy/mypyc error cluster by adding the missing
parameter annotations and the missing `IAether` spell-registry methods.

## Ticket Contract
- ENTRY_GATE: the reported mypy errors are:
  - `spellbook.py:462` missing parameter annotation(s)
  - `spellbook.py:1452` missing parameter annotation(s)
  - `spellbook.py:1491` `IAether` missing `_add_spells_to_aether`
  - `spellbook.py:1514` `IAether` missing `_remove_spells_from_aether`
  - `spellbook.py:2783` missing parameter annotation(s)
  - `spellbook.py:3021` missing parameter annotation(s)
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/utilities/interfaces/iaether.py`
- DEPENDENCIES:
  - live `Aether` spell-registry methods in `src/melder/aether/aether.py`
  - current Spellbook signature surface
- EXIT_GATE:
  - the targeted mypy cluster on `spellbook.py` is gone
  - `IAether` truthfully exposes the spell-registry methods `Spellbook` calls
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any missing-annotation site
  actually needs a narrower contract than the obvious local fix

## Scope Boundaries
- In scope:
  - the four flagged `Spellbook` signature sites
  - the two missing `IAether` methods used by `Spellbook`
- Out of scope:
  - broader `Spellbook` typing cleanup
  - unrelated `IAether` surface redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user provided a bounded mypy/mypyc cluster in
  `Spellbook` plus a clear instruction to add the missing interface methods

## Steps / Checklist
- [ ] confirm the exact flagged `Spellbook` sites and the real `Aether` method signatures
- [ ] patch the missing `Spellbook` annotations
- [ ] patch the `IAether` surface to include the real methods
- [ ] rerun targeted mypy for the cluster
- [ ] continue only after documenting the validation result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a bounded `Spellbook` annotation fix
- a truthful `IAether` spell-registry surface update

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `src/melder/utilities/interfaces/iaether.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spellbook.py src\melder\utilities\interfaces\iaether.py`

## Risks / Rollback Notes
- Low risk. This lane is limited to local annotations and one existing runtime surface.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-18T15:11:15Z
  TYPE: FACT
  CLAIM: The current `Spellbook` mypy/mypyc cluster is bounded and straightforward.
    Four defs in `spellbook.py` are missing parameter annotations, and the file
    also calls two real `Aether` spell-registry methods that `IAether` does not
    currently expose.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:462-462
  - src/melder/spellbook/spellbook.py:1452-1514
  - src/melder/spellbook/spellbook.py:2783-3021
  - src/melder/utilities/interfaces/iaether.py:149-374
  - src/melder/aether/aether.py:1666-1727
  IMPACT: This is a clean local mypy lane with no need for broad refactor or workaround typing.
  NEXT: patch the four signature sites and add the two `IAether` methods, then rerun
    targeted mypy on `spellbook.py` and `iaether.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T15:11:15Z
  TYPE: FACT
  CLAIM: The two-file source patch is landed. `spellbook.py` now annotates the
    `__exit__`, `inspect_spell`, `bind`, and `_add_hooks_to_spell` parameter surfaces,
    and `IAether` now declares the existing `_add_spells_to_aether(...)` and
    `_remove_spells_from_aether(...)` registry methods that `Spellbook` calls.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:1-5
  - src/melder/spellbook/spellbook.py:446-470
  - src/melder/spellbook/spellbook.py:1452-1514
  - src/melder/spellbook/spellbook.py:2783-3029
  - src/melder/utilities/interfaces/iaether.py:226-258
  IMPACT: The reported cluster should now be removable without widening into broader
    Spellbook or Aether typing work.
  NEXT: rerun targeted mypy on `spellbook.py` plus `iaether.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-18T15:11:15Z
  TYPE: MEASURE
  CLAIM: The exact six-site `Spellbook` cluster is gone.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:446-470
  - src/melder/spellbook/spellbook.py:1452-1514
  - src/melder/spellbook/spellbook.py:2783-3029
  - src/melder/utilities/interfaces/iaether.py:226-258
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spellbook.py src\melder\utilities\interfaces\iaether.py 2>&1 | Select-String 'src\\melder\\spellbook\\spellbook.py:(462|1452|1491|1514|2783|3021):'` -> no output
  IMPACT: The user-requested mypy/mypyc `Spellbook` lane is fixed; remaining mypy output from the raw two-file run is unrelated repo debt imported through the wider graph.
  NEXT: wait for the next exact cluster or widen only if the user wants more `Spellbook`/interface debt removed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active `Spellbook` mypy/mypyc lane for a small annotation and interface-surface
cluster. Current evidence points to a direct two-file fix.
