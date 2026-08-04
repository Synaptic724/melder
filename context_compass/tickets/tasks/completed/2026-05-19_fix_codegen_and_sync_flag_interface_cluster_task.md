# Task: fix codegen and sync flag interface cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-codegen-and-sync-flag-interface-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T15:35:00Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current bounded mypy cluster spanning
`creation_context_codegen.py`, `ticket_flag.py`, `fast_switch.py`, and
`ispellspace.py` while keeping public contracts truthful and avoiding
unrelated synchronization or codegen redesign.

## Ticket Contract
- ENTRY_GATE: the user supplied this exact bounded cluster.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - `src/melder/utilities/synchronization/ticket_flag.py`
  - `src/melder/utilities/synchronization/fast_switch.py`
  - `src/melder/utilities/interfaces/ispellspace.py`
  - directly implicated support interfaces only if the source proves they are stale
- DEPENDENCIES:
  - current creation-context codegen compile contract
  - current ticket/switch synchronization cleanup and context-manager contracts
  - no shims, no fake surfaces, no unrelated redesign
  - raise to Mark directly if the contract becomes ambiguous
- EXIT_GATE:
  - the targeted reported errors in these files are gone
  - any public interface changes remain truthful and bounded
  - focused validation confirms the lane
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the lane requires a broader
  synchronization or codegen API redesign instead of local typing cleanup

## Scope Boundaries
- In scope:
  - local return typing cleanup in creation-context codegen compile helpers
  - local optionality/annotation cleanup in ticket/switch synchronization helpers
  - truthful import/interface fixes if the source proves stale contract drift
- Out of scope:
  - unrelated repo-wide mypy debt
  - broad synchronization primitive redesign
  - broader Phase 12 runtime redesign

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user selected this exact codegen/sync/interface
  cluster as the next active lane.

## Steps / Checklist
- [x] read the exact failing slices in the reported files
- [x] classify local typing debt versus stale public contract drift
- [x] patch the bounded file/interface fixes
- [x] rerun focused mypy on the reported files
- [x] rerun directly implicated unit tests when behavior-sensitive files move
- [x] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded codegen/sync/interface typing fix

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- `src/melder/utilities/synchronization/ticket_flag.py`
- `src/melder/utilities/synchronization/fast_switch.py`
- `src/melder/utilities/interfaces/ispellspace.py`
- only if required by the truthful fix:
  - directly implicated support interfaces

## Validation
- `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\meld\creation_context\creation_context_codegen.py src\melder\utilities\synchronization\ticket_flag.py src\melder\utilities\synchronization\fast_switch.py src\melder\utilities\interfaces\ispellspace.py src\melder\utilities\interfaces\iconduit.py 2>&1 | Select-String 'src\\melder\\aether\\conduit\\meld\\creation_context\\creation_context_codegen.py:|src\\melder\\utilities\\synchronization\\ticket_flag.py:|src\\melder\\utilities\\synchronization\\fast_switch.py:|src\\melder\\utilities\\interfaces\\ispellspace.py:|src\\melder\\utilities\\interfaces\\iconduit.py:'`
  - no matching file-local mypy errors
- `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\synchronization\test_ticket_flag.py tests\unit\melder\utilities\synchronization\test_fast_switch.py tests\unit\melder\utilities\interfaces\test_interface_inheritance.py`
  - `55 passed, 1 warning`

## Risks / Rollback Notes
- Low to medium risk. This looks mostly local, but the codegen compile helpers
  may hide one broad return-typing seam if their generated callable surface is
  not typed consistently.

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
- DATETIME: 2026-05-19T15:35:00Z
  TYPE: FACT
  CLAIM: The next active lane is the bounded codegen/sync/interface cluster
    covering `creation_context_codegen.py`, `ticket_flag.py`, `fast_switch.py`,
    and `ispellspace.py`. The first step is exact slice reads because the
    report mixes no-any-return codegen helpers, optional deque cleanup/state
    issues, context-manager annotation drift, and one missing interface import.
  EVIDENCE:
  - user_error_report: `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - user_error_report: `src/melder/utilities/synchronization/ticket_flag.py`
  - user_error_report: `src/melder/utilities/synchronization/fast_switch.py`
  - user_error_report: `src/melder/utilities/interfaces/ispellspace.py`
  IMPACT: This should stay bounded if the source confirms mostly local typing
    debt instead of wider primitive or codegen contract drift.
  NEXT: read the exact failing slices in the reported files and classify local
    residue versus real contract drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T15:33:53Z
  TYPE: FACT
  CLAIM: The focused mypy run is narrower than the pasted report.
    `creation_context_codegen.py` is already clean in the bounded slice, and
    the live residue is only one missing `IConduit` import in `ispellspace.py`
    plus local optional-deque/context-manager typing in `ticket_flag.py` and
    `fast_switch.py`. The existing unit tests confirm the cleanup contract:
    `TicketFlag` must leave `_tickets is None` but all public operations fail
    through `check_cleaned()`, while `FastSwitch` intentionally becomes a
    broken primitive after cleanup and `len(switch)` raising `TypeError` is
    already the expected behavior.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellspace.py:1-41
  - src/melder/utilities/synchronization/ticket_flag.py:1-219
  - src/melder/utilities/synchronization/fast_switch.py:1-146
  - tests/unit/melder/utilities/synchronization/test_ticket_flag.py:96-177
  - tests/unit/melder/utilities/synchronization/test_fast_switch.py:59-78
  IMPACT: This lane is a local cleanup pass, not a broader codegen or sync redesign.
  NEXT: patch the missing import, add local deque narrowing that preserves the
    tested cleanup semantics, and rerun the focused mypy and unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T15:35:45Z
  TYPE: FACT
  CLAIM: The direct `IConduit` import in `ispellspace.py` is truthful for
    mypy, but it exposes a runtime interface cycle because `iconduit.py` still
    imports `ISpellSpace` during module import. The narrow truthful fix is to
    make `iconduit.py` stop requiring `ISpellSpace` at class-definition time
    instead of weakening `ISpellSpace` back to `Any` or an invented shim.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellspace.py:1-41
  - src/melder/utilities/interfaces/iconduit.py:1-16
  - src/melder/utilities/interfaces/iconduit.py:382-391
  - pytest_collection_error: `ImportError: cannot import name 'IConduit' from partially initialized module '...iconduit'`
  IMPACT: The lane stays bounded, but the interface cycle has to be resolved in
    `iconduit.py` before test collection can pass.
  NEXT: remove the eager `ISpellSpace` import from `iconduit.py`, quote the
    spellspace annotations there, then rerun the focused mypy and unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T15:38:09Z
  TYPE: MEASURE
  CLAIM: The codegen/sync/interface lane is green in the bounded checks.
    `creation_context_codegen.py` did not reproduce in the focused slice, so it
    was left untouched. The actual fixes were the truthful `IConduit` /
    `ISpellSpace` cycle break across the two interfaces plus local optional
    deque and context-manager return typing cleanup in `TicketFlag` and
    `FastSwitch`, while preserving the existing cleanup behavior tested in the
    unit suite.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellspace.py:1-41
  - src/melder/utilities/interfaces/iconduit.py:1-16
  - src/melder/utilities/interfaces/iconduit.py:382-405
  - src/melder\utilities\synchronization\ticket_flag.py:1-219
  - src/melder\utilities\synchronization\fast_switch.py:1-146
  IMPACT: The reported sync/interface cluster is removed without widening into
    a broader primitive or codegen redesign.
  NEXT: report the bounded fix and wait for the next exact bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded codegen/sync/interface typing lane.
