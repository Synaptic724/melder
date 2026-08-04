# Task: fix spellbook unit import drift after move

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-spellbook-unit-import-drift-after-move
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T13:23:24Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Find and fix the import breakage in the Spellbook unit-test tree after the
tests were moved from the old top-level location into the current
`tests/unit/melder/spellbook` layout.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to inspect the Spellbook unit-test
  import breakage after the move.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/spellbook/**`
  - directly implicated shared test helpers under `tests/**` only if import
    drift points there
  - source files only if the failing import contract truly belongs in runtime
- DEPENDENCIES:
  - current pytest collection behavior for the Spellbook unit tree
  - no shims, no fake surfaces, no unrelated refactors
  - raise to Mark directly if the import contract is ambiguous
- EXIT_GATE:
  - the concrete import-failure bucket is identified
  - bounded fixes are applied where the drift really lives
  - focused collection and/or unit validation confirms the import lane is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the failures require a wider
  packaging/import-policy change outside the moved test tree

## Scope Boundaries
- In scope:
  - stale moved-test import paths
  - stale shared-helper import paths
  - collection-only import breakage in the Spellbook unit ring
- Out of scope:
  - unrelated Spellbook runtime behavior bugs
  - broad repo-wide import cleanup unless the evidence forces it

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user selected the Spellbook unit import breakage as
  the next active lane.

## Steps / Checklist
- [ ] collect the Spellbook unit tree to capture the exact import failures
- [ ] search the tree for stale old-path imports and broken shared-helper refs
- [ ] patch only the bounded import drift proven by the evidence
- [ ] rerun focused collection and/or the direct Spellbook unit ring
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded Spellbook unit-test import fix

## Files / Paths Impacted
- `tests/unit/melder/spellbook/**`
- only if required by truthful fix:
  - directly implicated helpers under `tests/**`
  - directly implicated packaging/import files under `src/**`

## Validation
- Ran:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\bind\test_bind.py -k "test_bind_decorator_returns_original"`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook --collect-only`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\custom_exceptions\test_spellbook_validation_error.py --collect-only`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit --collect-only`
- Results:
  - `1 passed, 215 deselected, 1 warning`
  - `1998 tests collected in 1.79s`
  - `5 tests collected in 0.21s`
  - `6192 tests collected in 1.09s`

## Risks / Rollback Notes
- Low to medium risk. This should be mostly test-path drift, but it could
  expose a deeper shared-helper or packaging import seam.

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
- DATETIME: 2026-05-19T13:23:24Z
  TYPE: FACT
  CLAIM: The next active lane is the Spellbook unit-test import breakage after
    the tests were moved into `tests/unit/melder/spellbook`. The first step is
    exact collection evidence so we can tell whether the drift is inside the
    moved test files, in shared helpers, or in packaging/runtime imports.
  EVIDENCE:
  - user_request: "look into my spellbook unit tests I moved from top level into the aehter and it broke all imports"
  - tests/unit/melder/spellbook/** current file inventory
  IMPACT: The lane should start with collection-only failure capture, not code
    edits.
  NEXT: run focused Spellbook unit collection and search for stale old-path
    imports in the moved tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T13:23:24Z
  TYPE: MEASURE
  CLAIM: The direct Spellbook unit tree currently collects cleanly. A focused
    `pytest --collect-only` over `tests/unit/melder/spellbook` produced `1998`
    collected tests with no import-collection failures, so the reported
    breakage is not in the moved Spellbook subtree itself under the current
    runner configuration.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook --collect-only` -> `1998 tests collected in 0.50s`
  - tests/unit/melder/spellbook/** current collection surface
  IMPACT: The import drift is likely in the wider unit tree, a shared helper,
    or a stale external path assumption rather than inside the direct Spellbook
    subtree.
  NEXT: search the wider `tests/unit/**` tree for stale old Spellbook-path
    imports and cross-tree helper imports that still assume the pre-move
    layout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T13:23:24Z
  TYPE: MEASURE
  CLAIM: The broader unit collection also succeeds in the current workspace,
    and the only visible cross-tree imports under the Spellbook and Aether
    unit trees are normal shared-helper imports like `tests._frame_posture_test_support`
    and `tests.mocks.spellbook.*`. I could not reproduce a current import
    failure from the moved Spellbook test tree.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit --collect-only` -> `6192 tests collected in 1.38s`
  - tests/unit/melder/spellbook/** collection surface
  - tests/unit/melder/aether and tests/unit/melder/spellbook shared-helper import grep
  IMPACT: There is no concrete failing import bucket to patch in the current
    workspace. The next useful input is the exact failing command/output or the
    specific moved test files/branch diff that still reproduces the breakage.
  NEXT: ask Mark for the exact failing pytest command or the specific moved
    files that still reproduce the import failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T13:34:17Z
  TYPE: FACT
  CLAIM: The concrete import drift is now visible. A large part of the
    Spellbook-related unit tree still imports the old prefix
    `melder.aether.spellbook...`, including the exact failing file
    `tests/unit/melder/spellbook/bind/test_bind.py`, while its monkeypatch
    fixture already targets the current `melder.spellbook...` path. This is a
    bounded mechanical moved-test import rewrite, not a runtime packaging bug.
  EVIDENCE:
  - tests/unit/melder/spellbook/bind/test_bind.py:6-20
  - validation_result: `rg -n "melder\\.aether\\.spellbook" tests\unit\melder\spellbook tests\unit\melder\utilities\custom_exceptions\test_spellbook_validation_error.py`
  - user_failure_output: `ModuleNotFoundError: No module named 'melder.spellbook'` during monkeypatch import resolution
  IMPACT: The right fix is a deterministic test-only prefix rewrite from
    `melder.aether.spellbook` to `melder.spellbook` across the affected moved
    test files.
  NEXT: rewrite the stale import prefix in the affected test files only, then
    rerun focused collection on the failing bind file and the full Spellbook
    unit tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T13:35:35Z
  TYPE: FACT
  CLAIM: The repo's actual runtime layout still lives under
    `melder.aether.spellbook`, not `melder.spellbook`. The direct source-file
    inventory shows `src/melder/aether/spellbook/**` and no
    `src/melder/spellbook/**`, so the stale seam is the moved tests that now
    mix two prefixes: old imports already point at the real package, but some
    moved files and monkeypatch strings were changed to the nonexistent
    `melder.spellbook...` path.
  EVIDENCE:
  - src/melder top-level inventory
  - src/melder/aether/spellbook/** source inventory
  - src/melder/__init__.py: import/export surface still points to `melder.aether.spellbook.*`
  - tests/unit/melder/spellbook/bind/test_bind.py:6-20
  - tests/unit/melder/spellbook/bind/test_bind.py:83-92
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\bind\test_bind.py -k "test_bind_decorator_returns_original"` -> `ModuleNotFoundError: No module named 'melder.spellbook'`
  IMPACT: The correct bounded fix is to make the moved tests consistently use
    the real runtime prefix `melder.aether.spellbook...`, not to invent a new
    source package path.
  NEXT: revert the affected moved test files back to
    `melder.aether.spellbook...`, then rerun the failing bind file and full
    Spellbook unit collection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T13:36:28Z
  TYPE: MEASURE
  CLAIM: The moved-test import lane is green. The affected Spellbook-related
    unit files were normalized back to the real runtime package prefix
    `melder.aether.spellbook...`, the failing bind file now runs, the
    Spellbook unit subtree collects cleanly, the custom-exception Spellbook
    test collects cleanly, and the broader `tests/unit` collection is clean
    again.
  EVIDENCE:
  - tests/unit/melder/spellbook/bind/test_bind.py:1-25
  - tests/unit/melder/spellbook/test_spellbook.py:1-20
  - tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py:1-10
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\bind\test_bind.py -k "test_bind_decorator_returns_original"` -> `1 passed, 215 deselected, 1 warning`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook --collect-only` -> `1998 tests collected in 1.79s`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\custom_exceptions\test_spellbook_validation_error.py --collect-only` -> `5 tests collected in 0.21s`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit --collect-only` -> `6192 tests collected in 1.09s`
  IMPACT: The import breakage was test-path drift only. No runtime packaging
    or source import changes were needed.
  NEXT: report the bounded fix and wait for the next exact lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:01:22Z
  TYPE: FACT
  CLAIM: The same import-drift class also exists in two Aether unit tests, but
    the real module locations are different from the earlier Spellbook case.
    `Spellbook` still lives at `melder.aether.spellbook.spellbook.Spellbook`,
    while `Rift` lives at `melder.nexus.rift.rift.Rift`, not under
    `melder.aether.nexus...`. The failures are stale monkeypatch target
    strings, not runtime package bugs.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_frame_manager.py:930-936
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:214-255
  - src/melder/aether/spellbook/** source inventory
  - src/melder/nexus/rift/rift.py
  IMPACT: This stays a bounded test-only import lane. The next fix is to
    correct those two monkeypatch strings only.
  NEXT: patch the stale monkeypatch targets in the two Aether unit files, then
    rerun the exact failing tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:01:22Z
  TYPE: MEASURE
  CLAIM: The surfaced Aether-side import drift is also green now. The two
    stale monkeypatch strings were corrected to the real module locations, and
    the exact failing tests from the user output now pass.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_frame_manager.py:930-936
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:214-255
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_nexus_frame_manager.py -k "test_nexus_frame_manager_bootstrap_root_conduit_binds_and_refreshes_overview"` -> `1 passed, 85 deselected, 1 warning`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_nexus_orchestration_and_lifecycle.py -k "test_nexus_create_rift_unregisters_gate_and_does_not_consume_configuration_when_add_rift_fails or test_nexus_create_rift_cleans_gate_when_constructor_raises"` -> `2 passed, 23 deselected, 1 warning`
  IMPACT: The moved/import-drift lane now covers both the Spellbook subtree and
    the surfaced Aether stale monkeypatch targets.
  NEXT: report the bounded test-only import fixes and wait for the next exact
    lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded Spellbook unit import lane. Start with collection evidence and
stale-path search before editing.
