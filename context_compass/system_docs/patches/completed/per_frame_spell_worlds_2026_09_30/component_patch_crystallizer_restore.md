# component_patch_crystallizer_restore

## Metadata
- Patch ID: per_frame_spell_worlds_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T17:18:12Z
- Updated: 2026-09-30T17:18:12Z

<!-- BEGIN ENTRY: "RestoreEngine stage 1: recorded regime" -->
## Before
- Skips the recorded payload when Aether is configured; otherwise rebuilds (default regime) and activates it, even
  when frames exist, where the 0.2.8209 guard refuses a different sealed regime and the restore fails.
  EVIDENCE: src/melder/crystallizer/crystal_loader_system/restore_engine.py:1339-1393.

## After
- Live regime not yet fixed (Aether unconfigured, no frame): install the recorded configuration; its regime is
  sealed by the first frame stage 5 births.
- Live regime fixed (configured, or a frame exists) and different from a recorded regime: when the record binds one
  spell id in two frames and the live regime is process-wide, raise before anything is built (B); otherwise add the
  shortfall naming both regimes. A configured Aether is then skipped as today; an unconfigured one with frames
  installs the recorded logger policy under the live regime.
- A payload without the regime (pre-4.0 record) keeps today's behaviour plus the "missing" report when rebuilt.

## Validation Expectations
- Unit (synthetic chains): each branch above, including the refusal leaving nothing built.
- Integration: per-frame records restored in a reset world run per-frame ids afterwards.
<!-- END ENTRY: "RestoreEngine stage 1: recorded regime" -->

<!-- BEGIN ENTRY: "RestoreEngine stage 6: per-Book custody replay" -->
## Before
- `_book_bind_order` matches the Book's bind_order (spell ids) against custody keys; `_index_id_for_member` scans
  every Book's indexes; one global recorded-to-live spell map serves selections, anchors and contract grants.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1956-2202
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2462-2532

## After
- Bind order returns custody keys in the recorded order (spell ids mapped to this Book's keys), then the rest
  sorted. Binds take the spell id from the payload ("id", else the key) and use the key for shortfalls.
- `_index_id_for_member(spellbook_id, spell_id)` searches only that Book's indexes.
- Spell translation is per Book: `(recorded book, recorded spell id) -> live id`, written by active and staged binds
  (the report's identity map still records it); selections and anchors use their Book; a contract detail uses the
  Book of the conduit that granted it. Unchanged ids need no entry.

## Validation Expectations
- Integration: the same class in two frames restores both bindings in their own Books with selections intact;
  staged members anchor in their own Book.
<!-- END ENTRY: "RestoreEngine stage 6: per-Book custody replay" -->

<!-- BEGIN ENTRY: "LoadAdmission retarget: custody frame" -->
## Before
- Retarget rewrites frame twins and spellbook/cluster `frame_name` only.
  EVIDENCE: src/melder/crystallizer/crystal_loader_system/load_admission.py:274-333.

## After
- spell_crystal payloads get the target `frame_name`; a frame-scoped key (key different from the payload id) is
  rebuilt for the target frame and the entry re-keyed, with "custody_key" updated. The journal is minted afterwards
  from the rewritten keys, as today.

## Validation Expectations
- Unit: a retargeted per-frame slice carries "<id>@<target>" keys and payloads; a process-wide slice keeps its keys.
<!-- END ENTRY: "LoadAdmission retarget: custody frame" -->
