# component_patch_crystallizer_record

## Metadata
- Patch ID: per_frame_spell_worlds_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T17:18:12Z
- Updated: 2026-09-30T17:18:12Z

<!-- BEGIN ENTRY: "SpellCrystal: frame and custody key" -->
## Before
- A crystal carries the spell id, spellbook id and bind signature; no frame. The record keys it by `crystal.id`.
  EVIDENCE: src/melder/crystallizer/crystals/spell_crystal.py:116-345.

## After
- New slots `_frame_name` (read from `spell.aetheric_frame`) and `_custody_key`; constructor keyword
  `per_frame_custody: bool = False`. The key is the spell id, or "<spell_id>@<frame_name>" when `per_frame_custody`.
- Statics `compose_custody_key(spell_id, frame_name)` and `spell_id_of_custody_key(custody_key)` (split on the first
  "@"; a SHA256 id holds no "@"). Properties `frame_name` and `custody_key`; `describe()` adds both. Cleanup deletes
  both slots.

## Validation Expectations
- Unit: default key equals the id; per-frame key composes; statics round-trip, including a frame name that holds
  "@"; describe carries frame_name and custody_key. Test spell doubles gain `aetheric_frame`.
<!-- END ENTRY: "SpellCrystal: frame and custody key" -->

<!-- BEGIN ENTRY: "PersistenceProfile and PersistenceSystem: custody by key" -->
## Before
- Two maps keyed by spell id with replace-on-emit; activity and removal address the spell id; the journal and the
  captured payloads use it; `get_spell_crystal` is an exact lookup; `capture_index_graft` finds a member by id.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:334-434
  - src/melder/crystallizer/persistence/persistence_profile.py:744-926
  - src/melder/crystallizer/persistence/persistence_profile.py:1149-1182

## After
- Recording keys by `crystal.custody_key` (replace-on-emit per key); `record_spell_activity(custody_key, active)` and
  `remove_spell_crystal(custody_key)` address the key; journal entries carry it.
- spell_activity and spell_removed payloads carry "spell_id" (bare) and "custody_key".
- `get_spell_crystal(spell_id, frame_name=None)`: with a frame, that frame's key first; then the exact key (a bare id
  or a full custody key); without a frame, the first "<spell_id>@..." key in sorted order, active before inactive;
  KeyError otherwise. `describe_spell_crystals()` is keyed by custody key.
- `capture_index_graft` finds each member's custody by (spell id, the index's spellbook id); its "members" map stays
  keyed by spell id (one index lives in one Book).
- PersistenceSystem passes the new parameters through. The map names stay; comments say what keys them.

## Validation Expectations
- Unit: two crystals with one id in two frames coexist; activity and removal move or evict one copy; segment
  payloads carry both names; lookups by id, by frame and by key; a graft picks its own Book's copy. Test stubs gain
  `custody_key`.
<!-- END ENTRY: "PersistenceProfile and PersistenceSystem: custody by key" -->

<!-- BEGIN ENTRY: "Crystallizer facade: key-aware verbs" -->
## Before
- `create_spell_crystal(spell, spellbook_id=None)`; `emit_spell_removed(spell_id)`;
  `emit_spell_activity(spell_id, active)` re-reads the crystal by spell id; `get_spell_crystal(spell_id)`.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:829-865
  - src/melder/crystallizer/crystallizer.py:1113-1141
  - src/melder/crystallizer/crystallizer.py:1471-1545
  - src/melder/crystallizer/crystallizer.py:1596-1640

## After
- `create_spell_crystal` passes `per_frame_custody=not aether.process_wide_unique_spell_ids`.
- `emit_spell_removed` and `emit_spell_activity` take `frame_name: Optional[str] = None` and address the custody key
  (the id under process-wide ids; "<id>@<frame>" otherwise, ValueError without a frame); activity re-reads that key.
- `get_spell_crystal(spell_id, frame_name=None)` forwards to the record's lookup.
- The four spellbook emission sites pass `frame_name=self._aetheric_frame_name`; crystal creation sites are
  unchanged (the crystal reads its spell's frame); transfer re-emission is unchanged (transfers stay in one frame).

## Validation Expectations
- Unit: under per-frame ids the verbs need the frame and touch only that copy; under process-wide ids the frame is
  optional and ignored for the key.
<!-- END ENTRY: "Crystallizer facade: key-aware verbs" -->

<!-- BEGIN ENTRY: "RecordVersion 4.0.0" -->
## Before
- CURRENT "3.0.0" (major 3 fenced named lesser topology).
  EVIDENCE: src/melder/crystallizer/persistence/record_version.py:76-78.

## After
- CURRENT "4.0.0": major 4 fences frame-scoped custody keys, so an older reader refuses a new record instead of
  folding two frames' copies into one. Older records stay readable (bare keys are process-wide keys).

## Validation Expectations
- Existing stamp and gate tests (they compare with CURRENT); integration: a 3.x-shaped record still restores.
<!-- END ENTRY: "RecordVersion 4.0.0" -->

<!-- BEGIN ENTRY: "ImpactEngine: spell lookup" -->
## Before
- `blast_radius_of_spell(spell_id)` looks up the exact custody key.
  EVIDENCE: src/melder/crystallizer/crystal_analysis/impact_engine.py:281-317.

## After
- Exact key first; otherwise the first key in sorted order whose payload "id" is the spell id. affected_spells and
  custody_states list custody keys (a per-frame record lists one entry per frame's copy).

## Validation Expectations
- Unit: a spell id answers through a frame-scoped key; an unknown id still answers unknown_spell.
<!-- END ENTRY: "ImpactEngine: spell lookup" -->
