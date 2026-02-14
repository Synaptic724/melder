# Phase 7 Investigation (Change Control)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase07-change-control-investigation

## Scope
Analyze change-control wiring, component_of index rebuild, and revalidation hooks.

## Key Questions
- How does Phase 7 wire change-control state and revalidation?
- What inputs from Phase 5 are required?
- How are dirty roots tracked and revalidated?

## Evidence
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_change_control
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter._ensure_change_control_ready
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_root_blueprints (change-control wiring)
- src/melder/aether/dev_ops/change_control_manager/change_control_manager.py: ChangeControlManager.rebuild_component_of
- src/melder/aether/dev_ops/change_control_manager/change_control_manager.py: ChangeControlManager.set_revalidator
- src/melder/aether/dev_ops/change_control_manager/change_control_manager.py: ChangeControlManager.revalidate_dirty_roots
- src/melder/aether/dev_ops/change_control_manager/change_control_manager.py: ChangeControlManager.notify_spell_changed

## Findings
- Phase 7 is a wiring phase: run_phase_change_control delegates to _ensure_change_control_ready and performs no additional logic.
- _ensure_change_control_ready retrieves ChangeControlManager for the frame and, when Phase 5 root blueprints exist, rebuilds the component_of index.
- If no revalidator is registered, Phase 7 installs a revalidator that scans spells via SpellbookScanner, maps root ids to Spell instances, and runs SpellCrafter.run_all_phases for each dirty root.
- Phase 5 also wires change control: run_phase_root_blueprints rebuilds component_of and registers a revalidator. Phase 7 therefore duplicates wiring with slightly different error handling.
- ChangeControlManager.rebuild_component_of builds the component_of index from root blueprints and clears dirty tracking state.
- ChangeControlManager.notify_spell_changed marks a spell dirty, updates dirty roots, and marks dependency change on SpellSystemState for affected roots.
- ChangeControlManager.revalidate_dirty_roots runs the registered revalidator outside the lock and clears dirty roots when the callback succeeds.

## Risks / Concerns
- Change-control wiring happens in both Phase 5 and Phase 7; differing error handling or ordering could cause inconsistent revalidator behavior.
- Revalidation uses run_all_phases, which includes Phase 11; this can be expensive and may fail if Phase 11 assumptions are not met.

## Unknowns
- Call sites for notify_spell_changed / notify_provider_changed are not mapped yet. Investigate who signals dirty roots and under what conditions.
- Whether component_of should be rebuilt in Phase 5 or Phase 7 (or both) is a design decision.

## Next Steps
- Trace notify_spell_changed call sites to document change-control triggers.
- Decide whether Phase 5 or Phase 7 should own revalidator registration to avoid duplication.
