# component_patch_meld_resolution_runtime

## Metadata
- Patch ID: injected_provider_first_direct_meld_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: @NOW@
- Updated: @NOW@

<!-- BEGIN ENTRY: "Meld: deferred lane routing" -->
## Before
- `_ensure_runtime_resolution_ready` runs `_run_deferred_resolution_phases_for_target_spell` (8-11) for every
  flagged spell. For a spell with no Phase 5 root blueprint the plan phases are skipped
  (`_is_spell_plan_phase_eligible`), the lane still marks the spell complete, and the context build then raises.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:966-1019
  - src/melder/aether/spellbook/spellbook_creation_system.py:1757-1825
  - src/melder/aether/spellbook/spellbook_creation_system.py:2740-2779
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:644-684

## After
- Inside the same rebuild window and spell lock, a flagged spell that is neither an existing creation nor its
  current Phase 5 root (`SpellCompilerSystem.is_current_spell_phase5_root`) runs the full target pass
  `_run_resolution_phases_for_target_spell` (5-11) and must then read resolution-valid for the conduit
  (`_get_resolution_validity`), else SpellbookValidationError. Every other flagged spell keeps the 8-11 pass.
- Bookkeeping is unchanged: on success complete and not required; on failure required stays set, complete is
  False, `_door_epoch` is bumped and the error re-raised.
- The ConduitMeld and SpellSpaceMeld doors and `_execute_admitted` already call the lane while the flag is set;
  they do not change.

## Interface Deltas
- None public; private helpers on Meld only.

## Validation Expectations
- Unit: a flagged spell without a Phase 5 root runs the full pass (not 8-11) and completes; an existing creation
  keeps 8-11; a full pass that leaves the verdict invalid raises SpellbookValidationError and keeps the flag; a
  full-pass exception keeps the flag and bumps the epoch. The two deferred-lane tests make their spell a Phase 5
  root (they pinned the 8-11 route for a spell without one).
- Component: the regression file, the SpellSpace door included.
<!-- END ENTRY: "Meld: deferred lane routing" -->
