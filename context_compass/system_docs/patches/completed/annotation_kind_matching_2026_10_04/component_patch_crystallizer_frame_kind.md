# component_patch_crystallizer_frame_kind

## Metadata
- Patch ID: annotation_kind_matching_2026_10_04
- Status: active
- Owner: user (agent fable_1)
- Created: 2026-10-04T01:20:00Z
- Updated: 2026-10-04T01:20:00Z

<!-- BEGIN ENTRY: "SpellCrystal and loaders: the frame kind survives a restore" -->
## Before
- `SpellCrystal` records `_spellframe_name` only (`__name__` of a class frame, `str()` otherwise) and
  exposes it through `spellframe_name` and `describe()["spellframe_name"]`. `RestoreEngine._bind_one_active`,
  `_bind_one_staged` and `GraftRunner._bind_selected` (three sites) rebind with
  `spellframe=crystal.get("spellframe_name")` - a STRING. Under 0.2.8218's name matcher that string frame
  resolved exactly like the Protocol object; under kind matching it would be a category, so every
  Protocol-typed consumer of a restored world would stop resolving. `RecordVersion.CURRENT` is "4.0.0".
  EVIDENCE:
  - src/melder/crystallizer/crystals/spell_crystal.py:293-299
  - src/melder/crystallizer/crystals/spell_crystal.py:705-721
  - src/melder/crystallizer/crystals/spell_crystal.py:1222-1222
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2173-2190
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2773-2833
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:403-415
  - src/melder/crystallizer/persistence/record_version.py:80-80

## After
- The crystal also records `_spellframe_kind` (`"none"` / `"category"` / `"contract"`, the enum value's name),
  `_spellframe_module` and `_spellframe_qualname` (the Protocol's coordinates for a contract, None otherwise);
  three read properties and three `describe()` keys. RecordVersion "4.1.0" (minor: additive fields; 4.0.0
  readers keep reading, pre-4.1 records read with the new keys absent).
- Both loaders rebind through one helper: when the recorded kind is `contract`, import the Protocol by its
  coordinates through the existing qualified-import lane and bind it as the frame; when the import fails,
  file a shortfall (`spellframe_contract_hydration_failed (<module>.<qualname>): <error>`) and bind the name as
  a category so the spell still exists and is addressable by name; when the kind is absent (older record) or
  `category`/`none`, bind the recorded name (or None) as before.

## Interface Deltas
- Additive: three crystal fields/properties, three describe keys, one minor record version.

## State / Failure Deltas
- A restored or grafted Protocol-framed spell resolves Protocol-typed consumers as the recorded world did;
  the only new report row is the hydration shortfall above.

## Validation Expectations
- Unit: describe carries the three keys for a contract, category and bare spell; a 4.0.0 payload (no keys)
  rebinds by name. Integration: record -> restore of a Protocol-framed provider resolves `svc: IService`
  after the restore; a Protocol that cannot import files the shortfall and the spell is bound as a category.
<!-- END ENTRY: "SpellCrystal and loaders: the frame kind survives a restore" -->
