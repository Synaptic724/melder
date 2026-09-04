# Task: Verify disposal configuration through Crystallizer reload and Nexus defaults

## Metadata
- Task ID: TASK-2026-09-04-disposal-configuration-roundtrip
- Story: STORY-2026-09-04-ordered-disposal-binding
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T22:06:16Z

## Objective
Prove the new flag and ordered book vocabulary survive existing configuration transport,
and that Nexus-created books obtain the normal False default.

## Ticket Contract
- ENTRY_GATE: Configuration task verified; route here and consume the relevant patch contract.
- EXECUTION_BOUNDARY: Configuration emission/reload tests, generic book/checkpoint carriers,
  Nexus default factory verification, and source corrections only for demonstrated propagation defects.
- DEPENDENCIES: `tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`.
- EXIT_GATE: Recorded True/False, missing-flag defaults, ordered vocabulary, and Nexus default
  creation are verified; report exact commands/results and any uncovered path.
- FAILURE_ESCALATION: Surface a real generic transport defect; do not mirror the flag into
  CrystallizerConfiguration, NexusConfiguration, or a new root-owned field.

## Scope Boundaries
- In scope: configuration values and their existing transport APIs.
- Out of scope: resolved SpellCrystal list sorting, full world replay, custom Nexus rich-config API.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Configuration mapping identified a distinct cross-component verification slice.

## Required Reading and Evidence
Read discovery Configuration Change Map and relevant test architecture/components first.
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:258-481`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:559-652`
- `src/melder/crystallizer/crystals/spellbook_crystal.py:92-264`
- `src/melder/crystallizer/persistence/persistence_profile.py:1028-1306`
- `src/melder/crystallizer/persistence/persistence_crystal.py:78-184`
- `src/melder/crystallizer/persistence/persistence_crystal.py:345-451`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1822`
- `src/melder/nexus/nexus_frame_configuration.py:334-349`
- `src/melder/nexus/nexus_frame_manager.py:994-1030`
- `src/melder/nexus/nexus_frame_builder.py:219-268`
- `tests/unit/melder/aether/test_configuration_reload_lanes.py:31-89`
- `tests/unit/melder/aether/test_nexus_frame_configuration.py:178-195`

## Steps / Checklist
- [ ] Verify True and False are preserved by configuration emission into SpellbookCrystal.
- [ ] Carry a non-alphabetical method list through book twin, checkpoint cached item, and reload.
- [ ] Verify absent flag in an older configuration payload yields False with honest accounting.
- [ ] Verify reload seals the config before restored binds and preserves explicit recorded True.
- [ ] Verify NexusFrameConfiguration.to_spellbook_configuration inherits False.
- [ ] Reuse generic transport as found; change only an evidenced failing handoff if necessary.
- [ ] Record results and pass configuration evidence to the persistence story.

## Deliverables
Focused transport/default tests and recorded results, with no duplicated policy fields.

## Files / Paths Impacted
- `tests/unit/melder/aether/test_configuration_reload_lanes.py`
- `tests/unit/melder/aether/test_nexus_frame_configuration.py`
- Focused book/checkpoint transport test in the existing Crystallizer test hierarchy.
- Configuration owner implementation only if the tests expose a concrete default/reload defect.
- Generic carrier and Nexus source files are read-only unless a specific defect is established.

## Validation
- Not run; ticket only. Use a verified supported interpreter.
- Check both non-default True and explicit False, not just an empty/default payload.
- Assert method list order and flag values after the round trip, then assert sealed behavior.
- A default Nexus factory test does not establish custom priority selection through its builder;
  that builder currently exposes no rich Spellbook configuration input.

## Risks / Rollback Notes
Default seeding can make reload report a value as recorded when it was supplied locally.
Validate diagnostic accounting alongside values. Do not confuse configuration transport
with successful resolved-method replay; the latter is a later task.

## Applicable Anti-Patterns
- [ ] No unnecessary per-flag code in generic crystal/checkpoint containers.
- [ ] No custom Nexus API expansion or defensive snapshot redesign.

## Done Checklist
- [ ] Transport/default assertions and exact results recorded.
- [ ] Shared configuration test edits coordinated with the configuration task.
- [ ] Dependent replay task linked; owner acceptance precedes closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none yet
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: any temporary probe artifacts are explicitly registered before use

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: book payloads, reload, Nexus defaults
- IF_UNKNOWN: none

## Noting Behavior
Record tested boundaries and gaps separately, with source pointers and one NEXT action.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Inspected generic book payloads already carry bools/lists; tests must prove the new flag.
  EVIDENCE:
  - `src/melder/crystallizer/crystals/spellbook_crystal.py:240-264`
  - `src/melder/nexus/nexus_frame_configuration.py:334-349`
  IMPACT: No independent root-level priority setting is justified by the inspected code.
  NEXT: After configuration implementation, add recorded True/False reload cases first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:01:28Z
  TYPE: FACT
  CLAIM: Configuration freeze emits scalar booleans and ordered list values; SpellbookCrystal
    carries that map, profile capture invokes describe without per-property filtering, and
    PersistenceCrystal cached/replay forms carry the nested payloads. RestoreEngine reloads
    and seals configuration before active binds. Nexus-managed construction creates an
    ordinary defaults-loaded configuration. Preset books share the existing config object.
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:258-396`
  - `src/melder/crystallizer/crystals/spellbook_crystal.py:92-264`
  - `src/melder/crystallizer/persistence/persistence_profile.py:1028-1306`
  - `src/melder/crystallizer/persistence/persistence_crystal.py:78-184`
  - `src/melder/crystallizer/persistence/persistence_crystal.py:345-451`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1820`
  - `src/melder/nexus/nexus_frame_configuration.py:334-349`
  - `src/melder/nexus/nexus_frame_manager.py:994-1030`
  - `src/melder/aether/spellbook/spellbook.py:6230-6267`
  IMPACT: No duplicate root flag or per-key branch is needed in the inspected carriers.
    Normal defaults reach Nexus, while shared/preset configurations carry explicit values.
    Verify boolean/list round trips and backfill reporting after owner configuration changes.
    No runtime round trip was run in this information-gathering pass.
  NEXT: After configuration implementation, test emitted True/False and ordered vocabulary
    through cached-item reload, plus default Nexus construction and shared configuration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This verifies configuration, not full Spell disposal replay. The original mapper ran no
runtime tests. Keep False defaults and accurate backfill reporting, and defer final-list
sorting/staged/graft behavior to the crystal replay task.
