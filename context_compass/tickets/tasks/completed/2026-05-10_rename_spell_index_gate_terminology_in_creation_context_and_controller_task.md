# Completed: 2026-05-10T12:04:09Z
# Summary: Renamed the spell-side creation-gate controller/context surface from `lineage` to `index` and validated the focused creation-gate/creation-context ring.
# Task: Rename Spell Index Gate Terminology In Creation Context And Controller

## Metadata
- Task ID: TASK-2026-05-10-rename-spell-index-gate-terminology-in-creation-context-and-controller
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:48:45Z
- Updated: 2026-05-10T10:58:09Z

## Objective
Rename the spell-side CreationGateController and CreationContext wording from
`lineage` to `index` where the key is really `spell.spell_index.id`, while
leaving real conduit-lineage semantics untouched.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the spell-side rename plan for
  `CreationGateController`, the `CreationContext*` files, and the aligned
  tests.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/synchronization/creation_gate_controller.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - focused creation-gate / creation-context tests that directly depend on the
    renamed spell-side API and fields
- DEPENDENCIES:
  - STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
  - the raw `spell_lineage` search evidence collected for the spell-side gate
    family
- EXIT_GATE: the spell-side API, field, and test surfaces use `index` wording
  consistently and the conduit-lineage half of the controller remains
  unchanged.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rename proves to collide
  with a real mutation-lineage meaning rather than a SpellIndex container key.

## Scope Boundaries
- In scope:
  - spell-side gate registry names
  - spell-side CreationContextFactory helper names
  - spell-side CreationContext / builder field names
  - direct test updates required by those renames
- Out of scope:
  - conduit-lineage gate names
  - viewer `describe_spell_lineage(...)`
  - broader SpellIndex ownership refactors
  - mutation-lineage semantics

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the bounded spell-side rename is implemented and the
  focused compile/pytest ring is green.

## Steps / Checklist
- [x] Rename the spell-side controller registry and methods from
      `spell_lineage` to `spell_index`.
- [x] Rename CreationContextFactory spell-side helpers and stored id wording
      from `lineage` to `index`.
- [x] Rename CreationContext / builder field and parameter wording for the
      spell-side gate id.
- [x] Update the focused tests and any direct callers broken by the rename.
- [x] Run focused validation for the touched source/test ring.

## Deliverables
- spell-side gate API renamed to `spell_index`
- creation-context spell-side id fields renamed to `index`
- focused test ring updated and passing

## Files / Paths Impacted
- src/melder/utilities/synchronization/creation_gate_controller.py
- src/melder/aether/conduit/meld/creation_context/creation_context_factory.py
- src/melder/aether/conduit/meld/creation_context/creation_context_builder.py
- src/melder/aether/conduit/meld/creation_context/creation_context.py
- tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py
- tests/component/melder/utilities/synchronization/test_creation_gate_component.py
- tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py
- tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py
- tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py

## Validation
- Executed:
  - `python -m py_compile src/melder/utilities/synchronization/creation_gate_controller.py src/melder/aether/conduit/meld/creation_context/creation_context_factory.py src/melder/aether/conduit/meld/creation_context/creation_context_builder.py src/melder/aether/conduit/meld/creation_context/creation_context.py tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py tests/component/melder/utilities/synchronization/test_creation_gate_component.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py tests/component/melder/utilities/synchronization/test_creation_gate_component.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py`
- Result:
  - compile validation passed
  - focused pytest ring passed (`190 passed`)

## Risks / Rollback Notes
- Risk: the rename leaks into true conduit-lineage surfaces and muddies a real
  lineage concept.
  Rollback: keep the conduit-side names unchanged and revert any accidental
  spillover immediately.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.
- [ ] No blind repo-wide rename outside the bounded spell-side gate family.

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
- DATETIME: 2026-05-10T10:48:45Z
  TYPE: FACT
  CLAIM: The rename surface is bounded and mixed exactly the way the user
    described. The spell-side half of `CreationGateController` plus the
    CreationContext gate-id helpers are still using `spell_lineage` wording
    even though the key is `spell.spell_index.id`, while the conduit-side
    lineage registry is a separate real lineage concept that must not be
    renamed.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate_controller.py:15-39
  - src/melder/utilities/synchronization/creation_gate_controller.py:683-983
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:117-219
  - user_instruction: "spell lineage in these but it should just be spell index"
  IMPACT: The implementation can stay narrow: rename only the spell-side gate
    family and aligned creation-context fields/tests, while preserving the real
    conduit-lineage branch of the controller exactly as-is.
  NEXT: patch the bounded source/test ring and validate it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T10:58:09Z
  TYPE: MEASURE
  CLAIM: The spell-side rename is now landed through the full bounded ring.
    `CreationGateController` now exposes a spell-index gate family, the
    CreationContext builder/factory/context path now carries
    `creation_gate_index_id`, the direct test callers were updated, and the
    focused compile plus pytest ring both passed.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate_controller.py:15-18
  - src/melder/utilities/synchronization/creation_gate_controller.py:683-983
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:117-256
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:57-111
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:144-220
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:458-525
  - validation_result:
    `python -m py_compile src/melder/utilities/synchronization/creation_gate_controller.py src/melder/aether/conduit/meld/creation_context/creation_context_factory.py src/melder/aether/conduit/meld/creation_context/creation_context_builder.py src/melder/aether/conduit/meld/creation_context/creation_context.py tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py tests/component/melder/utilities/synchronization/test_creation_gate_component.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py tests/component/melder/utilities/synchronization/test_creation_gate_component.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py` -> `190 passed`
  IMPACT: The mixed spell-side gate family now matches the SpellIndex model
    without altering the conduit-lineage side of the controller.
  NEXT: return the bounded rename slice for review and acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded spell-side `lineage -> index` rename for the mixed
CreationGateController / CreationContext gate family. Conduit-lineage naming
stays out of scope.
