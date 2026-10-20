# Component patch: Conduit lookups by spell_id (find_spell_by_spell_id_2026_10_17)

## Before / after behavior
- `Conduit.get_spell_by_id(spell_id)` is renamed `Conduit.get_spell_by_spell_id(spell_id)` (owner, 2026-10-17)
  and made exact: before, for a parked spell_id, the spell its index has active (English for French's spell_id);
  after, the spell that owns the spell_id (French). Owner resolution through the frame is unchanged: a spell_id no
  conduit claims, or a missing frame, still raises ValueError.
- `Conduit.get_spell_permissions(spell_id)`: before, the active version's permissions for any spell_id of the
  index; after, the permissions the version with that spell_id was bound with. A miss still raises RuntimeError.
- `Conduit._resolve_transfer_spell` (transfer footprint): before, the spell_id branch returned `get_spell_by_id`'s
  answer, the index's active spell; after, it finds the spell by spell_id (`get_spell_by_spell_id`), then the spell
  that spell's index has active on this conduit (`get_spell_by_index_id`, the call its SpellIndex branch makes) -
  the same spell as before for a spell this conduit owns. A transfer moves the whole index
  (`transfer_spell_ownership`'s contract).
- The notch target's refusal for a version of another index names the renamed lookup in its remedy
  ("Pass its own index - conduit.get_spell_by_spell_id(<id>).spell_index - ...").
- Docstrings of `notch_spell`, `_resolve_notch_target`, `_owned_spell_by_id` and `add_to_spell_index` stop saying
  that `get_spell_by_id` / `find_spell_by_id` answer a parked spell_id with the index's active spell; a spell_id
  passed to them resolves to that exact spell, the spell `get_spell_by_spell_id` returns for it.

## Interface deltas
- `get_spell_by_id` removed, `get_spell_by_spell_id` added with the same signature, no alias; answers for a parked
  spell_id change (Breaking, release note). `get_spell_permissions` keeps its name and signature; its answer for a
  parked spell_id changes (Breaking).

## State and failure deltas
- No state. `add_spell_to_contract(spell_id=<parked>)` and `remove_spell_from_contract(spell_id=<parked>)` stop
  refusing with "Provided spell_id ... does not match inspected ID ...".
- `_resolve_transfer_spell` raises its RuntimeError in the same cases as before for a spell this conduit owns: a
  parked spell_id whose index has no active spell misses, as it did. A spell_id another conduit owns now misses
  here unless this conduit borrows its index (before, the other conduit's spell went on and the transfer refused
  it later, "Source conduit does not own the spell.").

## Dependency and ordering
- `get_spell_by_spell_id` -> `Spellbook._get_spell_by_id_via_aether` -> `find_spell_by_spell_id` on the owner's
  Book.
- The explicit index step takes this conduit's Book lock alone (`get_spell_by_index_id`); `_resolve_transfer_spell`
  runs before the transfer window with no other lock held.

## Validation expectations
- Integration: a lender with English active and French parked on one index, linked to a borrower:
  `get_spell_by_spell_id(French)` on the lender and the borrower returns French; English's spell_id returns
  English; after a notch to French, English's spell_id returns English; `get_spell_permissions` returns each
  version's own permissions; an unknown spell_id raises ValueError; `get_spell_by_id` no longer exists.
- A transfer by French's spell_id moves the whole index with English still active, as before.
