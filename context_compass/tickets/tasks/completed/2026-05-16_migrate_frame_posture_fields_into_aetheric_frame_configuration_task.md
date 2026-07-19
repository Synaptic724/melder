# Task: Migrate Frame Posture Fields Into AethericFrameConfiguration
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed after the owner move slice was absorbed into the completed frame-posture migration lane.


## Metadata
- Task ID: TASK-2026-05-16-migrate-frame-posture-fields-into-aetheric-frame-configuration
- Story: STORY-2026-05-16-implement-explicit-frame-configuration-and-local-config-split
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T12:22:59Z
- Updated: 2026-05-16T15:47:45Z

## Objective
Move the frame-global posture fields out of `SpellbookConfiguration` and make
`AethericFrameConfiguration` the runtime owner for:
- `system_state`
- `ai_native_enabled`
- `rift_enabled`
- `shared_framewide_spellbook_configuration`

Keep `SpellbookConfiguration` as the local rich-config owner and frame-posture
authoring surface.

## Ticket Contract
- ENTRY_GATE: the first shared-config mechanics slice is landed and the user
  explicitly asked to move the posture fields over now that the owner model is
  clearer.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/spellbook/configuration/spellbook_configuration.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/spellbook/spell_crafter/spell_crafter.py`
  - `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
  - `src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py`
  - focused unit/component/integration tests for configuration, Spellbook,
    Conduit, and Nexus frame posture
- DEPENDENCIES:
  - `tickets/tasks/2026-05-16_implement_shared_framewide_spellbook_configuration_first_slice_task.md`
- EXIT_GATE: frame-global posture fields no longer live in the rich
  `SpellbookConfiguration` property bag, runtime consumers read them from
  `AethericFrameConfiguration`, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if a remaining runtime
  consumer proves one of those fields still belongs in `SpellbookConfiguration`.

## Scope Boundaries
- In scope:
  - field-owner move
  - runtime consumer reroutes
  - focused test expectation rewrites
- Out of scope:
  - broader override/local field migration
  - new public APIs
  - unrelated Nexus/AR feature work

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the posture-owner move is landed and the focused plus
  adjacent validation rings are green.

## Steps / Checklist
- [x] Remove frame-global posture fields from the `SpellbookConfiguration`
      property bag.
- [x] Keep `SpellbookConfiguration` as the frame-posture authoring surface.
- [x] Reroute runtime reads to `AethericFrameConfiguration`.
- [x] Update focused tests to the new owner.
- [x] Run focused and adjacent validation.

## Validation
- Executed:
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/integration/melder/spellbook/test_spellbook_integration_core.py tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py tests/unit/melder/aether/test_nexus_frame_configuration.py tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py`
- Result:
  - focused + adjacent posture-owner ring passed (`522 passed`)

## Notes
- DATETIME: 2026-05-16T12:22:59Z
  TYPE: MEASURE
  CLAIM: The frame-global posture owner move is landed. `SpellbookConfiguration`
    no longer stores `system_state`, `ai_native_enabled`, `rift_enabled`, or
    `shared_framewide_spellbook_configuration` in its rich property bag. It now
    authors those values through an associated `AethericFrameConfiguration`
    object, and the runtime consumers that actually care about frame posture
    (`Spellbook` dynamic transaction gating, conjure policy checks, Conduit
    dynamic environment setup, and spell-crafter/occurrence-plan/contract-provider
    dynamic-mode decisions) now read from frame posture instead of the rich
    local config bag.
  EVIDENCE:
  - src/melder/aether/aetheric_frame_configuration.py:13-320
  - src/melder/spellbook/configuration/spellbook_configuration.py:13-1069
  - src/melder/spellbook/spellbook.py:191-198
  - src/melder/spellbook/spellbook.py:2061-2074
  - src/melder/spellbook/spellbook_creation_system.py:398-425
  - src/melder/aether/conduit/conduit.py:961-973
  - src/melder/spellbook/spell_crafter/spell_crafter.py:970-976
  - src/melder/spellbook/spell_crafter/spell_crafter.py:1097-1103
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1196-1199
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:76-83
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/integration/melder/spellbook/test_spellbook_integration_core.py tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py tests/unit/melder/aether/test_nexus_frame_configuration.py tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py` -> `522 passed`
  IMPACT: The owner boundary is materially clearer now. The rich config bag is
    local-only, and frame posture is a real first-class runtime object instead
    of duplicated config state hidden behind `get_property(...)`.
  NEXT: return this slice for review, then move the remaining intended local
    fields only when you want the next cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the field-owner migration that makes `AethericFrameConfiguration`
the runtime owner for the permanent frame posture fields.

