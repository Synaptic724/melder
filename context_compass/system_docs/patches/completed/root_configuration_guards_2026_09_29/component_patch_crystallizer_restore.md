# component_patch_crystallizer_restore

## Metadata
- Patch ID: root_configuration_guards_2026_09_29
- Status: active (stage 1 withdrawn; stage 4 changed for M2)
- Owner: user (agent melder_0)
- Created: 2026-09-29T23:43:57Z
- Updated: 2026-09-30T00:19:44Z

<!-- BEGIN ENTRY: "RestoreEngine stage 1: sealed regime" -->
## Before
- Stage 1 skips the recorded root configuration only when `aether.configured` is True. The configuration a first
  frame seals (defaults, frozen) leaves `configured` False, so stage 1 installs the recorded configuration into a
  world whose regime is already sealed - silently misreporting it when the recorded regime differs.
  EVIDENCE: src/melder/crystallizer/crystal_loader_system/restore_engine.py:1340-1394.

## After
- When frames exist and the recorded `process_wide_unique_spell_ids` differs from the live installed
  configuration's (the sealed regime), stage 1 records shortfall `live_aether_regime_sealed_recorded_payload_skipped`
  and applies nothing. Matching regimes keep today's behaviour.

## Validation Expectations
- A world with a frame and a recorded per-frame payload reports the shortfall and does not raise.
## Withdrawn (2026-09-29T23:55:15Z)
- The pre-check was implemented and removed again: the AetherCrystal payload records only the logger half
  (`channel_logger_activation_enabled` and two presence flags), never `process_wide_unique_spell_ids`, so
  `AetherConfiguration.from_recorded_payload` always rebuilds the default regime (True). A live Aether that stage 1
  may configure (`configured` False) has sealed that same default, so stage 1 cannot meet a mismatch and the guard
  would be dead code. restore_engine.py is unchanged. A non-regression test covers restoring into a live world whose
  first frame sealed the regime.
  EVIDENCE: src/melder/aether/aether_configuration.py:872-920 (twin payload),
  src/melder/aether/aether_configuration.py:421-485 (reload).
- Separate finding, not fixed here: because the regime is not recorded, a world recorded under per-frame spell ids
  restores under process-wide ids.
<!-- END ENTRY: "RestoreEngine stage 1: sealed regime" -->

<!-- BEGIN ENTRY: "RestoreEngine stage 4: active live Nexus" -->
## Before
- `_replay_nexus` reloads the recorded Nexus configuration into a fresh object and calls
  `Nexus().activate(configuration)` on the hosted Nexus. On a live world whose Nexus is active that silently swapped
  the live policy. Under M2 an active Nexus refuses another configuration, so the same call would raise and the
  all-or-nothing restore would tear the world down.
  EVIDENCE: src/melder/crystallizer/crystal_loader_system/restore_engine.py:1509-1567.

## After
- Stage 4 deactivates an active Nexus first, then activates the reloaded configuration - exactly what stage 3 does
  for MutationResearch (a world-scope load replaces the world; the deactivation is a truthful recorded act). A
  recorded "disabled" state still replays enable-then-disable. No other stage changes.

## Validation Expectations
- A checkpoint with a Nexus twin restored over an active live Nexus completes, leaves the recorded policy in force
  (not the host's object) and the Nexus active; a recorded "disabled" Nexus ends inactive with the recorded policy.
  With the M2 guard but without this change both restores fail.
<!-- END ENTRY: "RestoreEngine stage 4: active live Nexus" -->
