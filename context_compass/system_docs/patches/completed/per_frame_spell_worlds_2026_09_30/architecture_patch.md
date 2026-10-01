# architecture_patch

## Metadata
- Patch ID: per_frame_spell_worlds_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T17:18:12Z
- Updated: 2026-09-30T17:18:12Z

## Patch Scope and Non-Goals
- Objective: a world recorded under per-frame spell ids (`process_wide_unique_spell_ids=False`) restores as it was
  recorded. (A) The Aether record carries the spell-id regime, and restore installs it before any frame is born or
  says plainly why it cannot. (B) The record keeps one spell crystal per frame for a spell id, so the same class
  bound in several frames survives recording and restore, and every reader of spell custody follows.
- Non-goals: MutationResearch residence and journals stay keyed by spell id (code identity, which every frame's copy
  shares); process-wide worlds keep their record keys; a live world's regime is never migrated; the investigation's
  option C (flagging a displaced crystal) is dropped because nothing is displaced any more.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Aether Singleton (Global Runtime) | modify (additive) | no public read of the regime in force | none |
| Aether Root Configuration Assembly | modify | the Aether twin carried only the logger half | Aether |
| Logging and Initialization Helpers (AetherUtilitySystem) | modify | its twin re-emission would erase the regime | Aether |
| Crystallizer Root, Persistence Record, And Module-World Surfaces | modify | custody keyed by spell id loses a frame's copy; stage 1 and stage 6 read one copy per id | Aether |
| Spellbook Core (Binding and Conjure) | modify (call sites) | removal and park/promote emissions must name their frame | Crystallizer |

## Interface and Boundary Deltas
- Additions: `Aether.process_wide_unique_spell_ids` (read-only bool); `SpellCrystal.frame_name`,
  `SpellCrystal.custody_key`, `SpellCrystal.compose_custody_key(spell_id, frame_name)` and
  `SpellCrystal.spell_id_of_custody_key(custody_key)`; `describe()` gains "frame_name" and "custody_key".
- Additive keyword parameters: `Crystallizer.emit_spell_removed(spell_id, frame_name=None)`,
  `Crystallizer.emit_spell_activity(spell_id, active, frame_name=None)`,
  `Crystallizer.get_spell_crystal(spell_id, frame_name=None)` and `SpellCrystal(..., per_frame_custody=False)`.
  Under per-frame ids the two emit verbs raise ValueError when no frame is given.
- Record shape: the AetherCrystal configuration_payload gains "process_wide_unique_spell_ids". Spell custody is keyed
  by the spell id under process-wide ids and by "<spell_id>@<frame_name>" under per-frame ids - journal keys,
  checkpoint and formation payload keys, `describe_spell_crystals()` keys. spell_activity and spell_removed payloads
  carry "spell_id" (the bare id) and "custody_key". RecordVersion.CURRENT goes from 3.0.0 to 4.0.0.
- Restore: stage 1 installs the recorded regime, or reports or refuses when the live regime is already fixed; stage 6
  keys bind order, member-index lookup and spell translation per Book; a formation retarget re-keys custody.
- New shortfall reasons: `recorded_per_frame_ids_restored_under_process_wide_ids`,
  `recorded_process_wide_ids_restored_under_per_frame_ids`. New refusal (RuntimeError before anything is built): the
  record binds one spell id in two frames while the live regime is process-wide.

## Cross-Component Invariants
- A custody key is unique in a record: a spell id is unique per frame and links and transfers never cross frames,
  so (frame, spell id) is unique under both regimes, and under process-wide ids the spell id alone is.
- A custody entry's spell id is its payload "id"; a key is parsed only to name the spell of a tombstone whose
  crystal is already gone.
- A reader given a spell id without a frame answers the first matching key in sorted order; a reader that knows the
  frame or the Book answers that copy.
- Every Aether twin emission carries the regime in force, so a later twin never erases it.
- Recording changes no runtime behaviour (R-A covenant); crystallizer-off worlds are byte-identical.

## Migration Order
1. A (0.2.8213): the Aether property, both twin payloads and the reload lane, stage 1 install or shortfall.
2. B (0.2.8214): the crystal key, the record, the facade verbs and spellbook call sites, restore's per-Book helpers
   and the stage 1 refusal, the retarget, the impact read, RecordVersion 4.0.0.
Docs, graph, release note and the asset/bundle rebuild follow both.

## Rollback
- B reverts as one unit; its record shape is fenced by the major. A reverts alone: an older reload lane ignores the
  extra payload key.

## Ticket Coverage Matrix
| patch section | ticket |
|---|---|
| all | tickets/tasks/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md |
