# Task: fix change control manager interface contract cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-change-control-manager-interface-contract-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T12:18:39Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `ChangeControlManager` override cluster by aligning the public
`IChangeControlManager` contract to the real revalidator and root-blueprint
surfaces.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded `ChangeControlManager` override
  cluster.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/ichangecontrolmanager.py`
  - `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
  - support contract only if required:
    - `src/melder/utilities/interfaces/irootresolutionblueprint.py`
  - bounded validation tests only:
    - `tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py`
- DEPENDENCIES:
  - current concrete `ChangeControlManager` behavior and tests
  - no casts, no shims, no fake local protocols
- EXIT_GATE:
  - the targeted override cluster is gone
  - public interface contract matches the concrete and tests truthfully
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current tests and
  concrete disagree on whether `set_revalidator(None)` is a valid public path

## Scope Boundaries
- In scope:
  - `set_revalidator(...)` callable optionality
  - `rebuild_component_of(...)` blueprint mapping type
  - `upsert_component_of(...)` blueprint mapping type
- Out of scope:
  - broader change-control redesign
  - unrelated DevOps mypy debt

## Steps / Checklist
- [ ] align `IChangeControlManager` to the real concrete/test contract
- [ ] patch the concrete only if the interface alignment reveals one remaining
      local mismatch
- [ ] rerun targeted mypy on the bounded file pair
- [ ] rerun the bounded change-control-manager unit ring
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded `ChangeControlManager` interface-contract fix

## Files / Paths Impacted
- `src/melder/utilities/interfaces/ichangecontrolmanager.py`
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- only if required:
  - `src/melder/utilities/interfaces/irootresolutionblueprint.py`
- validation:
  - `tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\utilities\interfaces\ichangecontrolmanager.py src\melder\aether\dev_ops\change_control_manager\change_control_manager.py`

## Risks / Rollback Notes
- Low risk. The main issue is stale interface typing, not runtime logic.

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
- DATETIME: 2026-05-19T12:18:39Z
  TYPE: FACT
  CLAIM: The `ChangeControlManager` override cluster is an interface-truth
    problem, not a runtime bug. The concrete and tests both say
    `set_revalidator(..., None)` is invalid and should raise, while the
    interface still allows `Optional[Callable]`. The concrete and callers also
    use root-blueprint mappings, so `dict[str, object]` is too weak for
    `rebuild_component_of(...)` and `upsert_component_of(...)`.
  EVIDENCE:
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1082-1144
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1147-1236
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:395-428
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py:964-970
  IMPACT: The right first fix is to align the public interface to the real
    concrete/test contract, not to widen the concrete just to satisfy stale
    typing.
  NEXT: patch `IChangeControlManager` to use a required revalidator callable
    and `Dict[str, IRootResolutionBlueprint]` for component-of rebuild/upsert,
    then rerun the bounded checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:18:39Z
  TYPE: MEASURE
  CLAIM: The targeted `ChangeControlManager` override cluster is green. The
    fix was purely interface truth: make `set_revalidator(...)` require a real
    callback and make `rebuild_component_of(...)` /
    `upsert_component_of(...)` accept `Dict[str, IRootResolutionBlueprint]`,
    then align the concrete method signatures to that same public contract.
  EVIDENCE:
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:395-428
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1082-1236
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\utilities\interfaces\ichangecontrolmanager.py src\melder\aether\dev_ops\change_control_manager\change_control_manager.py 2>&1 | Select-String 'src\\melder\\utilities\\interfaces\\ichangecontrolmanager.py:|src\\melder\\aether\\dev_ops\\change_control_manager\\change_control_manager.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\change_control_manager\test_change_control_manager.py` -> `47 passed, 1 warning`
  IMPACT: The user-supplied override cluster is fixed without widening the
    concrete runtime behavior.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:18:39Z
  TYPE: FACT
  CLAIM: A re-check after possible local edits showed the interface file was
    still correct but the concrete `ChangeControlManager` had drifted back to
    `Dict[str, RootResolutionBlueprint]` on
    `rebuild_component_of(...)` / `upsert_component_of(...)`. Restoring those
    two concrete signatures back to `Dict[str, IRootResolutionBlueprint]`
    cleared the bounded mypy slice again.
  EVIDENCE:
  - src/melder/utilities/interfaces/ichangecontrolmanager.py:411-428
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1147-1236
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\utilities\interfaces\ichangecontrolmanager.py src\melder\aether\dev_ops\change_control_manager\change_control_manager.py 2>&1 | Select-String 'src\\melder\\utilities\\interfaces\\ichangecontrolmanager.py:|src\\melder\\aether\\dev_ops\\change_control_manager\\change_control_manager.py:'` -> no output
  IMPACT: The lane remains green; the only drift was the concrete annotation on
    those two methods.
  NEXT: report the re-check result and keep the lane in review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Bounded `ChangeControlManager` interface-truth lane. Current evidence says the
interface is stale on revalidator optionality and root-blueprint mapping types.
