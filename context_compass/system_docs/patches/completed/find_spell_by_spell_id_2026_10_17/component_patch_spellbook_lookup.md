# Component patch: the Spellbook's spell_id lookup (find_spell_by_spell_id_2026_10_17)

## Before / after behavior
- Before: `Spellbook.find_spell_by_id(spell_id)` read `_spells_by_id` (active versions) and returned a hit; else
  read `_inactive_spells` (parked versions), and for a hit read the parked spell's index
  (`Spell._spell_index_unless_cleaned`) and returned `_spells[that index]` - the spell the index has active - or
  None when the index had none (a version split off by `remove_from_spell_index`) or the parked spell was cleaned.
- After: `Spellbook.find_spell_by_spell_id(spell_id)` reads `_spells_by_id`, then `_inactive_spells`, and returns
  the Spell found under that spell_id - active or parked - or None. No index is read. A caller that wants the spell
  an index has active asks the index (`get_spell_by_index_id`, or `_find_spell(index)` inside the kernel).
- `Spellbook._get_spell_by_id_via_aether` (name kept) returns the owning Book's `find_spell_by_spell_id` answer.

## Interface deltas
- Removed (public): `find_spell_by_id`. Added (public): `find_spell_by_spell_id(spell_id: str) -> Optional[Spell]`.
- Docstrings corrected where they claim the lookup resolves a parked id to the live spell: `SpellIndex.update`,
  `SpellIndex.has_spell`; `Spell._spell_index_unless_cleaned` names its remaining readers (the parked branch of
  `_find_contracted_spell_by_id`, the explicit index steps).

## State and failure deltas
- No state. Still lock-free and O(1); `check_cleaned()` still raises RuntimeError for a cleaned Book.
- A parked version answers itself: also one split off into an index with no active spell (was None).
- A parked version disposed while the lookup runs answers the Spell it read - a borrowed reference, as an active
  one always was - or None once its id has left the map; it never raises (was None through the cleaned-index read).
- A notch or transfer step in flight can still make a lookup miss (None) for that spell_id, as before.

## Dependency and ordering
- Exact callers (want the spell that owns the id): `Conduit.get_spell_by_spell_id` (through
  `_get_spell_by_id_via_aether`), `Conduit.get_spell_permissions`, the outbound half of
  `ConduitWard._get_spells_in_contract_by_conduit`, the renamed call sites.
- Callers that need an index's active spell take the explicit index step (Conduit, ConduitWard and
  TransferOfOwnership patches), in the same change.

## Validation expectations
- Component tests (the method's own file, renamed for the method): a current spell_id answers its active spell; a
  parked spell_id answers the parked spell; after a notch each spell_id answers its own spell; a parked version
  moved to another index or split off answers itself; a disposed parked version misses; after a transfer both
  spell_ids answer in the target Book and miss in the source; unknown and foreign ids miss; no live map is walked; a
  disposal racing the lookup never raises.
- The suites that call the method, GIL off and on.
