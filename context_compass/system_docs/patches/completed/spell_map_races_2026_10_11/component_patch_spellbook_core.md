# Component patch: Spellbook Core (spell_map_races_2026_10_11)

## Before / after
- bind: _lookup_spells and _spells were published outside the Book lock, _spells_by_id inside it (via
  _register_owned_spell_id, with _spell_id_pool). After: all four inside one `with self._lock` block; claim_lookup
  and the bind callbacks stay outside it. _register_owned_spell_id already took this lock at that point: no new
  lock-order edge.
- inspect_spell over another conduit's Book, _find_contracted_spell_by_id: live walks -> list(...) snapshots;
  the contracted lookup probes with SpellIndex._has_spell_unless_cleaned.
- SpellbookCreationSystem book-wide factories (reached without the Book lock through Conduit.validate_resolution):
  _collect_broken_spells input, cleanup_phase_artifacts_after_resolution (spell_ids=None), the lead-spell reads of
  root blueprints, system validation and change control, and the five plan factories walk list(values()).
- _get_conduit_by_spell_id and _get_spell_by_id_via_aether: docstrings say an unclaimed id raises the Aether
  lookup's ValueError (it always did); _get_conduit_by_spell_id is annotated Conduit.

## State / failure deltas
- No longer raised under concurrent binds/removals: "dictionary changed size during iteration" from these walks;
  StopIteration from an emptied lead-spell read.

## Dependency / ordering
Book lock taken only by writers; snapshots are lock-free; no lock held while calling user code changes.

## Validation expectations
Paused-walk tests red on the 0.2.8229 tree where the race is deterministic, green after; full tree identical apart
from the added tests and the stubs that modelled the old walks.
