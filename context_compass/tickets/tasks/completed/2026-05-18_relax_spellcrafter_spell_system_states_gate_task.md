# Task: relax spellcrafter spell system states gate

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-relax-spellcrafter-spell-system-states-gate
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T13:42:56Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next full-suite blocker where `SpellCrafter` rejects the component
test's `_SpellSystemStatesStub` through an over-strict runtime
`ISpellSystemStates` gate before Phase 1/2/3 can run.

## Ticket Contract
- ENTRY_GATE: the next full-suite failure is
  `test_component_spell_crafter_spellmap_default_resolves_frame_only_candidate`
  raising `TypeError: SpellCrafter requires the concrete internal SpellSystemStates surface.`
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/spell_crafter.py`
  - `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`
  - directly implicated shared interface files only if the runtime contract truly needs them
- DEPENDENCIES:
  - the component spell-crafter tests that inject `_SpellSystemStatesStub`
- EXIT_GATE: the original component spell-crafter failure is green
- FAILURE_ESCALATION: raise `BLOCKER` if the component test assumption is
  stale and the runtime must continue requiring a stricter concrete state
  object

## Scope Boundaries
- In scope:
  - the runtime spell-system-state acceptance gate in `SpellCrafter`
  - the local component test stub only if the runtime contract genuinely
    requires additional methods
- Out of scope:
  - broader spell-system-state redesign
  - unrelated component failures after this one

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next full-suite failure is a bounded SpellCrafter/test-stub contract mismatch

## Steps / Checklist
- [ ] inspect the failing component test and `_SpellSystemStatesStub`
- [ ] patch the runtime gate or stub so the intended contract is truthful
- [ ] rerun the targeted spell-crafter component test
- [ ] continue to the next suite failure only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- spell-crafter gate fix for the component stub-backed phase 1/2/3 path

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`
- directly implicated shared interface files only if needed

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\component\melder\spellbook\test_spellbook_component_spell_crafter.py::test_component_spell_crafter_spellmap_default_resolves_frame_only_candidate`

## Risks / Rollback Notes
- Low to medium risk. The likely correct fix is to remove an over-strict runtime
  isinstance gate, but I need to confirm the phase path really only relies on the
  stubbed subset.

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
- DATETIME: 2026-05-18T13:42:56Z
  TYPE: FACT
  CLAIM: The next suite blocker is a SpellCrafter/test-stub contract mismatch.
    The component test injects `_SpellSystemStatesStub`, but
    `SpellCrafter._get_required_spell_system_states_from_spell(...)` hard-fails
    unless the attached object passes `isinstance(..., ISpellSystemStates)`.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:249-306
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:567-621
  - src/melder/spellbook/spell_crafter/spell_crafter.py:351-377
  IMPACT: The likely fix is to remove or relax the over-strict runtime gate
    unless the component test path proves it actually needs the full interface.
  NEXT: inspect the exact phase path used by the failing test and patch the
  runtime gate accordingly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:43:56Z
  TYPE: FACT
  CLAIM: The runtime gate is now relaxed in source. The helper no longer
    insists on `isinstance(..., ISpellSystemStates)` before accepting the
    attached spell-system-state surface, so the component spell-crafter tests
    can inject their narrow state recorder without tripping a concrete-type
    guard before Phase 1/2/3.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:351-372
  IMPACT: The original component failure should now proceed into the real phase
    path instead of dying during SpellCrafter initialization.
  NEXT: rerun the exact failing component spell-crafter test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:45:39Z
  TYPE: FACT
  CLAIM: The same helper block contained a second real runtime bug.
    `SpellCrafter.__init__` already called `_get_required_spellbook_from_spell(...)`,
    but the helper did not exist, and the instance helper
    `_get_required_spellbook()` incorrectly returned `self._spell` instead of
    the owning spellbook. Both are now fixed alongside the relaxed
    spell-system-state gate.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:256-259
  - src/melder/spellbook/spell_crafter/spell_crafter.py:294-321
  - src/melder/spellbook/spell_crafter/spell_crafter.py:344-364
  IMPACT: The targeted component path should now reach the real Phase 1/2/3
    logic instead of dying during SpellCrafter construction.
  NEXT: rerun the exact failing component spell-crafter test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:48:39Z
  TYPE: FACT
  CLAIM: The currently executed `SpellCrafter` helper block is still wrong in
    source. `__init__` assigns `_spell_validator` from `self._spell._spellbook`
    instead of the spellbook validator, `_get_required_spellbook()` returns the
    spell instead of the spellbook, and `__init__` still calls the missing
    `_get_required_spellbook_from_spell(...)` helper while
    `_get_required_spell_system_states_from_spell(...)` still carries the stale
    strict `ISpellSystemStates` gate.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:252-258
  - src/melder/spellbook/spell_crafter/spell_crafter.py:294-348
  IMPACT: The right fix is to patch the live helper block directly instead of
    continuing to chase test fallout around it.
  NEXT: patch the helper block in `spell_crafter.py`, then rerun the exact
    failing component spell-crafter test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:51:58Z
  TYPE: MEASURE
  CLAIM: The targeted component spell-crafter failure is now green. The live
    helper block no longer returns the spell instead of the spellbook, the
    missing `_get_required_spellbook_from_spell(...)` helper now exists, and
    the stub-backed phase path no longer dies on the stale strict
    SpellSystemStates gate.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:252-258
  - src/melder/spellbook/spell_crafter/spell_crafter.py:294-348
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\component\melder\spellbook\test_spellbook_component_spell_crafter.py::test_component_spell_crafter_spellmap_default_resolves_frame_only_candidate` -> `1 passed`
  IMPACT: This suite blocker is cleared, so the next useful move is another
    full-suite stop-on-first-failure run while staying out of the Nexus-heavy lane.
  NEXT: rerun `pytest -vv -x --tb=long` across the suite and capture the next
    non-Nexus failure if one exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Bounded SpellCrafter gate-fix lane opened for the next full-suite blocker.
