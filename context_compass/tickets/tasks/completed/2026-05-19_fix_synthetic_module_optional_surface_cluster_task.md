# Task: fix synthetic module optional surface cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-synthetic-module-optional-surface-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T12:47:45Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `synthetic_module.py` mypy cluster by proving whether the
reported `Optional[str]` / `Optional[list[str]]` flows are local narrowing debt
or stale public typing contracts.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded `synthetic_module.py` mypy cluster
  and selected it as the next lane.
- EXECUTION_BOUNDARY:
  - `src/melder/crystallizer/synthetic_module.py`
  - directly implicated support contracts only if required by evidence
  - bounded validation tests only if the file change needs them
- DEPENDENCIES:
  - current `SyntheticModule` runtime contract
  - no shims, no fake surfaces, no compatibility hacks
  - raise to Mark directly if the contract becomes ambiguous or I get stuck
- EXIT_GATE:
  - the targeted `synthetic_module.py` cluster is gone
  - any support-contract changes remain truthful and bounded
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the file proves to depend on
  a public contract that is materially ambiguous instead of just locally loose
  typing

## Scope Boundaries
- In scope:
  - local `str | None` return narrowing
  - local `list[str] | None` list materialization narrowing
  - local exec/register callsite narrowing
  - support interface/protocol truth only if the public contract is actually
    stale
- Out of scope:
  - broader crystallizer redesign
  - unrelated crystallizer/runtime mypy debt

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user selected this exact bounded mypy cluster as the
  next active lane.

## Steps / Checklist
- [ ] read `synthetic_module.py` in bounded chunks
- [ ] inspect directly implicated support contracts before changing types
- [ ] patch local narrowings first if the contract already tells the truth
- [ ] upgrade public contracts only if source evidence proves they are stale
- [ ] rerun targeted mypy on `synthetic_module.py`
- [ ] rerun bounded tests if the patch changes runtime behavior or if the file
      has a direct focused unit ring
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded `synthetic_module.py` typing fix

## Files / Paths Impacted
- `src/melder/crystallizer/synthetic_module.py`
- only if required by truthful fix:
  - directly implicated support interfaces/contracts under `src/melder/utilities/interfaces/`
  - directly implicated crystallizer support files

## Validation
- Ran:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\crystallizer\synthetic_module.py 2>&1 | Select-String 'src\\melder\\crystallizer\\synthetic_module.py:'`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\crystallizer\test_synthetic_module.py`
- Results:
  - no output for `synthetic_module.py`
  - `80 passed, 1 warning`

## Risks / Rollback Notes
- Medium risk. The user-reported lines look mostly like local optionality, but
  the `get_or_create` return path and parent-package registration path may
  expose a stale public contract.

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
- DATETIME: 2026-05-19T12:47:45Z
  TYPE: FACT
  CLAIM: The user selected the `synthetic_module.py` cluster as the next active
    lane. The file is large enough to require chunked reading, and the error
    shape currently looks like a mix of local `Optional[str]`,
    `Optional[list[str]]`, and one possibly stale constructor/return contract
    around synthetic-module registration.
  EVIDENCE:
  - user_error_report: `src/melder/crystallizer/synthetic_module.py:385-463`
  - user_error_report: `src/melder/crystallizer/synthetic_module.py:721-1304`
  IMPACT: The next safe step is bounded source reading plus directly implicated
    contract review before any patching.
  NEXT: read `synthetic_module.py` in explicit chunks and inspect the directly
    implicated contract files it imports.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:47:45Z
  TYPE: FACT
  CLAIM: The required identity/source/list fields in `SyntheticModule` look
    like stale optional typing, not real runtime optionality. The constructor
    enforces non-empty values for `_spell_crystal_id`, `_source_text`,
    `_source_sha256`, and `_binding_signature`, and initializes the three name
    collections as concrete lists. The remaining surfaced errors then collapse
    to two local importlib proofs: `reload_via_importlib(...)` returning a
    concrete `SyntheticModule`, and package metadata paths that read
    `module.__file__` through `ModuleType`.
  EVIDENCE:
  - src/melder/crystallizer/synthetic_module.py:211-249
  - src/melder/crystallizer/synthetic_module.py:252-267
  - src/melder/crystallizer/synthetic_module.py:385-463
  - src/melder/crystallizer/synthetic_module.py:721-721
  - src/melder/crystallizer/synthetic_module.py:791-791
  - src/melder/crystallizer/synthetic_module.py:858-886
  - src/melder/crystallizer/synthetic_module.py:1126-1151
  - src/melder/crystallizer/synthetic_module.py:1298-1304
  - src/melder/utilities/interfaces/isyntheticmodule.py:18-24
  IMPACT: The first patch should tighten the public `ISyntheticModule`
    contract and matching concrete field annotations, then add small fail-fast
    local proofs around importlib return/path handling.
  NEXT: patch `isyntheticmodule.py` and `synthetic_module.py`, then rerun
    targeted mypy and the bounded synthetic-module unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:47:45Z
  TYPE: PLAN
  CLAIM: The bounded implementation pass will stay behavior-preserving. I will
    tighten the `ISyntheticModule` and concrete field annotations for the
    required identity/source/list fields, then add small fail-fast local proofs
    around the importlib reload return and `__file__`-backed package metadata
    paths instead of changing how synthetic modules load, publish, or execute.
  EVIDENCE:
  - src/melder/crystallizer/synthetic_module.py:252-267
  - src/melder/crystallizer/synthetic_module.py:721-721
  - src/melder/crystallizer/synthetic_module.py:858-886
  - src/melder/crystallizer/synthetic_module.py:1120-1151
  - src/melder/utilities/interfaces/isyntheticmodule.py:18-24
  IMPACT: This keeps the in-memory importlib module behavior intact while still
    shaving down the current file-local mypy cluster.
  NEXT: patch the interface and concrete file, then run targeted mypy and the
    synthetic-module unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:47:45Z
  TYPE: MEASURE
  CLAIM: The targeted `synthetic_module.py` cluster is green. The required
    identity/source/list fields were tightened to the real live-module
    contract, the importlib reload path now proves the returned object is still
    a `SyntheticModule`, and the `__file__`-backed package metadata paths are
    fail-fast narrowed without changing how modules register, publish, or
    execute. The direct synthetic-module unit ring still passes.
  EVIDENCE:
  - src/melder/utilities/interfaces/isyntheticmodule.py:18-24
  - src/melder/crystallizer/synthetic_module.py:252-267
  - src/melder/crystallizer/synthetic_module.py:858-886
  - src/melder/crystallizer/synthetic_module.py:1118-1151
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\crystallizer\synthetic_module.py 2>&1 | Select-String 'src\\melder\\crystallizer\\synthetic_module.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\crystallizer\test_synthetic_module.py` -> `80 passed, 1 warning`
  IMPACT: The user-supplied `synthetic_module.py` line-item cluster is fixed
    without changing the in-memory importlib module behavior, and the broader
    repo mypy debt can stay deferred.
  NEXT: report the bounded fix and wait for the next bucket instead of widening
    into the unrelated imported-file errors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded `synthetic_module.py` lane. Start with chunked file reads and
direct contract inspection, then decide local narrowing versus interface truth.
