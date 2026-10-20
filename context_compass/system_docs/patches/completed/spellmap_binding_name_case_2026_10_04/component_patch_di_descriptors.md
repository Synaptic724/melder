# Component patch: DI descriptors and Phase 3 SpellMap resolution (spellmap_binding_name_case_2026_10_04)

## Before / after behavior
- Before: `SpellMap(binding_name="ScanProfile").binding_name == "scanprofile"` (SpellContract too), while
  `bind(binding_name="ScanProfile")` stores "ScanProfile"; Phase 3 compared the two raw strings, so a
  mixed-case SpellMap default raised "SpellMap default could not be resolved". String spellframes were
  compared case-sensitively as well.
- After: both descriptors store "ScanProfile"; Phase 3 matches binding names and string frames by their
  normalized keys, so "ScanProfile", "scanprofile" and "SCANPROFILE" select the same provider, as meld does.

## Interface deltas
- Descriptor `binding_name` value semantics; TypeError for a non-string name; one Phase-4 warning code
  retired. Constructor signatures and the `canonical_key`, `spell_key` and `lookup_triplet` shapes unchanged.

## State and failure deltas
- No new state. Zero or several candidates still raise RuntimeError from Phase 3 (messages unchanged).
- SpellContract resolution was already key-based; only its stored value changes.

## Dependency and ordering
- The descriptor change and the Phase 3 change land together; either alone leaves bind and SpellMap apart.

## Validation expectations
- Regression tests: bind, SpellMap, SpellContract and meld with mixed-case names select one provider; the
  descriptors keep the caller's text; the two tests that pinned lowercasing are inverted.
- Unit tiers for the descriptors, Phase 3, the Phase-4 strategies and the structural snapshot pass.
