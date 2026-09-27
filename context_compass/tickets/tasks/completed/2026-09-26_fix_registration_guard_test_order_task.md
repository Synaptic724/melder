

# Task: The registration-guard test passes in any order

## Metadata
- Completed: 2026-09-26T21:59:01Z
- Closure Basis: owner turn-in in chat (2026-09-26T21:59Z): "I accept your 2/3 continue working on the last part"
  (the Phase-5 pool fix and the guard-test fix; the tests docs task stays open).
- Summary: The system-document view fixtures boot a fresh Aether after their teardown resets and the guard test sets
  up its own world, so the selection passes in either order on 3.14t and GIL. Test-only change.
- Task ID: TASK-2026-09-26-fix-registration-guard-test-order
- Story: none
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-26T21:12:25Z
- Updated: 2026-09-26T21:59:01Z

## Objective
`tests/unit/melder/test_melder_registration_guard.py::test_bind_rejects_internal_class` passes alone and fails with
"Nexus must be initialized with an Aether instance." when run after the system-document tests. Find which test
leaves singleton state behind and make the suite order-independent, or raise it if the cause is in src.

## Ticket Contract
- ENTRY_GATE: owner approval (Notes); cause found and recorded before any edit.
- EXECUTION_BOUNDARY: test files and fixtures only; a src cause is raised as a finding with a DECISION_REQUEST.
- DEPENDENCIES: none.
- EXIT_GATE: the selection that failed passes in both orders on 3.14t and GIL; the test still passes alone.
- FAILURE_ESCALATION: DECISION_REQUEST if the cause is a production defect in Aether/Nexus reinitialization.

## Scope Boundaries
- In scope: the failing selection and the fixture or test that leaks state.
- Out of scope: unrelated test isolation.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner instruction to fix the reported follow-ups, 2026-09-26T21:12:25Z.
- from_state: review
- to_state: done
- transition_reason: Owner turn-in, 2026-09-26T21:59:01Z; see the Closure Basis.

## Steps / Checklist
- [x] Bisect the selection to the leaking test.
- [x] Read the leaking test and the Aether/Nexus reset path; decide test vs src.
- [x] Fix and rerun both orders.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Order-independent selection.

## Files / Paths Impacted
- tests/unit/melder/test_melder_registration_guard.py (and the leaking test, named in Notes)

## Validation
- Both orders on 3.14t and GIL (21:26:50Z note); the 7-file selection 255 passed, 1 skipped (21:45:09Z).
  Nothing was rerun at closure.

## Risks / Rollback Notes
- A shared fixture change can alter other tests' setup; rerun their files.

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
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Aether/Nexus singleton reset between tests
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T21:12:25Z
  TYPE: DECISION
  CLAIM: Owner, after the override lane turn-in: "yeah go ahead and fix all that shit and finish up all those things,
    ok fix the rare crash bro thats a correctness issue". This task is one of the three follow-ups melder_0 reported
    (Phase-5 pool race, order-dependent guard test, weak tests system docs); the deleted unroll benchmarks need no
    action (they measured the retired emitter's dict-vs-unroll choice).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Work is owner-approved; file lists are recorded here before any edit.
  NEXT: Bisect the failing selection on the work copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T21:25:39Z
  TYPE: FACT
  CLAIM: Test-side cause, no src defect. Paired with the guard file, only test_system_document_view.py and
    test_multithreading_system_document_view.py make test_bind_rejects_internal_class fail (the build_assets pair
    failures are the known copies-without-context_compass ones). Their autouse fixture resets AetherUtilitySystem,
    Nexus and Aether after each test but boots no new Aether, although its docstring says a test there "must not
    be the reason an unrelated test later in the session sees a dirty Aether". Spellbook.__init__ calls Nexus()
    with no arguments and relies on the Nexus an Aether boot constructs, and `Spellbook._aether` (the only
    ClassVar holding an Aether in src) still points at the cleaned instance, so the next Spellbook() raises "Nexus
    must be initialized with an Aether instance". The guard test has no setup of its own and passed only when
    something before it left a live world. The house pattern (reset the three, `Aether()`, rebind) is used by the
    other Nexus-touching fixtures. The reset hook is test-only, so production is unaffected.
  EVIDENCE:
  - tests/unit/melder/test_system_document_view.py:50-80
  - tests/integration/melder/multithreading/test_multithreading_system_document_view.py:53-71
  - tests/unit/melder/test_melder_registration_guard.py:32-39
  - src/melder/aether/spellbook/spellbook.py:261-266
  - src/melder/nexus/nexus.py:245-266
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:12-25
  IMPACT: Fix both sides: the view fixtures leave a freshly booted Aether bound to Spellbook after each test;
    the guard test gets its own fresh-world fixture.
  NEXT: Edit on the ~/work/s7/pre copy, run both orders on 3.14t and GIL. FILES:
    - tests/unit/melder/test_system_document_view.py
    - tests/integration/melder/multithreading/test_multithreading_system_document_view.py
    - tests/unit/melder/test_melder_registration_guard.py
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:26:50Z
  TYPE: MEASURE
  CLAIM: Fixed on a copy (apply_test_order_edits.py, 9 anchored line edits in 3 test files, CRLF kept): both view
    fixtures now boot a fresh Aether and bind it to Spellbook._aether after their teardown resets (docstring
    contract updated), and the guard file has an autouse fixture that resets and boots before and after each
    test. 3.14t and PYTHON_GIL=1, both orders: view + guard 87 passed, multithreading view + guard 14 passed. The
    original 7-file selection: 253 passed, 1 skipped, 2 failed (the two system-documents builder tests that fail
    only in copies without context_compass/, known); the guard test passes there now.
  EVIDENCE:
  - context_compass/artifacts/compiler_pool_snapshot_20260926/apply_test_order_edits.py:1-110
  - tests/unit/melder/test_melder_registration_guard.py:1-39
  IMPACT: The selection is order-independent; no src change.
  NEXT: Apply to the device with the Phase-5 lane's device apply and verify byte-identity.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:45:09Z
  TYPE: MEASURE
  CLAIM: Applied to the device and the work copy with the same script (byte-identical trees). On the work copy the
    7-file system-document selection is 255 passed, 1 skipped (the guard test included); the two builder failures
    seen earlier were only in a copy without context_compass/.
  EVIDENCE: tests/unit/melder/test_melder_registration_guard.py:1-69
  IMPACT: Done; review for the owner's turn-in.
  NEXT: Owner acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:49:08Z
  TYPE: FACT
  CLAIM: Correction to the 21:25:39Z FACT: `Spellbook._aether` is the only Aether cache annotated ClassVar, but not
    the only class-level Aether: CommandSystem and StaticFrameViewer also bind `_aether = Aether()` at class level.
    The fix stands (the guard test builds only a Spellbook, and the view fixtures now leave a live Aether that
    `Spellbook` uses); a test that builds a CommandSystem or StaticFrameViewer after a bare reset still needs its own
    fixture, which the Nexus/Rift suites already have.
  EVIDENCE:
  - src/melder/nexus/rift/command_system/command_system.py:98-98
  - src/melder/nexus/rift/frame_viewer/static_frame_viewer.py:61-61
  - src/melder/aether/spellbook/spellbook.py:175-175
  IMPACT: The tests docs state all three caches.
  NEXT: none for this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T21:59:01Z
  TYPE: DECISION
  CLAIM: Closed on the owner's turn-in (see the Closure Basis); acceptance given.
  EVIDENCE: tickets/tasks/completed/2026-09-26_fix_registration_guard_test_order_task.md
  IMPACT: The ticket moves to its completed folder; board and artifact rows are synced in the same pass.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Review. The view fixtures leave a freshly booted Aether after their teardown resets, and the guard test
sets up its own; the selection passes in either order on 3.14t and GIL. Test-only change.
Closed 2026-09-26T21:59:01Z on the owner's turn-in.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
