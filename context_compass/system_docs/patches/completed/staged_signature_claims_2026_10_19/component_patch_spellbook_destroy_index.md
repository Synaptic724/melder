# Component patch: Spellbook Core - `_destroy_spell_index` keeps other spells' signatures

Patch id: staged_signature_claims_2026_10_19. Author: melder_1 (synaptic_python_developer), 2026-10-19.

## Before
`_destroy_spell_index(spell_index, *, binding_key, owner_conduit_id)` pops `_lookup_spells[binding_key]` and calls
`AethericFrame.release_lookup(binding_key)`: both by key. Its callers hand it an index of parked members only
(`_apply_add_to_index` when the moved version emptied its source - every `bind_inactive`, folding the new version
off the index Bind minted - and the parked branch of `_dispose_spell` when the version was its index's last member),
with the departing parked version's key, which is the active sibling's key in the staging loop.

## After
`_destroy_spell_index(spell_index, *, spell_id, binding_key, owner_conduit_id)`:
1. pops `_spells[spell_index]` as before, and `_lookup_spells[binding_key]` only when it is `spell_index`;
2. calls `AethericFrame.release_lookup_by_spell_id(spell_id)` - the claim the departing member holds, if any -
   in place of `release_lookup(binding_key)`;
3. the frame registry, SpellSystemStates, record and index cleanup steps are unchanged.
Both callers pass the departing member's spell_id.

## State and failure deltas
- Visible today and gone after: a meld by address raising KeyError "[MELD] No spell found ..." for an active
  version, `find_spell_index` raising "Spell not found in the spellbook.", another Book's bind of a held signature
  accepted.
- A parked version that still holds a claim (S2's notch across keys) loses it when it is moved or disposed out of an
  index it empties - as by-key release did.

## Validation expectations
- The six component tests in
  `tests/component/melder/spellbook/test_spellbook_component_staged_version_keeps_active_signature.py`: five red on
  0.2.8262, all green after, with the GIL off and on; the claims probe re-run at the fix; the spellbook and conduit
  trees green.
