# Task: Default Class And Callable Profiles In AI Profile

## Metadata
- Task ID: TASK-2026-04-05-default-class-and-callable-profiles-in-ai-profile
- Story: STORY-2026-04-02-profile-contracts-and-access-boundaries
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T13:25:00Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Change the AI profile strategy so class spells populate both `class_profile`
and `callable_profile` by default instead of leaving `callable_profile` empty
for class-backed spells.

## Ticket Contract
- ENTRY_GATE: the current live strategy/tests were investigated and the user
  explicitly requested that the optional profiles be populated into
  `SpellAIProfile` by default.
- EXECUTION_BOUNDARY: AI profile strategy + focused tests only.
- DEPENDENCIES:
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py
- EXIT_GATE: class-backed AI profiles include both subprofiles by default and
  the focused test surface passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the callable-profile meaning
  for class spells becomes ambiguous beyond the current `MethodInspector`
  contract.

## Scope Boundaries
- In scope:
  - AI profile strategy behavior for class spells
  - focused spell-examiner tests
- Out of scope:
  - broader profile redesign
  - descriptor/view ACL work
  - runtime code outside spell-examiner AI profile behavior

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the AI profile strategy now populates both subprofiles for
  class spells by default and the focused test surface passed.

## Steps / Checklist
- [ ] Patch AI profile strategy for class spells.
- [ ] Update focused AI profile tests.
- [ ] Run focused compile/tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated AI profile strategy behavior
- focused unit tests

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py
- tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py
- codex/context_compass/tickets/tasks/2026-04-05_default_class_and_callable_profiles_in_ai_profile_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py`

## Risks / Rollback Notes
- Risk: callable-profile meaning for class spells is interpreted too loosely.
  Rollback: keep the change strictly tied to `MethodInspector`'s existing
  callable-object semantics.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T13:31:00Z
  TYPE: MEASURE
  CLAIM: The class-plus-callable AI profile default is landed and green. The
    strategy change was as narrow as expected: class spells still build
    `class_profile`, and they now also build `callable_profile` by default
    through the existing `_inspect_callable(...)` path. The focused strategy
    and profile tests passed after updating the class-spell strategy test to
    reflect the richer default.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py:77-80
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py:8-110
  - command:python -m py_compile src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py
  - command:python -m pytest -q tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py
  IMPACT: The AI profile now carries the richer spell-facing subprofile set by
    default for class-backed spells, which makes it more useful to the later
    view ACL work without inventing a new profile family.
  NEXT: return to the view-ACL design and decide how much of
    `class_profile` / `callable_profile` should be visible by default.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T13:25:00Z
  TYPE: FACT
  CLAIM: The current live AI profile contract is explicit: class spells produce
    `class_profile` and leave `callable_profile` empty, while method/lambda and
    other callable non-class spells produce `callable_profile`. This is not
    just inferred from code; it is also asserted by the focused AI profile
    strategy tests. Since `MethodInspector` already supports generic callables,
    the requested change is mechanically straightforward: class spells can also
    be inspected as callables without inventing a second inspector type.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py:71-100
  - src/melder/spellbook/spell_crafter/spell_examiner/inspectors/method_inspector.py:8-202
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py:1-346
  IMPACT: The main impact of this change is contract/test drift, not wider
    runtime breakage. The current focused tests will need to be updated to
    reflect the richer default class-spell AI profile.
  NEXT: patch the strategy so class spells also populate `callable_profile`,
    then update and rerun the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to make class-backed AI profiles include both class and
callable subprofiles by default.
