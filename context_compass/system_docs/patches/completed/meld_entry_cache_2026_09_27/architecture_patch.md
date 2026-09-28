# architecture_patch

## Metadata
- Patch ID: meld_entry_cache_2026_09_27
- Status: draft
- Owner: user (implementation: fable_0)
- Created: 2026-09-27T21:39:56Z
- Updated: 2026-09-27T21:39:56Z
- Ticket: tickets/tasks/2026-09-27_meld_entry_cache_by_name_and_class_task.md

## Objective
The calls users write - `conduit.meld("Name")` and `conduit.meld(spell=Cls)` - reach the compiled builder through
`Conduit.meld` -> `ConduitMeld.meld` -> `_input_resolution_cache` (name/class -> id) -> `_spell_id_pool` -> the
creation-context lane -> the builder: four Python frames and four C calls of dispatch around the construction
(533-536 ns vs 372 ns for `meld(spell_id=...)` on a width-1 object, VM, directional). Only `spell_id=` melds have
the inline warm lane in `Conduit.meld`. This patch gives the name and class shapes the same warm lane: a second
success-only registry on the meld door, `Meld._fast_input_doors`, keyed by the registered name string or the
class object the caller passed, holding the same `(spell, context, epoch, existing-object flag)` entry as the id
registry and read by the two public front doors with the id lane's guard ladder and arms. Prototype over the
real runtime objects: -32..-57% per warm creation on the shapes people write, -71% on a direct singleton meld.

## Non-goals
- No change to what `meld(spell_id=...)` does, to `_fast_meld_doors`, or to the door's slow lane results.
- No new codegen, no profile, no API change, no persisted-format change, no error-text change.
- Dynamic worlds, hooks, list/tuple/empty overrides, `spellframe`/`binding_name` addresses, instances and
  callables passed as `spell` keep their current paths.

## Changed Components
- Meld Resolution Runtime (code): `Meld` (registry slot, cleanup, docstring), `ConduitMeld.meld` (mint),
  `SpellSpaceMeld.meld` (mint), `Conduit.meld` (read lane).
- Creations and SpellSpace (code): `SpellSpace.meld` (read lane, mirror of `Conduit.meld`).
- Spellbook Core (code, one line): the upgrade route clears the new registry beside the two it clears today.

## Invariants
- I1 (same result): a warm hit returns exactly what the door's slow lane returns for the same call, because the
  entry is minted only after that lane succeeded for that key in the fast-lane posture (automatic world, no meld
  hooks, no spell hooks, no override payload or a non-empty dict payload, no stored mutation override) and every
  guard is a live read: `_meld_hooks`, `_door_epoch` compare, `_creation_context` identity,
  `_spellbook_validation_required`.
- I2 (remap safety): a name or class key resolves to a different spell only after its previous holder was parked
  by notch (`_cleanup_creation_context` bumps the epoch and clears the context) or cleaned by removal
  (`Spell.cleanup` deletes `_creation_context`, so the guard read raises AttributeError and misses); the frame's
  `LookupContainer.claim` refuses a second active spell per signature. A stale entry therefore always misses and
  is rebuilt by the slow lane for the new holder.
- I3 (bounded keys): entries are minted only for `str` names and classes (`isinstance(spell, type)`) that resolved,
  so the keyspace is the registered signatures plus the class objects a program passes; instances and callables
  never become keys (`normalize_spell_name` keys an instance by its class name, so an instance key would be
  unbounded and would keep the instance alive).
- I4 (no aliasing with ids): names live in their own dict; a registered name equal to another spell's 64-hex id
  can never serve the id lane.
- I5 (unchanged): the id lane, the executor read per hit through the live context (phase-11 hot swap), the
  cache-emit check, the existing-object arm and the override arm behave as today.

## Interface Deltas
- `Meld._fast_input_doors: Dict[Any, Tuple[Spell, CreationContext, int, bool]]` (internal slot; deleted in
  `cleanup`).
- No public signature changes. `Conduit.meld` and `SpellSpace.meld` gain one warm lane each; the docstrings say so.

## Migration Order
1. Patch docs (this folder). 2. `meld.py` slot/cleanup/docstring; `conduit_meld.py` and `spellspace_meld.py`
mint; `conduit.py` and `spell_space.py` read lanes; `spellbook.py` upgrade clear. 3. Unit, differential and
invalidation tests. 4. Suites on 3.14t (`-X gil=0`) on the VM; the dispatch experiment re-run. 5. Byte-identical
device apply. 6. Notch/release note/rebuild after the owner's answer on the frozen window; canonical docs and
indexes; promote this folder.

## Rollback
- Remove the two read lanes and the two mints; delete the slot. Nothing is persisted; the id lane is untouched.

## Ticket Coverage Matrix
| section | implementation | validation |
| --- | --- | --- |
| I1 | ladder and arms copied from the id lane; mint on the two success arms | differential test: same object by name, class and id; override dict arm; existing-object arm |
| I2 | none (existing chokepoints) | tests: notch, cleanup_spell then rebind, hook attach, context cleanup, spellbook validation flag, dynamic world never mints |
| I3 | mint rule `type(key) is str` or `isinstance(key, type)` | test: an instance and a lambda as `spell` mint nothing |
| I4 | separate dict | test: a name equal to a spell id resolves by name only |
| I5 | no edit to the id lane | existing conduit/meld/spell_space suites |
