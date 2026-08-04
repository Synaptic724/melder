# Task: fix spell crafter change control revalidator idempotence

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-spell-crafter-change-control-revalidator-idempotence
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:23:27Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next non-Nexus blocker where `SpellCrafter` re-registers a conduit
change-control revalidator even when one is already present.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first non-Nexus suite failure is
  `test_ensure_change_control_ready_skips_when_revalidator_present`
  asserting that `_ensure_change_control_ready("cid")` should not call
  `set_revalidator(...)` when the conduit already has a registered revalidator.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/spell_crafter.py`
  - `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
  - `src/melder/utilities/interfaces/ichangecontrolmanager.py`
  - `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- DEPENDENCIES:
  - current non-Nexus suite-driving lane
  - change-control manager revalidator contract
- EXIT_GATE:
  - the targeted unit test is green
  - `SpellCrafter` no longer overwrites existing conduit-specific revalidators
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if source evidence shows the
  current overwrite behavior is intentional and the unit contract is stale

## Scope Boundaries
- In scope:
  - conduit-specific revalidator presence query
  - frame-wide and local `SpellCrafter` Phase 7 helper idempotence
  - directly implicated test stub contract
- Out of scope:
  - broader change-control redesign
  - unrelated SpellCrafter or Nexus work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live non-Nexus blocker is a bounded
  change-control revalidator idempotence mismatch with direct source and test evidence

## Steps / Checklist
- [ ] confirm the live failure and exact revalidator registration path
- [ ] add the smallest truthful per-conduit query surface
- [ ] patch `SpellCrafter` to skip duplicate registration
- [ ] rerun the targeted unit test
- [ ] continue to the next non-Nexus blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a bounded change-control revalidator idempotence fix

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/utilities/interfaces/ichangecontrolmanager.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\spellbook\spell_crafter\test_spell_crafter.py::test_ensure_change_control_ready_skips_when_revalidator_present`

## Risks / Rollback Notes
- Low risk if the fix stays conduit-scoped and does not change global
  change-control semantics.
- Medium risk if other callers rely on unconditional overwrite behavior.

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
- DATETIME: 2026-05-18T14:23:27Z
  TYPE: FACT
  CLAIM: The next non-Nexus blocker is a narrow change-control idempotence mismatch.
    `SpellCrafter._ensure_change_control_ready(...)` and its local variant
    always call `set_revalidator(...)`, while the unit contract expects duplicate
    registration to be skipped when a conduit already has a registered revalidator.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5641-5721
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1082-1116
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:395-427
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4936-4955
  IMPACT: The non-Nexus suite stops on a redundant-registration contract mismatch
    before reaching the next runtime issue.
  NEXT: add a conduit-specific revalidator presence query and patch `SpellCrafter`
    to skip duplicate registration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:23:27Z
  TYPE: FACT
  CLAIM: The code path is now aligned around an explicit per-conduit query.
    `IChangeControlManager` and `ChangeControlManager` expose
    `has_revalidator_for_conduit(...)`, the unit stub implements the same
    surface, and both frame-wide and local SpellCrafter Phase 7 helpers now
    skip duplicate `set_revalidator(...)` calls.
  EVIDENCE:
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:395-409
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1082-1144
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4357-4365
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5677-5733
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:239-266
  IMPACT: The fix is now interface-truthful and does not require caller-side
    probing of private manager internals.
  NEXT: rerun the failing unit test and the adjacent registration control test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-18T14:23:27Z
  TYPE: MEASURE
  CLAIM: The targeted change-control idempotence lane is green.
  EVIDENCE:
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:395-409
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1082-1144
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4357-4365
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5677-5733
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\spellbook\spell_crafter\test_spell_crafter.py::test_ensure_change_control_ready_registers_revalidator_when_missing tests\unit\melder\spellbook\spell_crafter\test_spell_crafter.py::test_ensure_change_control_ready_skips_when_revalidator_present` -> `2 passed`
  IMPACT: This non-Nexus blocker is cleared, and the next useful move is to
    resume the broader stop-on-first non-Nexus suite run.
  NEXT: rerun `pytest -vv -x --tb=long -k "not nexus and not rift"` and route
    the next failure into its own task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active lane for the next non-Nexus blocker. The clean fix should expose a
per-conduit revalidator presence check on the change-control manager and use it
from both frame-wide and local `SpellCrafter` Phase 7 wiring helpers.
