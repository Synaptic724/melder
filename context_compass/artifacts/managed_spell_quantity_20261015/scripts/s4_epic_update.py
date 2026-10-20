"""S4 turn-in: update the epic's Build Specification (B1, B4), Open Questions, Stories, Notes and resume view."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
EPIC = ROOT / "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"

edits = [
    (
        """- Package root: `ManagedSpellMode`, `ReleaseManagedSpell` and `ManagedSpellExhaustedError` join the flat root next to
  `Existence` (the root's own contract: every user-facing name is importable from it); the lease type is imported
  from its module. Recorded as a build decision for the owner's review (Decision Log, 2026-10-15).
""",
        """- Package root: `ManagedSpellMode`, `ReleaseManagedSpell`, `ManagedSpellLease` and `ManagedSpellExhaustedError` join
  the flat root next to `Existence` (the owner's root ruling of 2026-07-19: user-held surfaces, front-facing enums and
  user-catchable errors reach the flat facade). The lease joined in S4 (its DECISION note); recorded as build
  decisions for the owner's review (Decision Log, 2026-10-15).
""",
    ),
    (
        """- `src/melder/aether/conduit/creations/release_managed_spell.py`: a process singleton built like Aether (owner,
  2026-10-15): `__new__` with a double-checked class-level `_instance` guard, `_initialized`, and a cleanup that resets
  the singleton state. Aether creates and owns it - constructed eagerly in `Aether.__init__` beside the other hosted
  roots and cleaned by Aether's cleanup; `ReleaseManagedSpell()` returns that instance. The registry is instance
  state: `_pools_by_class: Dict[type, Tuple[ManagedSpellQuantity, ...]]` republished whole (copy-on-write) under a
  leaf `_lock` held only to publish; every read is lock-free. Releasing is a call on this singleton, never an Aether
  verb (the 2026-10-13 ruling stands). It has the reset-singleton feature Aether has (owner, 2026-10-15): resetting
  clears the instance and its registry so the next `ReleaseManagedSpell()` (or the next Aether) builds a fresh one -
  the same reset hook and naming as Aether's. UNKNOWN U11: its place in Aether's construction and cleanup order and
  the exact reset hook Aether and its hosted roots use (read aether.py:116-332 and one hosted root in S4).
- `register(pool)` / `unregister(pool)` are called by Creations only, when a store takes or gives up a pool.
""",
        """- `src/melder/aether/conduit/creations/release_managed_spell.py` (as built in S4; U11 settled): a process singleton
  with the hosted roots' shape (owner, 2026-10-15) - `_instance`, a class `_singleton_lock`, `_initialized`, a
  double-checked `__new__`, a once-only `__init__(*, aether=None)` under the lock that refuses a first construction
  without its host (ValueError, bookkeeping reset), a `cleanup()` that publishes empty maps as tombstones, keeps
  `_lock` and resets the bookkeeping, `_reset_singleton_for_tests()` (a half-built husk's AttributeError ignored, the
  bookkeeping cleared in a `finally`) and `_live_instance()` (the stores' teardown lookup; never constructs).
  `Aether.__init__` builds it last, after Nexus (`ReleaseManagedSpell(aether=self)`); `Aether.cleanup` cleans it
  right after the frames, whose stores unregister their pools first; `ReleaseManagedSpell()` returns the instance,
  and after a reset the next Aether builds a fresh one (a bare `ReleaseManagedSpell()` before it refuses). Like every
  hosted root it stays published when the frames' teardown raises (Aether resets only its own bookkeeping).
  Releasing is a call on this singleton, never an Aether verb (the 2026-10-13 ruling stands). The registry is
  instance state: `_pools_by_class: Dict[type, Tuple[ManagedSpellQuantity, ...]]` (the hot read) and
  `_registrations: Dict[int, Tuple[type, str]]` (`id(pool)` -> class, holding root id), republished whole
  (copy-on-write) under a leaf `_lock` held only to publish; every read is lock-free.
- `register(pool, *, root_conduit_id)` / `unregister(pool)` are called by Creations only, when a store takes or gives
  up a pool: ensure registers after its store lock; extract and cleanup unregister; restore unregisters a pool it
  replaces, registers the one it installs, then cleans the replaced one. `register` is idempotent, records the
  holding root (a pool's own `owner_conduit_id` is fixed at construction and keeps naming its first root after a
  move) and re-keys a rebind that brought another class object; `unregister` does nothing on a cleaned registry.
""",
    ),
    (
        """  pool and no filter -> `pool.put_back(obj)`. Otherwise the cold resolver: keep pools whose spell id equals `spell_id`
  and whose owner root is `conduit`'s root; with no filter and several pools, keep the one whose spell is the active
  version of its index; exactly one must remain, else ValueError listing every candidate (spell id, binding name,
  frame, root) and the keywords that pick one. A class with no pool -> ValueError (not a managed class in any live
  root). Release never needs a conduit.
""",
        """  pool and no filter -> `pool.put_back(obj)`. Otherwise the cold resolver: keep pools whose spell id equals `spell_id`
  and whose holding root is `conduit`'s root (a lesser names its root); when several remain, keep those whose version
  its index selects (cleanup-safe reads: `ManagedSpellQuantity._spell_unless_cleaned`,
  `Spell._spell_index_unless_cleaned`, `SpellIndex._is_selected_unless_cleaned`); exactly one must remain, else
  ValueError listing every candidate (spell id, binding, frame, root, active) and the keywords that pick one. A class
  with no pool -> ValueError (not a managed class in any live root). Release never needs a conduit. Measured (S4): a
  bound `release` adds about 50 ns over `put_back`; the `ReleaseManagedSpell()` call itself costs about 70 ns, as
  `Aether()` does, so hot loops bind it once.
""",
    ),
    (
        """- None open with the owner. U1-U6 and U10 are settled (S2, S3); U7-U9 and U11 are read in source by S4-S6.
""",
        """- None open with the owner. U1-U6, U10 and U11 are settled (S2-S4); U7-U9 are read in source by S5 and S6.
""",
    ),
    (
        """- [ ] S4 STORY-2026-10-15-release_managed_spell - the registry, release / managed / release_all / describe, the lease,
      package-root exports.
      tickets/stories/2026-10-15_release_managed_spell_story.md
""",
        """- [x] S4 STORY-2026-10-15-release_managed_spell - the registry, release / managed / release_all / describe, the lease,
      package-root exports.
      Landed 0.2.8244. tickets/stories/completed/2026-10-15_release_managed_spell_story.md
""",
    ),
]

MEASURE = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S4 landed as 0.2.8244: `ReleaseManagedSpell`, a hosted-root singleton Aether builds last and cleans after
    the frames, keyed by class with copy-on-write maps and a lock-free release (one dict get, then `put_back`); the
    cold resolver (spell id, holding root, the selected version, precise ValueErrors); `managed`, `release_all`,
    `describe`; `ManagedSpellLease`; the Creations register/unregister calls; four package-root exports. Green in
    both GIL modes on the new tests and on the whole tree (unit, component, integration including all 279
    crystallizer integration ids, the experimentation trees). Routing: a bound release +50 ns over `put_back`; the
    `ReleaseManagedSpell()` call +70 ns, as `Aether()`. U11 is settled in B4; B1 lists the lease.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_release_managed_spell_story.md:1-330
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s4_validation_index.md:1-54
  - release_docs/next_version_release.md:308-420
  IMPACT: S5's `Conduit.managed_spell_meld` returns the lease and its emitted plans lease from the pools the registry
    routes back to; S6's moves keep the holding root right through extract and restore.
  NEXT: Rebuild and check for 0.2.8244, then S5 - read the codegen seams of B7 whole (U7, U8), the component patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""

HANDOFF_OLD_START = "- Source revision: 0.2.8243 - S1 landed 0.2.8241"
epic = EPIC.read_text(encoding="utf-8")
for old, new in edits:
    assert epic.count(old) == 1, old[:80]
    epic = epic.replace(old, new)
anchor = "## Closure Confirmation"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, MEASURE + anchor)

start = epic.index("## Context / Handoff Summary")
end = epic.index("## Project-Specific Additions")
handoff = """## Context / Handoff Summary
- Scope: build `Existence.managed_spell_quantity` end to end (Build Specification B1-B12) in seven stories, one notch
  per landed story, rebuild last.
- Controlling decisions: the Decision Log (owner rulings 2026-10-12 to 2026-10-15; melder_0's build decisions of
  2026-10-15, and the S4 story's DECISION note: the lease on the root, the holding root). The objects handed out are
  the agents'; Melder keeps the structure right.
- Source revision: 0.2.8244 - S1 landed 0.2.8241 (the member, the matrix, route family "managed", Phase 6 rank 0);
  S2 0.2.8242 (the four bind options, Spell fields, the managed-only id part, record 4.2.0 and replay); S3 0.2.8243
  (the pool, the exhaustion error, the Creations pool map, owner stamping, the probes, purge 0); S4 0.2.8244
  (`ReleaseManagedSpell`, the lease, the Creations register/unregister calls, the root exports).
- Done: Milestone 1; the epic rewritten and archived; the architecture patch doc; the seven stories; S1-S4 landed and
  closed (tickets/stories/completed/); U1-U6, U10 and U11 settled (B2-B5).
- Remaining: S5-S7 in order (Stories); U7-U9 inside them; a component patch before each story's build.
- Limits: the codex_bridge listing fails ("Codex app tool request failed" on every try on 2026-10-15, last at 14:49Z),
  so the tickets and the board row are the coordination record; hosted CI runs and coverage are the owner's (Not run).
- Owners: melder_0 builds; the owner accepts; no other lane holds a file of this one.
- Next 1-3 actions: rebuild the assets and bundles for 0.2.8244 and check them; S5 - read the codegen seams of B7
  whole and answer U7 and U8 from source, take a baseline emission capture, write the S5 component and
  code-description patches and the mapping note; then red tests.

"""
epic = epic[:start] + handoff + epic[end:]
epic = epic.replace("- Updated: 2026-10-15T14:05:52Z", f"- Updated: {NOW}")
EPIC.write_text(epic, encoding="utf-8")
print("epic updated", NOW)
