# Task: Transfer-ownership tests (10 unit / 3 component / 3 integration)

## Metadata
- Task ID: TASK-2026-06-20-transfer-ownership-tests
- Story: UNKNOWN (standalone test task)
- Status: review
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p2
- Created: 2026-06-20T16:11:16Z
- Updated: 2026-06-20T16:18:00Z

## Objective
Add focused transfer-ownership tests at three levels, validating the post-migration shape: the
strategy is envelope-only (plans scopes from the conduit-built footprint metadata) and the Conduit
owns footprint discovery (`_build_transfer_transaction_metadata` / `_discover_transfer_footprint`).

## Ticket Contract
- ENTRY_GATE: migration task in review (TASK-2026-06-20-migrate-transfer-footprint-to-conduit); fixtures
  confirmed (unit strategy fixture; component `_make_spellbook(dynamic=True)`; integration
  `_make_dynamic_configuration` + `conjure(dynamic=True)`).
- EXECUTION_BOUNDARY: ADD test files only (unit/component/integration). No source edits.
- DEPENDENCIES: the migrated conduit methods + the envelope strategy.
- EXIT_GATE: 10 unit + 3 component + 3 integration authored, py_compile-clean; user runs the 3.14t
  suites green.
- FAILURE_ESCALATION: CONFLICT if a test exposes a real migration regression.

## Steps / Checklist
- [x] Unit (10): tests/unit/.../change_control_manager/test_transfer_ownership_transaction_strategy.py
      — guards (conduit identity, missing footprint), conduit/ward/spellbook/cluster/binding scopes,
      transaction-owner scopes, spellbook_id, capabilities, sort + identity stamp. py_compile-clean.
- [x] Component (3): tests/component/melder/aether/conduit/test_conduit_component_transfer_footprint.py
      — `_build_transfer_transaction_metadata` stamps the footprint; `_discover_transfer_footprint`
      returns participants + identity keys; `transfer_spell_ownership` still moves the spell. clean.
- [x] Integration (3): tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py
      — ownership moves to target; meld resolution flips; selective single-spell move. clean.
- [x] Findings documented in Notes.

## Validation
- Not run (agent: Py3.10 sandbox cannot import the 3.14t chain).
- Recommended:
  - `pytest tests/unit/melder/aether/dev_ops/change_control_manager/test_transfer_ownership_transaction_strategy.py -q`
  - `pytest tests/component/melder/aether/conduit/test_conduit_component_transfer_footprint.py -q`
  - `pytest tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py -q`

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: migration in review; fixtures confirmed; authoring begun.

## Notes
- DATETIME: 2026-06-20T16:11:16Z
  TYPE: PLAN
  CLAIM: Tests validate the migration shape: strategy reads the conduit-built footprint (no live
    reach); conduit `_discover_transfer_footprint` does the domain discovery. Component tests call
    `_build_transfer_transaction_metadata` directly on a real conduit to assert the stamped footprint.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2880-3117
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:385-470
  - tests/component/melder/aether/conduit/test_conduit_component_transactions.py:455-503
  IMPACT: Coverage for the last reaching strategy's migration.
  NEXT: Write the unit file first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-20T16:24:00Z
  TYPE: MEASURE
  CLAIM: User ran all 16 transfer tests on .venv_new (Python 3.14t) -> ALL PASSED (10 unit /
    3 component / 3 integration). Validates the footprint-into-conduit migration end to end:
    envelope strategy plans off the conduit-built footprint; conduit
    _build_transfer_transaction_metadata / _discover_transfer_footprint produce the footprint; the
    transfer still moves ownership through to meld resolution.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transfer_ownership_transaction_strategy.py
  - tests/component/melder/aether/conduit/test_conduit_component_transfer_footprint.py
  - tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py
  IMPACT: Both the migration task and this test task are validated green.
  NEXT: Await user OK to close both transfer lanes (and the optional conftest path fix).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-20T16:24:00Z
  TYPE: FACT
  CLAIM: Test path finding: tests/conftest.py adds `src/` to sys.path but NOT the repo root, and the
    tests/ tree has no __init__.py (namespace layout). So `from tests.mocks...` only resolves when the
    repo root is on sys.path -- which `python -m pytest` provides (cwd) but the bare `pytest` console
    script does not. Affects every test importing `tests.mocks`, not just these. Optional fix: insert
    PROJECT_ROOT (already computed in conftest) into sys.path.
  EVIDENCE:
  - tests/conftest.py
  IMPACT: Bare `pytest <files>` fails to collect tests that import tests.mocks; `python -m pytest` works.
  NEXT: User decides whether to apply the conftest fix.
  REREAD: HELPFUL
  SCORE_0_TO_10: 6

## Context / Handoff Summary
Three transfer-ownership test files (10 unit / 3 component / 3 integration) validating the
footprint-into-conduit migration. Agent cannot run pytest; user runs the 3.14t suites.
