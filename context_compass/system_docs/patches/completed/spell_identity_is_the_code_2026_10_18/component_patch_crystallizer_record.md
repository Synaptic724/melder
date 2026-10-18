# Component patch: Crystallizer - the SpellCrystal records the binding hash (spell_identity_is_the_code_2026_10_18)

## Metadata
- Patch ID: spell_identity_is_the_code_2026_10_18
- Component: Crystallizer Root, Persistence Record, And Module-World Surfaces - `SpellCrystal`
  (`src/melder/crystallizer/crystals/spell_crystal.py`), `RecordVersion`
  (`src/melder/crystallizer/persistence/record_version.py`), `RestoreReport` and `RestoreEngine`
  (`src/melder/crystallizer/crystal_loader_system/restore_engine.py`); the docstrings of `GraftRunner`
  (`src/melder/crystallizer/crystal_loader_system/graft_runner.py`)
- Story: STORY-2026-10-18-binding_manifest_hash (S2), landing with STORY-2026-10-18-spell_id_hashes_the_object_code
  (S1)
- Status: approved - the owner's direction (chat 2026-10-18): "make sure you land the binding hash going into
  crystallizer too please" (the epic's DECISION note of 2026-10-18T16:18:35Z); its two design points - a minor
  record version and the restore report's binding changes - are stated to him with this patch.
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T16:32:46Z
- Updated: 2026-10-18T16:32:46Z

## Component Purpose and Boundary
- Current boundary, read on 0.2.8255 (spell_crystal.py, record_version.py and graft_runner.py whole; in
  restore_engine.py the report, the engine's state, its book-and-bind span and its contract replay): a SpellCrystal
  captures at bind what a restore replays through bind - the spellframe (its name, kind and a Protocol's module and
  qualname), the binding name, the existence, the permissions, resolvable, the resolved disposal names in order,
  the profile family and a managed spell's four settings (record 4.2.0) - and `describe()` is the payload the
  record persists, folds and replays. A restore rebinds each active and staged member from that payload under the
  receiving Book's policy. When a bind returns another spell_id than the recorded one, the report's identity map
  gains recorded -> live and the engine's per-Book translation follows it, so selections, parked members and
  contract grants find the rebuilt spell (`RestoreEngine._map_spell_identity`). A graft binds the same way and
  follows the ids its binds return; its report has no identity map.
- Today a receiving Book whose policy composes another disposal order gives another spell_id - the binding is in
  the id - and the identity map shows it. Under S1 the spell_id is the code and S2's binding hash carries the
  binding, so without this patch a binding rebuilt differently would leave no trace in the report.
- Target boundary: the crystal records the spell's binding hash beside the fields it records; a restore compares the
  hash of each binding it rebuilds with the recorded one and reports a difference; a graft behaves as before.

## Before/After Behavior Summary
- Before: `describe()` has no binding hash; RecordVersion 4.2.0. A restore into a Book whose disposal priority
  differs from the recording Book's binds `Greeter` with another disposal order: its spell_id moves and the
  identity map holds the old and the new id.
- After: `describe()["binding_hash"]` is the spell's `binding_hash` at capture; RecordVersion 4.3.0. The same restore
  keeps `Greeter`'s spell_id (its code did not change) and the report's `binding_changes` holds
  `{<custody key>: {"recorded": <hash>, "live": <hash>}}`; under the recording Book's policy it holds nothing. A
  spell whose code changed since the record (a class edited on disk) maps its spell_id as today.
- A record of 4.2.0 or before carries no binding hash: its bindings replay as before and are not compared.

## Interface Deltas
- `SpellCrystal.binding_hash` (property, str): the hash captured from `Spell.binding_hash`
  (component_patch_binding_pipeline.md, S2 section); `describe()` gains `"binding_hash"` for every spell.
- `RecordVersion.CURRENT` "4.2.0" -> "4.3.0", minor: an additive key that 4.2 readers ignore; a 4.3 reader of a 4.2
  record finds none.
- `RestoreReport.record_binding_change(custody_key, recorded_binding_hash, live_binding_hash)`; `describe()` gains
  `"binding_changes"`, a dict by custody key, empty when every binding replayed as recorded.
- `RestoreEngine._bind_one_active` and `_bind_one_staged` call `_record_binding_change(custody_key, crystal,
  live_spell)` after their bind; the staged path finds its parked spell with `find_spell_by_spell_id` (exact since
  0.2.8253).
- Docstrings (S1's statements, true until this landing): the SpellCrystal contract (record 4.3.0);
  `RestoreReport.map_identity`; `RestoreEngine._replay_books_and_binds`, `_bind_one_active`, `_bind_one_staged`,
  `_map_spell_identity`, `_replay_contracts` and `_replay_one_contract`; `GraftRunner._bind_selected` and
  `_merge_members` - a receiving Book's policy moves the binding hash, and a spell_id moves only with the code.

## State and Lifecycle Deltas
- SpellCrystal: one slot, `_binding_hash`, set in `__init__`, read under the crystal lock, deleted in `cleanup`.
- RestoreReport: one dict, `_binding_changes`, under the report lock - the parallel driver's units write it from
  worker threads, each under its own custody keys - deleted in `cleanup`.

## Failure Mode Deltas
- New failure mode: none. A difference is reported, never raised and never a shortfall: applying the receiving
  Book's policy is the restore's rule, as it is for the identity map today.
- Changed: a receiving-policy difference moves the binding hash, not the spell_id, so the references that went
  through the per-Book translation for it now resolve directly.
- RISK (S5, outside this patch): until S5 lands, a record written before S1 that holds one object twice - one class
  under two binding names - meets the one-object refusal at its second replayed bind and the all-or-nothing
  restore rolls back. S5's rule (restore the first registration, a shortfall per dropped duplicate) removes it.

## Dependency and Ordering Constraints
1. Needs `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section), so it follows spell.py's return
   after S9 (0.2.8256; M1-37).
2. Lands with S1 and S2 in one pass; the record version moves in the change set that adds the key.

## Validation Expectations
- Unit: the crystal of a class, of a staged version and of a managed spell carries its spell's binding hash, in
  the property and in `describe()`; cleanup deletes it; `RecordVersion.CURRENT` is 4.3.0 and a 4.2.0 payload passes
  `check_readable`; `RestoreReport.record_binding_change` and `describe()["binding_changes"]`, cleanup included.
- Integration: record, then restore into a Book under the recording Book's policy - the same spell_ids and binding
  hashes, no binding change; into a Book whose disposal priority differs - the same spell_ids, a binding change
  for each binding rebuilt with another order, and its contract grants and selections found without translation
  (the reversed premise of `test_changed_id_restore_regrants_contract_details`); a record without the key
  restores as before.
- The existing crystallizer, restore and graft suites pass.

## Unknowns and Open Decisions
- UNKNOWN: none in the code paths read.
- Stated for the owner: a graft reports no binding change, as it reports no changed spell_id today (it has no
  identity map).

## Context / Handoff Summary
- What changed: nothing in `src/`.
- Next entrypoint: `src/melder/crystallizer/crystals/spell_crystal.py:SpellCrystal.__init__` (the bind-signature
  capture), then `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._bind_one_active`.
