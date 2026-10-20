# Component patch: tests, system documents, graph and UX (spell_index_naming_2026_10_18)

## Before / after behavior
Tests (55 files hold a renamed name; inventory `rename_candidates_tests_hits.txt`, 324 lines):
- Every renamed name, code and key, edited by hand one line for one line: SpellSystemNode and RootResolutionBlueprint
  keywords and properties, the asserted codes and detail keys, RiskManager's `_spell_index_conduits` and a bucket's
  `spell_index_ids`, the patch targets `Meld._ensure_spell_index_resolvable` and the four transfer methods.
- Four modules move with `mv -n`, named after what they test:
  - `tests/unit/melder/spellbook/spell_crafter/system/validation/test_lineage_alignment_strategy.py` ->
    `test_spell_index_alignment_strategy.py`
  - `.../validation/test_lineage_version_conflict_strategy.py` -> `test_spell_index_version_conflict_strategy.py`
  - `.../validation/test_root_lineage_conflict_strategy.py` -> `test_root_spell_index_conflict_strategy.py`
  - `tests/integration/melder/aether/conduit/test_lineage_remediation_notch_race.py` ->
    `test_spell_index_remediation_notch_race.py` (its subject: a SpellIndex's validity remediation racing a notch)
- Fixture values that stand for a SpellIndex id ("lineage-root", f"lineage-{spell_id}", "lr") become
  "index-root", f"index-{spell_id}"; test function names that say lineage for a SpellIndex follow. Scope-tree
  tests keep theirs (`unique_per_conduit_lineage`, the lesser lineage, the conduit lineage gates).
- The docstring and comment wording pass the owner put in scope ("Also tests, UX, docs"; SpellIndex uses only) runs
  in the same per-file edit modules, so each test file is touched once.

System documents (released by melder_0's M0-192):
- src_architecture (9 lines), src_components (19) and tests_components (5) name renamed identifiers or codes; they
  follow the map. The wording pass covers the four system documents' SpellIndex uses (src_architecture line 18, "A
  spell index holds a lineage of versions", among them). Each edited document's index is regenerated in the same
  pass.

Graph (`context_compass/system_docs/graph/`):
- The three strategy descriptors under `melder/aether/spellbook/spell_compiler/system/validation/` move with `mv -n`
  to the new module names; inside them the node ids, `source`, `file`, labels and the collapse candidate take the new
  module path before re-extraction, so the authored fields stay on their nodes (copy authored fields onto a renamed
  node first; never let them retire). Their authored role and responsibilities are reworded.
- `compiler_phase_6.json` (12 lines: imports and authored edges to the three strategies) takes the new ids, so no
  edge dangles. Authored prose naming a renamed identifier is updated in `spell_system_states.json`,
  `spell_system_node.json`, `root_resolution_blueprint.json`, `risk_manager.json`, `conduit_meld.json`,
  `transfer_of_ownership.json`, `permissions.json`, `detail_reason.json` and `conduit_cluster.json`; the wording
  pass covers the rest of the authored prose's SpellIndex uses (`bind.json`'s Bind -> SpellIndex edge, "a SpellIndex
  lineage key", among them).
- Re-extract with `--strict`, read each changed node against its source and accept it, reassemble; the walker
  reports no stranded descriptor and no retired node from the moves.

UX examples, docs pages, README and agent guides:
- `UX_and_AIX_experiences/03_advanced/16_ward_policies.py` lines 9 and 16 ("borrowed lineages", "local lineages")
  mean contracted spells: reworded. `UX_and_AIX_experiences/AGENTS.md` line 68 ("lineages GROW via
  create_lesser_conduit") is the scope tree: kept.
- `docs/` pages, the README and `agents/` guides hold none of the renamed names; their few lineage uses go through
  the same classification, and only SpellIndex uses are reworded.

Release note, notch, rebuild:
- One section in `release_docs/next_version_release.md` for the naming: what a SpellIndex and a lineage are, the
  docstring pass, and under **Breaking change:** the four renamed codes and six reworded messages a
  `SpellbookValidationError` can show, with the three moved internal modules; nothing persisted changes, so no
  cache or record migration. The Packaging line names the rebuild for the new version; the bind-guard count stays
  628.
- One notch at landing, the next number above `__version__` (0.2.8254 is melder_0's), NOTICE M1-28; the rebuild
  last, both checks OK.

## Interface deltas
- None beyond the architecture patch's tables.

## State / failure deltas
- None.

## Dependency / ordering
- src first, then tests in the same change set (no state of the tree whose tests import a moved module by its old
  path), then the documents and the graph, then the release note, notch and rebuild.

## Validation expectations
- The whole tree with the GIL off and on; the UX example harness (`UX_and_AIX_experiences/pytest_examples`);
  `extract_graph.py --strict` and the walker's report; `index_document.py --check` on each edited document;
  `_build_asset_runner.py --check` and `llm_support/_builder.py --check` after the rebuild.
