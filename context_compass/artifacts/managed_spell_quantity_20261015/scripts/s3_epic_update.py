"""S3 turn-in: settle U3-U6 and U10 in the epic's Build Specification, mark S3 landed, add the epic's S3
MEASURE note and refresh the handoff. Every replacement must match exactly once or nothing is written."""
import pathlib
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
text = EPIC.read_text(encoding="utf-8")

REPLACEMENTS = [
    (
        "- Updated: 2026-10-15T12:42:32Z\n",
        f"- Updated: {NOW}\n",
    ),
    (
        '''- Sizes: elastic -> `baseline_idle=min(20, limit)`, `max_idle=limit` and the kernel pools' stretch, settle and decay
  (UNKNOWN U5: read the arguments `Conduit.__init__` passes, conduit.py:198-408); limited_quantity and queue ->
  `baseline_idle = max_idle = limit` (fixed capacity: nothing to trim while `count <= limit`).
''',
        '''- Sizes: elastic -> `baseline_idle=min(20, limit)`, `max_idle=limit` and the kernel pools' stretch, settle and decay
  (settled by S3, U5: Conduit builds both kernel pools with `baseline_idle=20, max_idle=256` and every other argument
  defaulted - stretch 0, settle 1800 s, decay 10% per 600 s - and the pool takes the same defaults); limited_quantity
  and queue -> `baseline_idle = max_idle = limit` (fixed capacity: nothing to trim while `count <= limit`).
''',
    ),
    (
        '''  (`id(obj)` -> the disposal-bearing `many` children recorded for that object); descriptive fields (spell id, spell
  name, binding name, frame, owner conduit id and name, mode, limit, timeout, reset names, disposal names); a
  borrowed Spell, read only by the registry's cold resolver (`Spell._spell_index_unless_cleaned`).
''',
        '''  (`id(obj)` -> the disposal-bearing `many` children recorded for that object) and `_orphaned_children` (records
  left by objects dropped while out, kept for teardown); descriptive fields (spell id, spell name, binding name,
  frame, owner conduit id, mode, limit, timeout, reset names, disposal names); a borrowed Spell behind the `spell`
  property, which raises once the pool is torn down (the registry's cold resolver reads it there, and ensuring the
  pool again re-points it at a Spell rebound under the same id).
''',
    ),
    (
        '''- Cold paths: `reserve()` - elastic: `count += 1` under the lock and `_note_miss()`, returns None; limited_quantity:
  raises ManagedSpellExhaustedError at `count >= limit`, else `count += 1`, returns None; queue: under the condition,
  loops `count < limit` -> `count += 1`, return None / an idle object -> return it / else wait the remaining timeout,
  raising at the deadline. `abandon(children)` - a failed build: `count -= 1`, notify, dispose the given children.
  `adopt(obj, children)` - record children under `id(obj)`; an entry already under that id belongs to a dead object
  and is disposed first. `destroy_object(obj)` (the base hook used by trims and cleanup) - the disposal methods, then
  the object's recorded children newest first; `count -= 1` (clamped at 0); notify. `create_object` raises
  RuntimeError (the plan builds, never the pool). `cleanup()` - destroy the idle objects, dispose the children recorded
  for objects still out, mark cleaned; failures are joined into one ExceptionGroup shaped like Creations' (one
  RuntimeError per failing method, chained). `describe()` - mode, limit, timeout, count, idle, children recorded.
''',
        '''- Cold paths (as built in S3): `reserve()` - elastic: `count += 1` under the lock and `_note_miss()`, returns None;
  limited_quantity: below the limit `count += 1`, returns None; at the limit returns an idle object released since the
  plan's empty pop, else raises ManagedSpellExhaustedError (so the refusal always means every object is out); queue:
  one deadline, then under the condition a free place -> `count += 1`, return None / an idle object -> return it /
  else wait the remaining time, raising at the deadline; a torn-down pool raises its torn-down RuntimeError (woken
  waiters included). `abandon(children, error)` - a failed build: `count -= 1`, notify, dispose the given children,
  their disposal failures added as notes on `error`. `adopt(obj, children)` - record children under `id(obj)`; a
  record already under that id (an object dropped while out) is kept as an orphan for teardown; adopting into a
  torn-down pool disposes the object and its children and raises the torn-down error. `destroy_object(obj)` (the base
  hook used by trims, raising resets and cleanup) - the disposal methods outside the lock, then the object's recorded
  children newest first; `count -= 1` (clamped at 0); notify. `create_object` and `acquire` raise RuntimeError (the
  plan builds, never the pool). `cleanup()` - under the condition drain the idle objects, swap the children maps for
  empty ones and wake every waiter; outside the lock dispose the idle objects newest first with their children, then
  the children recorded for objects still out, then the orphans; failures joined into one ExceptionGroup shaped like
  Creations' (one RuntimeError per failing method, chained); idempotent; the scalar fields stay as documented
  tombstones and the Spell is deleted. `describe()` - the base keys without `in_use_count`, plus identity, mode,
  limit, timeout, count, out count and children recorded.
''',
    ),
    (
        '''- UNKNOWN U6: `AbstractElasticPool.cleanup` failure handling and the fields it leaves
  (abstract_elastic_pool.py:228-248).
''',
        '''- Settled by S3 (U6): `AbstractElasticPool.cleanup` marks cleaned, destroys the idle objects one by one under `_lock`
  and stops at the first raising destroy, keeping every field; the pool overrides `cleanup` (above) instead of
  reusing it. A trim destroys outside the lock and re-pools the rest when one destroy raises.
''',
    ),
    (
        '''- `_managed_quantities: Dict[str, ManagedSpellQuantity]` beside `_creations`. Resolution reads `_creations` only, so
  lookups, live-creation probes and purge never meet a pool.
''',
        '''- `_managed_quantities: Dict[str, ManagedSpellQuantity]` beside `_creations`. Resolution reads `_creations` only, so
  lookups and purge never meet a pool; the live-creation probes read it through `get_managed_quantity(spell_id)`, a
  lock-free get.
''',
    ),
    (
        '''- `extract_spell_creations` (1302-1375) adds a `{"scope": "managed", "stored": pool}` row and gives the pool up
  (unregister); `restore_spell_creations` (1377-1474) takes it (register), first retiring a pool already under the id
  (cleanup, unregister) - the flip composes an empty pool for the active member before the move restores the moved one.
''',
        '''- `extract_spell_creations` adds a `{"scope": "managed", "disposable": False, "stored": pool}` row and gives the pool
  up (S4: unregister); `restore_spell_creations` takes it (S4: register), replacing a pool already under the id and
  cleaning the replaced one after the store lock, its failures raised as one ExceptionGroup once the restore
  completes (S4: unregister it) - the flip composes an empty pool for the active member before the move restores the
  moved one.
''',
    ),
    (
        '''- UNKNOWN U3: `clear_all` and `reset_for_pool` for pools (root stores hold pools; pooled lesser and spellspace stores
  never do). UNKNOWN U4: the ConduitMeld / SpellSpaceMeld readers (conduit_meld.py, spellspace_meld.py) - purge leaves
  a managed spell untouched (returns 0); the live-creation probe's managed answer (count > 0 proposed).
''',
        '''- Settled by S3 (U3): `reset_for_pool` (and `clear_all` through it) runs only on a lesser's store at pool return and a
  spellspace's store at exit, never on a root store, so neither meets a pool. (U4): `ConduitMeld._get_purge_creations`
  selects the caller's own store for a managed spell, where `Creations.purge` returns 0 before any lock;
  `SpellSpaceMeld.purge` keeps refusing it ("purge it from its authorized conduit"); both live-creation probes answer
  from the owner store's pool (`Meld._describe_managed_pool_status`: `is_live` when `count > 0`, `creation_count` the
  count, `storage_scope_kind` "managed_pool", `storage_owner_conduit_id` the owner root; no store or no pool -> 0).
  The Nexus static rooms treat managed like `many` (no stored object to hand out).
''',
    ),
    (
        '''- UNKNOWN U10: which versions `define_conduit_into_spells` stamps at conjure (spellbook_creation_system.py:1350-1375),
  so whether parked managed versions get a pool at conjure or at their first stamp.
''',
        '''- Settled by S3 (U10): conjure stamps only the Book's active spells (`define_conduit_into_spells` walks `_spells`); a
  post-conjure `bind` / `bind_inactive` stamps the new spell and the transfer flip the active member; `_apply_notch`
  stamps nothing. A version parked before conjure has no owner store, and so no pool, until a later stamp - the S5 miss
  must not assume a pool exists.
''',
    ),
    (
        '''- [ ] S3 STORY-2026-10-15-managed_quantity_pool - ManagedSpellQuantity, the exhaustion error, Creations integration,
      the store readers.
      tickets/stories/2026-10-15_managed_quantity_pool_story.md
''',
        '''- [x] S3 STORY-2026-10-15-managed_quantity_pool - ManagedSpellQuantity, the exhaustion error, Creations integration,
      the store readers.
      Landed 0.2.8243. tickets/stories/completed/2026-10-15_managed_quantity_pool_story.md
''',
    ),
    (
        "- None open with the owner. The UNKNOWNs U1-U10 in the Build Specification are read in source by their stories.\n",
        "- None open with the owner. U1-U6 and U10 are settled (S2, S3); U7-U9 and U11 are read in source by S4-S6.\n",
    ),
    (
        '''- Source revision: 0.2.8242 - S1 landed 0.2.8241 (the member, the matrix, route family "managed", Phase 6 rank 0);
  S2 landed 0.2.8242 (the four bind options, Spell fields, the managed-only id part, record 4.2.0 and replay).
- Done: Milestone 1; the epic rewritten and archived; the architecture patch doc; the seven stories; S1 and S2 landed
  and closed (tickets/stories/completed/); U1 and U2 settled (B5).
- Remaining: S3-S7 in order (Stories); the UNKNOWNs U3-U10 inside them; a component patch before each story's build.
''',
        '''- Source revision: 0.2.8243 - S1 landed 0.2.8241 (the member, the matrix, route family "managed", Phase 6 rank 0);
  S2 landed 0.2.8242 (the four bind options, Spell fields, the managed-only id part, record 4.2.0 and replay); S3
  landed 0.2.8243 (the pool, the exhaustion error, the Creations pool map, owner stamping, the probes and purge 0).
- Done: Milestone 1; the epic rewritten and archived; the architecture patch doc; the seven stories; S1-S3 landed and
  closed (tickets/stories/completed/); U1-U6 and U10 settled (B2, B3, B5).
- Remaining: S4-S7 in order (Stories); U7-U9 and U11 inside them; a component patch before each story's build.
''',
    ),
    (
        '''- Limits: the codex_bridge listing fails ("Codex app tool request failed", twice on 2026-10-15), so the tickets and
  the board row are the coordination record; hosted CI runs are the owner's (Not run).
''',
        '''- Limits: the codex_bridge listing fails ("Codex app tool request failed" on every try on 2026-10-15, last at 14:02Z),
  so the tickets and the board row are the coordination record; hosted CI runs are the owner's (Not run).
''',
    ),
    (
        '''- Next 1-3 actions: S3 - read AbstractElasticPool, Creations (maps, cleanup, extract/restore, clear_all,
  reset_for_pool) and the ConduitMeld / SpellSpaceMeld store readers whole (U3, U4, U5, U6, U10); write
  component_patch_managed_quantity_pool.md and its mapping note; red tests.
''',
        '''- Next 1-3 actions: rebuild the assets and bundles for 0.2.8243 and check them; S4 - read aether.py (the singleton
  slot, `__new__`, `__init__`'s hosted roots, cleanup and `_reset_singleton_for_tests`) and one hosted root whole
  (U11), write component_patch_release_managed_spell.md and its mapping note, then red tests.
''',
    ),
]

NOTE_ANCHOR = '''  NEXT: Apply the revert, validate, rebuild; then S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
'''
NOTE = f'''  NEXT: Apply the revert, validate, rebuild; then S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S3 landed as 0.2.8243: `ManagedSpellQuantity(AbstractElasticPool)` (sizes per mode, reserve, put_back with
    resets outside every lock, abandon / adopt / destroy_object with id-keyed children records, a cleanup that drains
    under the lock and disposes outside it), `ManagedSpellExhaustedError`, the Creations pool map (ensure and get,
    pools cleaned before the disposable registry, the `managed` extract/restore row, purge 0), owner stamping in
    `Spell._add_owned_conduit`, the probes' "managed_pool" answer and the static rooms. Green in both GIL modes on the
    new tests and on the unit, component and integration trees; the crystallizer integration tree ran a smoke shard
    only (S3 changes no crystallizer code). U3-U6 and U10 are settled in B2 and B3 with the as-built behaviour.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_quantity_pool_story.md:1-348
  - release_docs/next_version_release.md:365-387
  IMPACT: S4 registers pools at the four points where a store takes or gives one up (ensure, extract, restore,
    cleanup) and reads a pool's Spell only through `spell`; S5's miss relies on `reserve` serving an idle object
    before it refuses, and must not assume a pool exists for an unstamped version.
  NEXT: Rebuild and check for 0.2.8243, then S4 (U11 first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
'''

for old, new in REPLACEMENTS + [(NOTE_ANCHOR, NOTE)]:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor matched {count} times, nothing written:\n{old[:160]}")
    text = text.replace(old, new)

EPIC.write_text(text, encoding="utf-8")
print("epic updated", NOW)
