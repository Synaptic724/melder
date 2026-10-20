# Component patch: the meld gate's name (spell_index_naming_2026_10_18)

## Before / after behavior
- `Meld._ensure_lineage_resolvable(spell)` (`src/melder/aether/conduit/meld/meld.py`) is
  `Meld._ensure_spell_index_resolvable(spell)`. It refreshes the stale dependencies a compiling plan expands, reruns
  the structural phases while the SpellSystemState of the spell's SpellIndex reads `unknown` or `gated`, gates the
  conduit verdict after a rerun and hands off to the per-conduit resolution gate - what it does today. The name
  says whose state it ensures: the SpellIndex's.
- Its callers rename the call: ConduitMeld.meld (`conduit_meld.py`) and SpellSpaceMeld.meld (`spellspace_meld.py`),
  both under `if self._spellbook._spellbook_validation_required:`.
- The class docstrings that cite it name the new method: SpellValidity (`spell_validity.py`) and SpellSystemStates
  (`spell_system_states.py`).

## Interface deltas
- None public: Meld is internal (AGENT_ACCESS: internal). Tests patch the method by name - `test_meld.py` (24
  lines), the remediation race integration test (3), the non-resolvable flag component test (2) - and move with it.

## State / failure deltas
- None.

## Dependency / ordering
- The definition and its two calls change in one change set; no state of the tree calls a missing method.
- The system documents name it in the Meld-Time Validation Gate sequence and the component map (13 lines across
  src_architecture and src_components); they follow at landing.

## Validation expectations
- `tests/unit/melder/aether/conduit/meld/test_meld.py`, the renamed remediation race test, the warm meld door tests
  and the non-resolvable flag tests, GIL off and on.
