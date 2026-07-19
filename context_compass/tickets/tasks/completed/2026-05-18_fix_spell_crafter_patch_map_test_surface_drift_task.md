# Task: fix spell crafter patch map test surface drift

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-spell-crafter-patch-map-test-surface-drift
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:27:19Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next non-Nexus blocker by aligning `SpellCrafter` unit-test stubs with
the live public patch-map surface.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first non-Nexus suite failure is
  `test_capture_phase8_11_codegen_ir_exports_sorted_payloads`
  raising because the test stub uses private `_targets_by_spec` fields while
  runtime reads public `targets_by_spec` properties.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- DEPENDENCIES:
  - current non-Nexus suite-driving lane
  - live patch-map public property contract
- EXIT_GATE:
  - the targeted failing unit test is green
  - patch-map unit stubs in this file use the live public property names
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if source evidence shows runtime
  should still accept the old private stub shape

## Scope Boundaries
- In scope:
  - test-only stub surface normalization in `test_spell_crafter.py`
  - confirming the live patch-map public contract from source
- Out of scope:
  - runtime patch-map redesign
  - unrelated SpellCrafter failures after this stub-surface drift is corrected

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live non-Nexus blocker is a bounded test-surface
  drift against the live patch-map public API

## Steps / Checklist
- [ ] confirm the live patch-map public surface and the stale test stub shape
- [ ] patch the affected `SimpleNamespace` stubs to use public property names
- [ ] rerun the targeted failing unit test
- [ ] continue to the next non-Nexus blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- normalized patch-map test stubs aligned to the live public contract

## Files / Paths Impacted
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\spellbook\spell_crafter\test_spell_crafter.py::test_capture_phase8_11_codegen_ir_exports_sorted_payloads`

## Risks / Rollback Notes
- Low risk. This lane should stay test-only if the source public contract is
  still current.

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
- DATETIME: 2026-05-18T14:27:19Z
  TYPE: FACT
  CLAIM: The next non-Nexus blocker is a test-surface drift, not a runtime bug.
    `SpellCrafter` reads public `targets_by_spec` and `specificity_by_spec`
    properties from Phase 10 patch maps, but the unit test file still builds
    `SimpleNamespace` stubs with old private `_targets_by_spec` and
    `_specificity_by_spec` fields in multiple places.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:2241-2301
  - src/melder/spellbook/spell_crafter/spell_crafter.py:2954-2964
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:208-229
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:631-640
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5766-5773
  IMPACT: The broad non-Nexus suite stops on stale unit scaffolding before the
    next real runtime issue.
  NEXT: normalize the affected patch-map stubs in `test_spell_crafter.py` to
    the live public property names, then rerun the targeted failing test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:27:19Z
  TYPE: FACT
  CLAIM: The stale private patch-map stub fields have been normalized across
    `test_spell_crafter.py`. The affected `SimpleNamespace` fixtures now expose
    public `targets_by_spec` and `specificity_by_spec` fields, and there are no
    remaining `_targets_by_spec` / `_specificity_by_spec` occurrences in that unit file.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5766-5773
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5917-5938
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:6048-6086
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:6361-6399
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:7625-7796
  IMPACT: The test file now mirrors the live public patch-map surface instead of
    poking stale private field names.
  NEXT: rerun the exact failing unit test for Phase 8/11 IR export ordering.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-18T14:27:19Z
  TYPE: MEASURE
  CLAIM: The targeted patch-map drift lane is green.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5766-5773
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\spellbook\spell_crafter\test_spell_crafter.py::test_capture_phase8_11_codegen_ir_exports_sorted_payloads` -> `1 passed`
  IMPACT: This non-Nexus blocker is cleared, so the next useful move is another
    stop-on-first non-Nexus suite pass.
  NEXT: rerun `pytest -vv -x --tb=long -k "not nexus and not rift"` and route
    the next failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active lane for the next non-Nexus blocker. Current evidence says the runtime
public contract is stable and the unit file needs to stop stubbing private
patch-map fields directly.
