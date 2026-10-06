# component_patch_aether_root_configuration

## Metadata
- Patch ID: per_frame_spell_worlds_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T17:18:12Z
- Updated: 2026-09-30T17:18:12Z

<!-- BEGIN ENTRY: "Aether: regime in force" -->
## Before
- The regime lives only in the private `_process_wide_unique_spell_ids` (sealed when the first frame is born) and in
  the installed configuration; the first frame installs frozen defaults without setting `configured`, so no public
  read says which regime is in force.
  EVIDENCE: src/melder/aether/aether.py:2543-2605.

## After
- `Aether.process_wide_unique_spell_ids` (read-only): once any frame exists, the sealed value; before that, the
  installed configuration's value (the one the next first frame seals); True when nothing is installed.
- Lock-free point-in-time read, like the frame lookups: the seal is written before the first frame is inserted, both
  under the Aether lock. Raises RuntimeError when Aether is cleaned; a drifted configuration value raises the
  configuration's own TypeError.

## Validation Expectations
- Component: True on a fresh Aether; follows an installed configuration before the first frame; equals the sealed
  value after it; a configuration replaced before the first frame changes the answer; cleaned Aether raises.
<!-- END ENTRY: "Aether: regime in force" -->

<!-- BEGIN ENTRY: "AetherConfiguration: twin and reload" -->
## Before
- `emit_configured_twin_when_recording` records channel_logger_activation_enabled and two logger presence flags.
- `from_recorded_payload` reloads the logger flag only, so a rebuilt configuration always carries the default regime
  (True) and the absent regime is not reported.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:872-920
  - src/melder/aether/aether_configuration.py:421-485

## After
- The twin payload adds "process_wide_unique_spell_ids" (the configuration's value).
- The reload lane applies a recorded regime before it freezes; a payload without it keeps the default (True) and
  lists "process_wide_unique_spell_ids" under "missing".

## Validation Expectations
- Unit: a payload with the regime False reloads False, frozen; an empty payload lists both keys missing; a full
  payload lists nothing missing (the two existing reload tests move to this contract).
- Integration: with recording on, activating a per-frame configuration records the regime False in the Aether twin.
<!-- END ENTRY: "AetherConfiguration: twin and reload" -->

<!-- BEGIN ENTRY: "AetherUtilitySystem: root twin re-emission" -->
## Before
- Every mutating utility verb re-emits the Aether twin from the live logger truth; replace-on-emit keeps that twin,
  so any regime field another emitter recorded would be erased.
  EVIDENCE: src/melder/aether/aether_utility_system.py:204-256.

## After
- The re-emitted payload adds the regime read from the Aether, but only when the Aether singleton is initialized and
  not cleaned (Aether marks itself cleaned before it tears frames and the crystallizer down, and `Aether()` returns
  that husk until teardown ends). Otherwise the key is omitted and a restore reports it missing.

## Validation Expectations
- Integration: after `Aether.activate` of a per-frame configuration (which drives the utility verbs), the recorded
  twin still carries the regime False.
<!-- END ENTRY: "AetherUtilitySystem: root twin re-emission" -->
