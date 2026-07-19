# Task: add conduit mutation research surface

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-add-conduit-mutation-research-surface
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T13:34:38Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Add the missing `Conduit.get_mutation_research()` runtime surface so the
mutation-research component tests can reach the Aether-owned root through a
live conduit.

## Ticket Contract
- ENTRY_GATE: full-suite pytest stop-on-first-failure now breaks in the
  mutation-research component matrix because `Conduit` lacks
  `get_mutation_research()`
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/utilities/interfaces/iconduit.py`
  - directly implicated mutation-research interface files only if required
- DEPENDENCIES:
  - Aether-owned MutationResearch root already exists and is exercised by the
    component test
- EXIT_GATE: the original failing mutation-research component test is green
  without inventing a fake shim
- FAILURE_ESCALATION: raise `BLOCKER` if the expected Aether-owned surface no
  longer exists and the component test assumption is stale

## Scope Boundaries
- In scope:
  - missing conduit mutation-research surface
  - truthful interface exposure for that method
- Out of scope:
  - broader mutation research redesign
  - unrelated component failures after this first mutation blocker

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next full-suite blocker is a missing conduit runtime method

## Steps / Checklist
- [ ] inspect the failing mutation-research component test and the Aether-owned root
- [ ] patch the concrete conduit and interface surface
- [ ] rerun the targeted mutation-research component test
- [ ] continue to the next suite failure only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- conduit-facing mutation research accessor that returns the Aether-owned root

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/interfaces/iconduit.py`
- directly implicated mutation-research interface files only if needed

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\component\melder\mutation_research\test_mutation_research_root_component.py::test_component_conduit_returns_aether_owned_mutation_research[1]`

## Risks / Rollback Notes
- Low to medium risk. This looks like a missing façade method, but I need to
  confirm the Aether-owned root is still the intended ownership boundary.

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
- DATETIME: 2026-05-18T13:34:38Z
  TYPE: FACT
  CLAIM: The next full-suite blocker is a missing conduit surface, not a
    failing implementation. The component mutation-research matrix calls
    `conduit.get_mutation_research()` and asserts it returns the same
    Aether-owned root exposed on `conduit._aether.mutation_research`, but the
    concrete `Conduit` class does not currently implement that method.
  EVIDENCE:
  - tests/component/melder/mutation_research/test_mutation_research_root_component.py:64-81
  IMPACT: The next fix should stay bounded to the conduit/interface façade
    ring unless inspection shows the test is stale about MutationResearch
    ownership.
  NEXT: inspect `Conduit`, `IConduit`, and the Aether-owned MutationResearch
  surface before adding the accessor.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:38:05Z
  TYPE: FACT
  CLAIM: The conduit-facing accessor is now patched in source. `IConduit` and
    `Conduit` were the original target, but the practical runtime fix stays on
    the concrete `Conduit` only for now because importing
    `IMutationResearch` into `IConduit` immediately opens the existing
    mutation-interface cycle (`iconduit -> imutationresearch ->
    imutationconduit -> iconduit`). The concrete conduit method itself is a
    direct façade over the existing Aether-owned `mutation_research` root
    instead of a new shim or duplicate owner.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2255-2313
  - src/melder/utilities/interfaces/imutationresearch.py:1-89
  - src/melder/utilities/interfaces/imutationconduit.py:1-31
  IMPACT: The targeted component failure should now move from missing-method to
    either green or the next real mutation-root contract issue.
  NEXT: rerun the original failing mutation-research component test with
  verbose traceback.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:40:46Z
  TYPE: MEASURE
  CLAIM: The original mutation-research component failure is now green. The
    concrete `Conduit.get_mutation_research()` façade correctly returns the
    same Aether-owned root exercised by the component test.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2291-2313
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\component\melder\mutation_research\test_mutation_research_root_component.py::test_component_conduit_returns_aether_owned_mutation_research[1]` -> `1 passed`
  IMPACT: The current suite blocker is cleared, so the next move is another
    full-suite stop-on-first-failure run.
  NEXT: rerun `pytest -vv -x --tb=long` across the suite and capture the next
    failure if one exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Bounded conduit-facing mutation-research accessor lane opened for the next
full-suite blocker.
