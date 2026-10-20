# Architecture patch: spell_index_naming_2026_10_18

## Objective and non-goals
- Objective: carry the owner's rulings of 2026-10-18 into the names Melder's code uses. A SpellIndex is not a
  lineage: it is an index that organizes spells and selects one, and a spell_id names one spell. Lineage is the
  conduit scope tree: a root conduit and its lessers. After the src wording pass the owner chose "Messages and
  renames": reword the runtime messages that call a SpellIndex a lineage and rename the identifiers, diagnostic
  codes and detail keys that do (Breaking in the release note), and "Also tests, UX, docs". This patch is the
  rename map with its message rewordings and compatibility notes, for his approval before any rename lands.
- Lands with it, not gated by this patch (docstrings and comments only, owner-directed 2026-10-18): the src
  wording pass, 552 hand edits in 72 files, uncommitted and not notched.
- Non-goals:
  - Every scope-tree use of lineage stays: `Existence.unique_per_conduit_lineage` and its "lineage" route family,
    `ConduitLineageGateOps` and `conduit_lineage_gate_ops`, the lesser lineage and its errors ("Root conduit is not
    set for this lineage."), `lineage_ancestors`, `lineage_depth`, the member root lineages a cluster drains.
  - Two other meanings stay: the ACL configuration chain's revision lineage and IDBuilder's dotted
    ownership-chain ids.
  - No behaviour, control flow, lock, severity or diagnostic condition changes; no alias or shim for an old name
    (the owner's no-fallback rule).
  - RootResolutionBlueprint's SpellIndex id stays unthreaded: both SpellSystemRootBlueprintBuilder sites pass None
    today, so `root_lineage_mismatch` cannot fire outside its unit tests; the rename keeps that, and threading the
    id is not asked.

## Changed components
- Phase 6 system validation (component_patch_phase6_validation): SpellSystemNode, SpellSystemIndex,
  RootResolutionBlueprint, SpellSystemRootBlueprintBuilder, CompilerPhase5's index build, CompilerPhase6's
  strategy list, six strategies (three classes and their modules renamed), SpellbookValidationError's internal
  codes, the dormant phase 2-5 IR capture and StructuralSnapshot's hydrate message.
- DevOps risk tracking (component_patch_risk_manager): RiskManager and its per-conduit bucket; the loop variable
  of ConduitWard's contract-consumer invalidation.
- The meld gate (component_patch_meld_gate): `Meld._ensure_lineage_resolvable`, its two callers and the class
  docstrings that name it.
- Ownership transfer (component_patch_transfer_of_ownership): four private methods, two parameters and one
  runtime message.
- Tests, system documents, the graph and the UX examples (component_patch_tests_docs_graph).

## Invariants
- I1. Only names and text change. Every renamed method, parameter, slot, local, module, class, code and key keeps
  its behaviour, positional order, call order and severity; no lock, cache, codegen or record change.
- I2. A name that means a SpellIndex says spell_index (or index, for a local map keyed by SpellIndex id); a
  scope-tree name keeps lineage; a name that holds either a SpellIndex id or "spell:<spell_id>" (RiskManager's
  resolution key) says what it is: `risk_key`.
- I3. No old name survives: a caller of an old name fails at import or attribute lookup, and every caller in src,
  tests, UX and documents moves in the same change.
- I4. Nothing persisted reads a renamed name. The creation cache stores no Phase 6 diagnostic, code, key or
  strategy name; the Crystallizer records no SpellIndex-lineage key (its `lineage_ancestors` is the scope tree);
  the phase 2-5 IR capture has no production caller and hashes values, not keys. No cache generation,
  RecordVersion or codegen change.
- I5. The bind-guard manifest keeps 628 entries; the three renamed strategy classes change their (module,
  qualname) pairs when it is regenerated at the rebuild.
- I6. Lines in a file with mixed line endings keep their own terminators: CompilerPhase5's two lines go through
  the keep-endings applier the owner approved for the six wording lines.

## Interface deltas
None of these names is exported at the package root, and no class here is public (Phase 6 nodes, blueprints and
strategies, RiskManager and the transfer are internal). What reaches a user is text: the codes and messages a
`SpellbookValidationError` renders when a conjure or meld is refused. Owner direction: listed as Breaking.

Diagnostic codes, messages and detail keys:

| strategy (after) | code before -> after | message after | detail keys before -> after |
| --- | --- | --- | --- |
| SpellIndexAlignmentStrategy | `root_lineage_mismatch` -> `root_spell_index_mismatch` (internal) | "Root '<root>' carries SpellIndex '<a>', but its SpellSystemIndex node records SpellIndex '<b>'." | `root_lineage_id`, `index_lineage_id` -> `root_spell_index_id`, `node_spell_index_id` |
| SpellIndexVersionConflictStrategy | `lineage_version_conflict` -> `spell_index_version_conflict` (user error) | "Root '<root>' includes multiple versions of SpellIndex '<id>': [...]." | `lineage_id` -> `spell_index_id` |
| RootSpellIndexConflictStrategy | `root_lineage_conflict` -> `root_spell_index_conflict` (internal) | "SpellIndex '<id>' maps to multiple root spell ids: [...]." | `lineage_id` -> `spell_index_id` |
| OwnershipConsistencyStrategy | `lineage_conduit_conflict` -> `spell_index_conduit_conflict` (internal) | "SpellIndex '<id>' maps to multiple conduits: [...]." | `lineage_id` -> `spell_index_id` |
| ContractedVersionDriftStrategy | `contracted_version_drift` (kept) | "Spell '<s>' is not a visible current version of SpellIndex '<id>'." | `lineage_id` -> `spell_index_id` |
| IdentityMixingStrategy | `identity_mixing_detected` (kept, internal) | "Spell '<s>' depends on SpellIndex id '<d>' instead of a spell_id." | `known_lineage_ids` -> `known_spell_index_ids` |

Other runtime messages:

| raiser | before | after |
| --- | --- | --- |
| SpellSystemNode, SpellSystemIndex.ensure_node (ValueError) | "lineage_id must not be None." | "spell_index_id must not be None." |
| StructuralSnapshot.hydrate_full_hit (RuntimeError) | "Spell <id> has no lineage state at hydrate." | "Spell <id> has no SpellSystemState for its SpellIndex at hydrate." |
| TransferOfOwnership._mark_spell_index_disabled (RuntimeError) | "Failed to register lineage for transfer disable." | "Failed to register the SpellIndex's state for the transfer's disable." |

Identifiers (all internal):

| before | after | kind |
| --- | --- | --- |
| `SpellSystemNode(lineage_id=)`, `.lineage_id`, slot `_lineage_id` | `spell_index_id`, `.spell_index_id`, `_spell_index_id` | keyword, property, slot |
| `SpellSystemIndex.ensure_node(spell_id, lineage_id, ...)` | `spell_index_id` | parameter |
| `RootResolutionBlueprint(root_lineage_id=)`, `.root_lineage_id`, slot `_root_lineage_id` | `root_spell_index_id`, `.root_spell_index_id`, `_root_spell_index_id` | keyword, property, slot |
| `LineageAlignmentStrategy` (`lineage_alignment_strategy.py`) | `SpellIndexAlignmentStrategy` (`spell_index_alignment_strategy.py`) | class, module |
| `LineageVersionConflictStrategy` (`lineage_version_conflict_strategy.py`) | `SpellIndexVersionConflictStrategy` (`spell_index_version_conflict_strategy.py`) | class, module |
| `RootLineageConflictStrategy` (`root_lineage_conflict_strategy.py`) | `RootSpellIndexConflictStrategy` (`root_spell_index_conflict_strategy.py`) | class, module |
| `Meld._ensure_lineage_resolvable` | `Meld._ensure_spell_index_resolvable` | method |
| `_ConduitRiskState.lineages` | `spell_index_ids` | slot |
| `RiskManager._lineage_conduits` | `_spell_index_conduits` | slot |
| `RiskManager._resolve_lineage_id`, `_resolve_lineage_id_from_spell_id` | `_resolve_spell_index_id`, `_resolve_spell_index_id_from_spell_id` | methods |
| `RiskManager.on_structural_validity_change(lineage_id, validity)` | `(spell_index_id, validity)` | parameter (its caller passes it positionally) |
| `RiskManager._update_structural_risk(conduit_id, lineage_id, ...)` | `spell_index_id` | parameter |
| `RiskManager._update_resolution_risk(conduit_id, lineage_key, ...)` | `risk_key` | parameter |
| `TransferOfOwnership._mark_lineage_dirty`, `_mark_lineage_disabled` | `_mark_spell_index_dirty`, `_mark_spell_index_disabled` | methods |
| `TransferOfOwnership._conduit_has_impacted_lineage(conduit, impacted_lineages)` | `_conduit_has_impacted_index(conduit, impacted_index_ids)` | method, parameter |
| `TransferOfOwnership._collect_impacted_conduit_ids(*, impacted_lineages, ...)` | `impacted_index_ids` | keyword parameter |
| IR payload key `"phase5_root_lineage_id"` (no production caller) | `"phase5_root_spell_index_id"` | dict key |
| locals `lineage_id`, `lineage_ids`, `lineages`, `root_lineage_id`, `phase5_root_lineage_id`, `impacted_lineages` | `spell_index_id`, `spell_index_ids`, `spell_index_ids`, `root_spell_index_id`, `phase5_root_spell_index_id`, `impacted_index_ids` | locals |
| locals `lineage_to_spell_ids`, `lineage_to_conduits`, `lineage_to_spells`, `lineage_to_roots` | `index_to_spell_ids`, `index_to_conduits`, `index_to_spells`, `index_to_roots` | locals |

## Migration order
1. These patch docs, linked from the ticket and the artifact board; the owner approves the map (or edits it).
2. Red tests on today's tree: the strategy unit tests assert the new codes, keys and messages.
3. src in one change set: the three strategy modules moved with `mv -n`, then every renamed name, code, key and
   message by hand, one line for one line, in edit modules like the wording batches; CompilerPhase5's two lines
   with the keep-endings applier.
4. Tests: four modules moved with `mv -n`, the renamed names, codes, keys, monkeypatch targets and SpellIndex-id
   fixture values, and the docstring and comment wording pass, in the same per-file edits.
5. Suites with the GIL off and on: the Phase 6, meld, risk, transfer and dev-ops trees, then the whole tree.
6. System documents (names and wording) with their indexes; the graph (three descriptors moved with `mv -n`, ids,
   edges and authored prose updated, re-extracted, accepted after reading, reassembled); the UX wording.
7. The release note (one section, the renames under Breaking); one notch, the next number above `__version__` at
   landing (0.2.8254 is melder_0's); NOTICE M1-28 to melder_0; the rebuild last.

## Rollback
- Revert the change set, the seven `mv -n` moves included (three src modules, four test modules) and the three
  descriptor moves. Nothing persisted, cached or emitted carries a renamed name.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md (Notes 2026-10-18T01:29:02Z to 02:12:55Z, 10:37:30Z and the plan Note of this patch) |

## Code description patch
- Not required: no control flow, error semantics, rollback path or lock changes.
