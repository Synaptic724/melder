# Task: Implement Crystallizer Configuration And Singleton

## Metadata
- Task ID: TASK-2026-05-04-implement-crystallizer-configuration-and-singleton
- Story:
- Epic: EPIC-2026-05-04-implement-crystallizer-configuration-and-activation
- Status: review
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-04T22:18:15Z
- Updated: 2026-05-04T22:24:52Z

## Objective
Implement the first crystallizer root/config slice:
- `CrystallizerConfiguration`
- singleton `Crystallizer`
- explicit configured/activated gates

## Ticket Contract
- ENTRY_GATE: the user explicitly requested this configuration/singleton slice.
- EXECUTION_BOUNDARY:
  - `src/melder/crystallizer/configuration/crystallizer_configuration.py`
  - `src/melder/crystallizer/configuration/builder.py`
  - `src/melder/crystallizer/crystallizer.py`
  - focused tests for this slice
- DEPENDENCIES:
  - Spellbook/Nexus configuration patterns
  - crystallizer artifact stack
- EXIT_GATE: config/root behavior is real and directly testable.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the slice requires a larger
  identity redesign than a bounded first implementation pass.

## Scope Boundaries
- In scope:
  - config object
  - fluent config methods
  - singleton root
  - configured/activated checks
  - focused tests
- Out of scope:
  - full loader refactor
  - broad caller migration
  - persistence implementation

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the focused config/root slice is implemented and the new
  test ring is green.

## Steps / Checklist
- [x] Read the relevant configuration/root patterns from source.
- [x] Implement `CrystallizerConfiguration`.
- [x] Implement singleton `Crystallizer`.
- [x] Add focused tests.
- [x] Run targeted validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `CrystallizerConfiguration`
- singleton `Crystallizer`
- focused configuration/activation tests

## Files / Paths Impacted
- src/melder/crystallizer/configuration/crystallizer_configuration.py
- src/melder/crystallizer/configuration/builder.py
- src/melder/crystallizer/crystallizer.py
- tests/unit/melder/crystallizer/test_crystallizer_configuration.py
- tests/unit/melder/crystallizer/test_crystallizer.py

## Validation
- Executed:
  - `python.exe -m py_compile src/melder/crystallizer/configuration/crystallizer_configuration.py src/melder/crystallizer/configuration/builder.py src/melder/crystallizer/crystallizer.py tests/unit/melder/crystallizer/test_crystallizer_configuration.py tests/unit/melder/crystallizer/test_crystallizer.py`
  - `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_crystallizer_configuration.py tests/unit/melder/crystallizer/test_crystallizer.py`
  - `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_spell_crystal.py tests/unit/melder/crystallizer/test_synthetic_module.py`
- Result:
  - compile validation passed
  - config/root ring passed (`10 passed`)
  - existing crystallizer unit compatibility ring passed (`172 passed`)

## Risks / Rollback Notes
- Risk: config shape gets overbuilt before the loader actually consumes it.
  Rollback: keep only the first policy field and core activation semantics.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
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
- DATETIME: 2026-05-04T22:18:15Z
  TYPE: PLAN
  CLAIM: The first implementation slice should mirror the repo's established
    configuration and singleton patterns instead of inventing a custom
    crystallizer shape. That means a mutable-then-freeze config object with a
    fluent API and a singleton root that stays unusable until configured and
    activated.
  EVIDENCE:
  - src/melder/spellbook/configuration/configuration.py
  - src/melder/aether/nexus/configuration/nexus_configuration.py
  - src/melder/aether/nexus/nexus.py
  IMPACT: The resulting root/config slice will feel native to the repo and
    gives later loader work a stable policy home.
  NEXT: implement the code and validate the configured/activated gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T22:24:52Z
  TYPE: MEASURE
  CLAIM: The first crystallizer root/config slice is now landed. The empty
    crystallizer config/root files now contain a real `CrystallizerConfiguration`
    with mutable property bag, validation, freeze/finalize, activation, and
    fluent `with_user_source_root_paths(...)`; a thin
    `CrystallizerConfigurationBuilder`; and a singleton `Crystallizer` root with
    explicit configured/activated gates plus a `create_spell_crystal(...)`
    helper that injects the configured source-root policy into crystal
    construction.
  EVIDENCE:
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:1-285
  - src/melder/crystallizer/configuration/builder.py:1-75
  - src/melder/crystallizer/crystallizer.py:1-264
  - tests/unit/melder/crystallizer/test_crystallizer_configuration.py:1-71
  - tests/unit/melder/crystallizer/test_crystallizer.py:1-114
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_crystallizer_configuration.py tests/unit/melder/crystallizer/test_crystallizer.py` -> `10 passed`
  IMPACT: Crystallizer policy now has an explicit home outside
    `SpellCrystal.__init__`, and the loader-facing root can require real config
    activation instead of relying on ad hoc constructor parameters forever.
  NEXT: decide whether the next migration step is pushing current callsites
    through `Crystallizer.create_spell_crystal(...)` or widening config beyond
    the first user-source-root field.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first crystallizer configuration/root implementation slice.
