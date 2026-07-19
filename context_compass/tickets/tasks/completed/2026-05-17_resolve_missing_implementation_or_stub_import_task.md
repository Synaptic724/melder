# Task: resolve missing implementation or stub import
- Completed: 2026-05-17T16:50:29Z
- Summary: Closed after the dead optional `melder_native_fast_dispatch` seam
  was removed from the Phase 12 no-overrides executor, the focused executor
  test ring stayed green, and the task-specific import-not-found text
  disappeared from the narrow mypy probe.

## Metadata
- Task ID: TASK-2026-05-17-resolve-missing-implementation-or-stub-import
- Story: none
- Status: done
- Owner: mypy_1
- Agent Name: mypy_1
- Priority: p1
- Created: 2026-05-17T16:03:44Z
- Updated: 2026-05-17T16:50:29Z

## Objective
Resolve the single missing implementation/stub import item cleanly. If the
missing module is dead optimization plumbing rather than a real dependency,
remove the seam instead of stubbing or excluding it.

## Ticket Contract
- ENTRY_GATE: epic `EPIC-2026-05-17-execute-first-mypyc-typing-cleanup-tranche`
  is active and this task is selected as the first work item
- EXECUTION_BOUNDARY: only the missing-module/import-not-found lane
- DEPENDENCIES: `Experiments/00_TOC.md`, `Experiments/07_fix_order.md`, and the
  concrete error site for `melder_native_fast_dispatch`
- EXIT_GATE: one explicit target-boundary decision is implemented, the dead
  seam is removed if that is the right answer, and the corresponding backlog
  line is removed from the experiment markdown
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the correct answer is neither
  remove, stub, generated module, nor target exclusion

## Scope Boundaries
- In scope:
  - the single missing implementation or stub import item
- Out of scope:
  - the broader undefined-name/import tranche

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user accepted the seam removal and asked to continue
  through the tickets, so task 1 is closed and handed off

## Steps / Checklist
- [x] inspect the missing import site and determine whether it is optional,
      generated, native-only, or missing by mistake
- [x] choose the repo-compatible resolution: remove the dead seam instead of
      stubbing, generating, or excluding it
- [x] remove the resolved backlog line from the experiment markdown
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- dead optional native-dispatch seam removed from the no-overrides executor
- focused Phase 12 tests updated to the direct-call-only runtime model

## Files / Paths Impacted
- `Experiments/02_signature_and_annotation_errors.md`
- `Experiments/07_fix_order.md`
- runtime/stub/packaging files as determined by investigation

## Validation
- Ran: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_crafter\\blueprints\\test_phase12_no_overrides_executor.py`
- Result: `36 passed, 1 warning`
- Ran: `.\\.venv_new\\Scripts\\python.exe -m mypy src\\melder\\spellbook\\spell_crafter\\blueprints\\phase12_no_overrides_executor.py`
- Result: no remaining `melder_native_fast_dispatch` / `import-not-found`
  output; unrelated existing type errors in other files still remain
- Warnings:
  - pytest cache warning because `.pytest_cache` path creation was already in a
    conflicting filesystem state

## Risks / Rollback Notes
- Removing a seam that still carried runtime value would be a behavior change,
  so the justification must stay tied to the generated direct-call path and the
  current missing-module state.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-05-17T16:03:44Z
  TYPE: PLAN
  CLAIM: This task is the first fix-order item because unresolved missing
    modules can poison downstream name/type resolution and make later counts
    noisy.
  EVIDENCE:
  - Experiments/00_TOC.md:91-91
  - Experiments/07_fix_order.md:59-59
  IMPACT: This should be resolved before the broader undefined-name tranche.
  NEXT: inspect the concrete import-not-found site and choose generate vs stub
    vs exclusion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:16:00Z
  TYPE: FACT
  CLAIM: The missing module is an optional external native dispatcher seam, not
    an intended in-repo Python implementation. The runtime path already catches
    `ImportError`, gates native use behind
    `MELDER_ENABLE_NATIVE_TRANSIENT_DISPATCH`, and falls back to direct Python
    invocation when the native module is absent.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:55-89
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py:287-324
  - pyproject.toml:1-54
  IMPACT: The narrow repo-compatible fix path is a typed stub for
    `melder_native_fast_dispatch`, not a fake Python runtime module and not a
    mypyc-target exclusion.
  NEXT: add a top-level stub for `melder_native_fast_dispatch` with the real
    dispatcher signature and then remove the solved backlog line from the live
    experiments markdown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T16:22:00Z
  TYPE: CONFLICT
  CLAIM: The currently available `.venv_new` environment still does not expose
    `melder_native_fast_dispatch` on normal import resolution. A direct
    `.venv_new\\Scripts\\python.exe -c "import melder_native_fast_dispatch"`
    probe raises `ModuleNotFoundError`, and a filesystem search under `.venv`
    and `.venv_new` does not show a matching module artifact.
  EVIDENCE:
  - validation_probe: `.\\.venv_new\\Scripts\\python.exe -c "import melder_native_fast_dispatch, sys; print(melder_native_fast_dispatch.__file__)"`
  - filesystem_probe: recursive search under `.venv` and `.venv_new` for
    `melder_native_fast_dispatch*`
  IMPACT: "Use `.venv_new`" alone is not sufficient to settle task 1. The real
    remaining question is whether the native module needs an extra bootstrap
    path/env var or whether the stub path should stand.
  NEXT: inspect `.venv_new` path/bootstrap state and ask for the exact env
    bootstrap command if the module still does not appear.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T16:29:37Z
  TYPE: DECISION
  CLAIM: The missing import item is resolved by deleting the dead optional
    native transient-dispatch seam, not by stubbing it. The executor already
    codegens the direct transient call shape inside Phase 12, so the extra
    `melder_native_fast_dispatch` optimization layer was redundant and missing
    from the active env.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1-101
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1399-1557
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py:270-303
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_crafter\\blueprints\\test_phase12_no_overrides_executor.py` -> `36 passed, 1 warning`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m mypy src\\melder\\spellbook\\spell_crafter\\blueprints\\phase12_no_overrides_executor.py` -> no `melder_native_fast_dispatch` / `import-not-found` output
  IMPACT: Task 1 no longer blocks the tranche. The import-not-found item is
    resolved without inventing a fake runtime module or carrying dead
    optimization plumbing forward.
  NEXT: review this removal, then either close task 1 or route the tranche to
    the next ready item.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-17T16:50:29Z
  TYPE: DECISION
  CLAIM: The user accepted the dead-seam removal and asked to continue through
    the tickets, so task 1 is complete. The tranche can now move to the next
    ready item without carrying this optional native-dispatch boundary forward.
  EVIDENCE:
  - user_instruction: "great continue going through tickets please"
  IMPACT: The task can move to `completed`, the active board row can be
    removed, and the epic can mark item 1 complete while the queue advances.
  NEXT: move the task to `tickets/tasks/completed/` and route the next ready
    mypy tranche item.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Task 1 is implemented and ready for review. The dead optional native transient
dispatcher seam was removed from the Phase 12 no-overrides executor, the
focused executor tests were updated to the direct-call-only model, and the
task-specific `import-not-found` text no longer appears in the narrow mypy
probe for this file.
