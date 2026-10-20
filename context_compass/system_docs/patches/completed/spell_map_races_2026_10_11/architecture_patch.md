# Architecture patch: spell_map_races_2026_10_11

## Objective
Close the remaining races over Spellbook's spell maps and SpellIndex membership that the find_spell_by_id lane
(0.2.8229) left open, and make the id lookups' documentation state the miss contract they implement. Ticket:
tickets/tasks/2026-10-11_close_remaining_spell_map_races_task.md.

## Non-goals
- No reader-side Book lock anywhere (conjure holds that lock while phase workers and hooks run).
- No change to what any lookup answers on a quiet Book; no new public API.
- D-10, D-11, D-20 and the Aether frame-registry sweep are out of scope.

## Changed components
- Spellbook Core: bind publishes its four active maps (_lookup_spells, _spells, _spells_by_id, _spell_id_pool)
  under the Book lock; inspect_spell over another Book,
  the contracted-spell lookup and the creation system's book-wide factories walk one-call snapshots.
- Binding Pipeline: SpellIndex.has_spell re-checks cleaned under its lock; new internal
  SpellIndex._has_spell_unless_cleaned; Detail.has_spell and IndexDetail.has_spell answer through it.
- Conduit Runtime / Aether: Conduit.get_spell_permissions and CommandSystem.get_spell_by_id resolve through
  Spellbook.find_spell_by_id; the transfer impact walk snapshots its maps. Conduit.get_spell_by_id and
  get_conduit_by_spell_id keep raising ValueError for an unclaimed id (owner decision 2026-10-11); their docstrings,
  and get_conduit_by_spell_id's annotation, now say so, as do Spellbook._get_conduit_by_spell_id and
  _get_spell_by_id_via_aether.

## Invariants
1. Every writer of Spellbook._spells, _lookup_spells, _spells_by_id and _spell_id_pool holds the Book lock, so a
   walk that holds it never meets a size change or a resize.
2. A walk that does not hold the Book lock iterates a one-call snapshot (list(...) of the map or view), never a
   live view; a single-key read stays a single-key read.
3. A membership probe over an index the caller neither owns nor locks answers False for a cleaned index; the
   public has_spell raises only the documented RuntimeError, never AttributeError.
4. Conduit.get_spell_by_id and get_conduit_by_spell_id raise ValueError for an id no conduit claims (unknown or
   removed, bound in another frame, owner cleaned, a lineage between owners while a transfer runs) and for an
   unknown frame, as they always did, and document it: get_* raises and find_* returns None, the lookup convention
   of 0.2.79 and 0.2.8208 (owner decision 2026-10-11, ticket Note 11).

## Interface deltas
- New internal: SpellIndex._has_spell_unless_cleaned(spell_id) -> bool.
- Documentation only: Conduit.get_conduit_by_spell_id is annotated Conduit (it never returned None);
  get_spell_by_id keeps Optional[Spell] (None when the owner's Book does not resolve the id); both document
  their ValueError. No public behaviour changes.

## Migration order
Tests (red where reproducible) -> src -> component docs -> architecture doc and indexes -> graph -> notch and
release note -> assets and llm_support last.

## Rollback
Revert the src files of the change set; no data, cache or record format changes (no cache generation moves).

## Coverage matrix
| invariant | test |
| --- | --- |
| 1 | Book-locked walk paused mid-walk while another thread binds (component) |
| 2 | creation-system loop paused in its body while another thread binds (component) |
| 3 | has_spell with cleanup between check and lock; probe after cleanup; IndexDetail (unit) |
| 4 | unclaimed id -> ValueError naming it from both Conduit lookups; registered id resolves; unknown frame ->
ValueError (component contract lock; the two integration tests that pin the raise stay) |
