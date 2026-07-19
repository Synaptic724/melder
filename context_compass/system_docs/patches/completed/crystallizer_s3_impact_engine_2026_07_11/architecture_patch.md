# Architecture Patch: S3 impact engine (blast radius over manifests)

- Patch ID: crystallizer_s3_impact_engine_2026_07_11
- Ticket: STORY-2026-07-11-impact-engine (epic:
  crystallizer_v3_horizon_iteration, tranche S3 - final story)
- Status: active

## Objective
A READ-ONLY view that turns the custody manifests into blast-radius
answers: which spells a module reaches (transitively), what has drifted
on disk since the world sealed, and what that drift touches. The record
already carries every edge (module_targets, per-module direct-dependency
maps, bind-time fingerprints, S2 retained sources); S3 only indexes and
answers - it never mutates or reshapes the record.

## Non-goals
- No record mutation, no twin escape (dict-only surfaces).
- No live-runtime inspection (the record is the input; the drift check
  reads DISK, never runtime objects).
- No scheduling/watching; one-shot views the caller invokes.

## Interface Deltas (all additive)
- PersistenceProfile.describe_spell_crystals(): {spell_id: crystal
  describe() + "custody_state": "active"|"inactive"} across both custody
  maps; PersistenceSystem.describe_spell_crystals() active-profile
  passthrough.
- NEW crystal_analysis/impact_engine.py: ImpactEngine (Cleanable) over
  the detached custody map. Construction builds two reverse indexes:
  module -> carrying spells; module -> importing modules (union of
  per-crystal module_to_direct_dependencies, reversed). Verbs:
  spells_touching_module, blast_radius_of_module (transitive closure:
  modules/spells/spellbooks/custody_states; unknown module -> honest
  empty + "unknown_module": True), blast_radius_of_spell (radius of the
  spell's root module; unknown sha honest), describe_source_drift
  (per recorded fingerprint: read_text/utf-8 re-hash - the CRLF-safe
  custody read - -> unchanged|drifted|absent + radius per non-unchanged
  module), describe().
- Crystallizer.analyze_impact(module_name=None, spell_id=None):
  activation-gated facade; module view, spell view, or (both None) the
  full drift report; always detached dicts.

## Migration Order
1. read seam -> 2. engine -> 3. facade -> 4. tests (unit closure/drift +
facade smoke).

## Rollback
All additive; deleting the engine + seam + verb restores byte-identical
surfaces.
