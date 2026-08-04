Completed: 2026-05-23T19:26:44Z
Summary: Realigned stale conduit cloud/cluster surface tests to the current runtime contract
and cleared the narrow failing ring.
Summary: Closed by user cleanup request after the stale expectations were superseded by later
component/integration coverage on the same surfaces.

# Task: Align conduit cloud and cluster surface tests to current runtime

## Metadata
- Task ID: TASK-2026-05-22-align-conduit-cloud-cluster-surface-tests
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-22T13:46:49Z
- Updated: 2026-05-23T19:26:44Z

## Objective
Repair the stale conduit cloud/cluster surface tests so they match the current
runtime contract instead of asserting that still-supported helpers were removed.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected to the broader test failures after
  the `_active_spell` rename validation pass.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/aether/conduit/test_conduit_dynamic.py`
  - `tests/unit/melder/aether/test_nexus.py`
- DEPENDENCIES:
  - the current live `Conduit` cloud helper surface in
    `src/melder/aether/conduit/conduit.py`
  - the broader Nexus command-surface tests already asserting capability/codegen
    exposure for cloud and cluster helpers
- EXIT_GATE: the stale assertions are aligned to current runtime truth and the
  focused failing ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the tests expose a real
  contract contradiction between raw Conduit and command-surface expectations.

## Scope Boundaries
- In scope:
  - stale test expectation updates
  - narrow docstring/intent wording updates in the touched tests
- Out of scope:
  - runtime behavior changes
  - broader cloud/cluster API redesign
  - unrelated Nexus or conduit failures

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the stale cloud/cluster surface assertions are updated and
  the focused failing ring is now green.

## Steps / Checklist
- [ ] Re-read the stale failing tests against the live `Conduit` surface.
- [ ] Patch only the stale assertions and wording.
- [ ] Re-run the narrow failing ring.
- [x] Re-read the stale failing tests against the live `Conduit` surface.
- [x] Patch only the stale assertions and wording.
- [x] Re-run the narrow failing ring.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated unit tests aligned to the current conduit cloud/cluster surface

## Files / Paths Impacted
- `tests/unit/melder/aether/conduit/test_conduit_dynamic.py`
- `tests/unit/melder/aether/test_nexus.py`

## Validation
- `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_dynamic.py tests\unit\melder\aether\test_nexus.py`
- Result: `180 passed, 1 warning`

## Risks / Rollback Notes
- Risk: one or more of the failing tests may reflect a half-finished attempted
  runtime deprecation instead of simple test drift.
- Rollback: keep the patch limited to expectations already contradicted by the
  broader current test file contract.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into runtime API changes in this task.
- [ ] No silent contract edits without matching test wording.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-22T13:46:49Z
  TYPE: FACT
  CLAIM: The reported failures are stale expectation tests, not a regression
    from the `_active_spell` rename. The live `Conduit` still exposes
    `get_conduit_cloud(...)`, and the broader `test_nexus.py` file already
    treats cloud/cluster helpers as supported on capability and selected
    codegen command surfaces. So the failing assertions are internally
    inconsistent with the current suite's broader contract.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:985-999
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:154-163
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:601-626
  - tests/unit/melder/aether/test_nexus.py:1986-1994
  - tests/unit/melder/aether/test_nexus.py:5134-5148
  - tests/unit/melder/aether/test_nexus.py:4614-4615
  IMPACT: The right fix is a narrow test alignment pass, not a runtime surface
    change.
  NEXT: patch only the stale tests and rerun the failing ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T13:46:49Z
  TYPE: MEASURE
  CLAIM: The stale conduit cloud/cluster assertions are fixed and the focused
    ring is green. The raw `Conduit` tests now assert that
    `get_conduit_cloud(...)` is still present while the cluster mutator helpers
    remain absent on the raw conduit surface, and the capability-room Nexus
    test now executes `get_conduit_cloud` successfully through the command
    surface instead of expecting an `AttributeError`.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:154-163
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:601-626
  - tests/unit/melder/aether/test_nexus.py:4588-4616
  - src/melder/aether/conduit/conduit.py:985-999
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_dynamic.py tests\unit\melder\aether\test_nexus.py` -> `180 passed, 1 warning`
  IMPACT: The broader suite no longer has these internally inconsistent stale
    expectations blocking progress.
  NEXT: return to the SpellIndex semantic and mechanics lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the narrow stale-test alignment for conduit cloud and cluster
surface expectations after the broader suite exposed internally inconsistent
assertions.
