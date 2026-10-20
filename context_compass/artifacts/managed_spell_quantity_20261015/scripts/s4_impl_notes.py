"""S4: record the as-built FACT and the build DECISION in the story, refresh its resume view and the board row."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STORY = ROOT / "tickets/stories/2026-10-15_release_managed_spell_story.md"
BOARD = ROOT / "attention_board.md"

FACT = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S4 as built on the working copy (0.2.8243, not yet notched), re-read after the compaction.
    `ReleaseManagedSpell(Cleanable)` has the hosted-root shape: a double-checked `__new__`; a once-only
    `__init__(*, aether=None)` under `_singleton_lock` that refuses a first construction without its host
    (ValueError, bookkeeping cleared); `cleanup()` publishes empty maps as tombstones, keeps `_lock` and resets
    `_instance`/`_initialized`; `_reset_singleton_for_tests()` ignores a husk's AttributeError and clears the
    bookkeeping in a `finally`; `_live_instance()` serves the stores' teardown. State: `_pools_by_class` (class ->
    tuple of pools) and `_registrations` (`id(pool)` -> class, holding root id), copy-on-write under the leaf `_lock`,
    read lock-free. `register(pool, *, root_conduit_id)` is idempotent, only moves the root on a restore into another
    root and re-keys a rebind that brought another class; `unregister` does nothing on a cleaned registry.
    `release` / `managed`: one dict get by `type(obj)`; one pool and no filter -> `put_back` / the lease; else
    `_resolve_pool` (cleaned, filter types, the conduit's root, then spell id and holding root, then the version its
    index selects; not-managed, ambiguity and no-match ValueErrors). `release_all` attempts every object, then one
    ExceptionGroup; `describe(cls)` adds `holding_conduit_id` and `active_version` to each pool snapshot.
    `ManagedSpellLease` releases once (released even when the put-back raises) and `__exit__` never suppresses.
    Aether builds the registry last (after Nexus) and cleans it right after the frames. Creations registers at
    ensure (after the store lock), unregisters at extract and cleanup, and on restore unregisters the replaced pool,
    registers the installed one, then cleans the replaced one. Supporting reads: `ManagedSpellQuantity.managed_class`,
    `_spell_unless_cleaned` (the Spell is deleted under the pool lock now) and `SpellIndex._is_selected_unless_cleaned`.
    The package root exports ReleaseManagedSpell, ManagedSpellLease, ManagedSpellMode and ManagedSpellExhaustedError.
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:100-261
  - src/melder/aether/conduit/creations/release_managed_spell.py:263-349
  - src/melder/aether/conduit/creations/release_managed_spell.py:351-507
  - src/melder/aether/conduit/creations/release_managed_spell.py:509-680
  - src/melder/aether/conduit/creations/managed_spell_lease.py:11-161
  - src/melder/aether/conduit/creations/creations.py:324-397
  - src/melder/aether/conduit/creations/creations.py:1116-1249
  - src/melder/aether/conduit/creations/creations.py:1476-1697
  - src/melder/aether/aether.py:140-266
  - src/melder/aether/aether.py:268-361
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:198-313
  - src/melder/aether/spellbook/bind/spell_index.py:358-388
  - src/melder/__init__.py:77-95
  - src/melder/__init__.py:210-284
  IMPACT: B4 holds as specified, with the two additions in the DECISION below. S5's `Conduit.managed_spell_meld`
    returns this lease; S6's moves keep the registry right through extract and restore.
  NEXT: Run the component and integration shards in both GIL modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Build decisions inside the owner's go-ahead, open to the owner's review. (1) The lease joins the package
    root beside the three names B1 listed: the root is the deliberate flat facade (owner ruling 2026-07-19) and the
    lease is a user-held surface. (2) `register` takes `root_conduit_id` and the registry records each pool's holding
    root, because a pool's own `owner_conduit_id` is fixed at construction and keeps naming its first root after a
    move; the `conduit=` filter and `describe` read the holding root. (3) `cleanup` publishes empty maps instead of
    deleting them, so a lock-free release racing teardown misses and raises the cleaned error from the cold path.
    (4) The pool deletes its Spell under its lock and offers `_spell_unless_cleaned`, and SpellIndex gained
    `_is_selected_unless_cleaned`, so the resolver's active-version read never raises under a racing teardown.
    (5) A failed frame teardown leaves the registry published, as it leaves every hosted root: Aether's cleanup
    resets only its own bookkeeping (BUG-149) and the next Aether adopts the live registry.
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:176-207
  - src/melder/aether/conduit/creations/release_managed_spell.py:263-311
  - src/melder/aether/conduit/creations/release_managed_spell.py:577-640
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:130-196
  - src/melder/aether/aether.py:300-361
  - context_compass/system_docs/patches/active/melder_init_composition_2026_07_19/architecture_patch.md:6-38
  IMPACT: B1 lists four root exports and B4 the holding root (epic update at closure). S6 owns whether a moved pool's
    `owner_conduit_id` (its `describe()` key) should follow the move; the registry is right either way.
  NEXT: Run the component and integration shards in both GIL modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""

HANDOFF_OLD = """## Context / Handoff Summary
- Scope: S4 - registry, lease, exports.
- State: ready, blocked on S3.
- Next: component patch.
"""
HANDOFF_NEW = """## Context / Handoff Summary
- Scope: S4 - the Aether-owned `ReleaseManagedSpell` singleton, `ManagedSpellLease`, the Creations register and
  unregister calls, the cleanup-safe reads they need, the package-root exports.
- State: implemented on the working copy (0.2.8243; not notched, nothing committed). New and changed tests green in
  both GIL modes (197 each); unit trees green in both modes (aether + spellbook 6874 each; the rest 2508 passed,
  3 skipped, 7 xfailed each). Runs: artifacts/managed_spell_quantity_20261015/runs/s4_*.
- Decisions: the FACT and DECISION notes of this update (the lease export, the holding root).
- Remaining: component and integration shards in both modes (crystallizer integration included); the routing-cost
  probe; the MEASURE note; notch 0.2.8244 and the release note; epic B1/B4; closure and board sync; rebuild last.
- Limits: codex_bridge fails ("Codex app tool request failed"); hosted CI is the owner's (Not run).
- Next: the component shards in both GIL modes.
"""

CHECK_OLD = """- [ ] Component patch and mapping note.
- [ ] Red tests: routing, filters, ambiguity, not managed, lease, describe, release_all aggregation,
      register/unregister following the store."""
CHECK_NEW = """- [x] Component patch and mapping note.
- [x] Red tests: routing, filters, ambiguity, not managed, lease, describe, release_all aggregation,
      register/unregister following the store."""

story = STORY.read_text(encoding="utf-8")
anchor = "## Closure Confirmation"
assert story.count(anchor) == 1
assert story.count(HANDOFF_OLD) == 1, "handoff anchor"
assert story.count(CHECK_OLD) == 1, "checklist anchor"
story = story.replace(anchor, FACT + anchor)
story = story.replace(HANDOFF_OLD, HANDOFF_NEW)
story = story.replace(CHECK_OLD, CHECK_NEW)
story = story.replace("- Updated: 2026-10-15T14:16:58Z", f"- Updated: {NOW}")
STORY.write_text(story, encoding="utf-8")

board = BOARD.read_text(encoding="utf-8")
row_old = ("| melder_object_pools | in_progress | implementation | claude | melder_0 | none | S4: read aether.py's singleton "
           "slot, init, cleanup and reset hook plus one hosted root whole (U11), then the S4 patch and mapping note. |")
row_new = ("| melder_object_pools | in_progress | validation | claude | melder_0 | none | S4: run the component and "
           "integration shards in both GIL modes, then the routing probe, notch 0.2.8244, release note and closure. |")
assert board.count(row_old) == 1, "board row"
board = board.replace(row_old, row_new)
old_tail = "| tickets/stories/2026-10-15_release_managed_spell_story.md | 2026-10-15T14:06:33Z | REQUIRED |"
assert board.count(old_tail) == 1, "board tail"
board = board.replace(old_tail, f"| tickets/stories/2026-10-15_release_managed_spell_story.md | {NOW} | REQUIRED |")
BOARD.write_text(board, encoding="utf-8")
print("ok", NOW)
