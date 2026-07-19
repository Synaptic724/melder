# Architecture Patch: MutationResearch restore build stage

- Patch ID: mr_restore_build_stage_2026_07_11
- Ticket: EPIC-2026-07-11-mutation-research-restore-build-stage
  (authored by mutation_0 as the twin-over handoff; melder_0 executes)
- Status: active

## Objective
Convert `_replay_mutation_research` from an ordered REPORT stage into a
BUILD stage mirroring `_replay_nexus`: a checkpointed world that
contained research unfolds WITH its research. MR-side seams are all
landed and owner-run green (Phase-B twin: activated/configuration_payload/
composition_payload; `load_recorded_composition`;
`activate(hydrate_from_record)`; `describe_configuration_payload`) -
this patch consumes them and never edits MR internals, with ONE
exception owned by the reload-lane law: the config gains
`load_recorded_dictionary`.

## Non-goals
- No MR internals edits (root/research_set/diff/twin are mutation_0's;
  seam mismatches go to his mailbox, never engine-side reshaping).
- No formation-scoped MR (world-scope root; conduit/frame loads
  reclassify like frame_posture).
- The two open owner dials (journal window bound, snapshot-ring
  persistence) are additive mutation_0-side changes; nothing here moves.

## Interface Deltas
- S1 MutationResearchConfiguration.load_recorded_dictionary(recorded):
  reload-lane law verb - with_defaults backfill floor, recorded keys
  overwrite via set_property (single bool key: no coercion helper),
  per-key {"rejected", "backfilled"} outcome, SEALS VIA activate() on
  return (freeze + activated + the config's own emission factor: the
  re-emission mid-replay is the Nexus-precedent re-recording covenant;
  replace-on-emit means the root's later composition re-emission
  supersedes it in the fresh profile).
- S2 engine `_replay_mutation_research` (report -> build), canonical
  slot unchanged (Aether|Utility -> Crystallizer -> MR -> Nexus):
  no twin = NO-OP; folded "cleaned" = shortfall, no rebuild; else reload
  verb over configuration_payload (rejected/backfilled -> per-key
  shortfalls) -> root via Aether()._get_mutation_research() (hosted
  accessor, never free-constructed) -> configure(...) ->
  activate(hydrate_from_record=False) (engine owns FOLDED truth; the
  fresh active profile is empty mid-replay) ->
  load_recorded_composition(composition_payload); disabled later-wins =
  activate-then-deactivate (recorded history, Nexus precedent);
  pre-Phase-B (no composition key) = config-only rebuild + shortfall
  "composition_not_recorded_pre_phase_b"; built_stack push +
  record_built("mutation_research"); BOTH
  `*_recorded_not_restored_first_cut` shortfalls DELETED.
- S3: (a) NEW preflight MRCompositionStrategy (9th default row):
  composition payload parses + per-set organization/residence agreement
  (lane-held SHAs resident, residences point at described lanes);
  warnings, blocker only on unparseable payload; (b) LoadAdmission
  scope adjudication treats mutation_research findings as
  expected_for_scope on conduit/frame loads; (c) round-trip integration
  test (declare -> checkpoint -> fresh boot -> load_checkpoint ->
  research present + journal sequences continue + later activate()
  hydration NO-OPs on the non-virgin registry).

## Migration Order
S1 verb -> S2 stage -> S3 preflight/adjudication/round-trip -> tests.

## Rollback
Stage reverts to the two first-cut shortfalls; the reload verb is
additive; the preflight row unregisters cleanly.
