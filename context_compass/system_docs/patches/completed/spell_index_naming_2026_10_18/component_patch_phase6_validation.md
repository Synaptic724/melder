# Component patch: Phase 6 system validation names (spell_index_naming_2026_10_18)

## Before / after behavior
- SpellSystemNode (`src/melder/aether/spellbook/spell_compiler/system/spell_system_node.py`): a node carries the
  SpellIndex id of its spell as `lineage_id` (constructor keyword, property) in slot `_lineage_id`, and refuses None
  with "lineage_id must not be None.". After: `spell_index_id`, `_spell_index_id`, "spell_index_id must not be
  None.". Same value, same check.
- SpellSystemIndex.ensure_node (`spell_system_index.py`): parameter `lineage_id` -> `spell_index_id`, passed on as
  `spell_index_id=`; its ValueError text follows.
- RootResolutionBlueprint (`blueprints/root_resolution_blueprint.py`): `root_lineage_id` (constructor parameter,
  property) and slot `_root_lineage_id` -> `root_spell_index_id`, `_root_spell_index_id`. The value stays optional;
  SpellSystemRootBlueprintBuilder passes `root_spell_index_id=None` at both of its sites, as it passes None today,
  and keeps the comment "SpellIndex ids can be threaded later if needed".
- CompilerPhase5._build_system_index_for_snapshot (`phases/compiler_phase_5.py`): the local that holds the spell's
  `SpellSystemState.spell_index_id` is `spell_index_id`, passed as `SpellSystemNode(spell_index_id=...)`. Lines 296
  and 306 end in CRLF in a file with mixed endings: the keep-endings applier.
- The six strategies under `system/validation/` (codes, messages and keys in the architecture patch's table):
  - `LineageAlignmentStrategy` -> `SpellIndexAlignmentStrategy`, module moved to
    `spell_index_alignment_strategy.py`; local `root_lineage_id` -> `root_spell_index_id`; reads
    `blueprint.root_spell_index_id` and `node.spell_index_id`.
  - `LineageVersionConflictStrategy` -> `SpellIndexVersionConflictStrategy`, module
    `spell_index_version_conflict_strategy.py`; locals `lineage_to_spell_ids` -> `index_to_spell_ids`,
    `lineage_id` -> `spell_index_id`.
  - `RootLineageConflictStrategy` -> `RootSpellIndexConflictStrategy`, module
    `root_spell_index_conflict_strategy.py`; locals `lineage_to_roots` -> `index_to_roots`, `lineage_id` ->
    `spell_index_id`.
  - OwnershipConsistencyStrategy (name kept): locals `lineage_to_conduits`, `lineage_to_spells`, `lineage_id` ->
    `index_to_conduits`, `index_to_spells`, `spell_index_id`; its docstring's "Uses `lineage_id` as the grouping
    key" names `spell_index_id`.
  - ContractedVersionDriftStrategy (name kept): locals `lineage_to_spell_ids`, `lineage_id` ->
    `index_to_spell_ids`, `spell_index_id`.
  - IdentityMixingStrategy (name kept): local `lineage_ids` -> `spell_index_ids`.
  - Each moved module's docstrings name the new class, code and keys; their other wording was done in the src
    pass.
- CompilerPhase6 (`phases/compiler_phase_6.py`): imports the three classes from their new modules and lists them in
  `_build_strategies` in the same positions, so the canonical order and the diagnostics' order do not change.
- SpellbookValidationError.INTERNAL_CODES (`utilities/custom_exceptions/spellbook_validation_error.py`):
  `lineage_conduit_conflict`, `root_lineage_conflict`, `root_lineage_mismatch` -> `spell_index_conduit_conflict`,
  `root_spell_index_conflict`, `root_spell_index_mismatch`, in the set's sorted order. `spell_index_version_conflict`
  stays out of the set, as `lineage_version_conflict` is today (a user-facing error).
- SharedCompilerExecutions.capture_phase2_5_codegen_ir (`phases/shared_compiler_executions.py`; no production
  caller - CompilerPhase2 dropped the eager export): local and payload key `phase5_root_lineage_id` ->
  `phase5_root_spell_index_id`. The signature hashes a positional tuple of values, so equal inputs hash as before.
- StructuralSnapshot.hydrate_full_hit (`structural_snapshot/structural_snapshot.py`): "Spell <id> has no lineage
  state at hydrate." -> "Spell <id> has no SpellSystemState for its SpellIndex at hydrate.", beside the
  existing "has no SpellIndex at hydrate.".

## Interface deltas
- Internal only: the names above. A test or tool that imports a strategy from its old module, reads
  `node.lineage_id` or `blueprint.root_lineage_id`, or asserts an old code or key fails (no alias).
- User-visible text: the four renamed codes and the six reworded messages in a `SpellbookValidationError`; three of
  the codes render marked [internal] as before.

## State / failure deltas
- None. The same diagnostics fire under the same conditions with the same severities and order; only their codes,
  messages and detail keys read differently.
- A diagnostic's `source` (the producing strategy's class name, filled by SpellSystemValidationSystem) changes for
  the three renamed classes. It is compared only inside a process (ConduitResolutionState's diagnostics signature)
  and is never persisted or rendered.

## Dependency / ordering
- The three modules move with `mv -n` in the same change set that edits their imports in CompilerPhase6; no state
  of the tree imports a moved module by its old path.
- SpellSystemNode's keyword changes together with its two producers (CompilerPhase5, SpellSystemIndex.ensure_node)
  and the RootResolutionBlueprint keyword with the builder's two sites.

## Validation expectations
- Red first: each strategy's unit test asserts the new code, keys and message on today's tree (fails), then passes.
- The Phase 6 unit and component trees (`tests/unit/melder/spellbook/spell_crafter/system/`,
  `tests/component/melder/spellbook/spell_crafter/system/`), the CompilerPhase5 and 6 tests, the
  SpellbookValidationError rendering tests (the renamed internal codes still render [internal]), GIL off and on.
