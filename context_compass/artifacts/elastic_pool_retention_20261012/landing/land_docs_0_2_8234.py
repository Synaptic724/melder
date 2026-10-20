"""
Land the 0.2.8234 (elastic pool retention) text into src_architecture, src_components and tests_components.

Usage: python land_docs_0_2_8234.py <system_docs dir> <UTC timestamp>
Every anchor must match exactly once; LF documents.
"""
import pathlib
import sys


def edit(path: pathlib.Path, pairs: list) -> None:
    """Apply (old, new) pairs, each exactly once."""
    raw = path.read_bytes()
    assert b"\r\n" not in raw, path
    text = raw.decode("utf-8")
    for old, new in pairs:
        assert text.count(old) == 1, (path.name, old[:90])
        text = text.replace(old, new)
    for number, line in enumerate(text.split("\n"), 1):
        if len(line) > 120 and " " in line.strip().lstrip("- ").strip("`"):
            pass
    path.write_bytes(text.encode("utf-8"))
    print(path.name, "edited", len(pairs))


def main() -> int:
    docs = pathlib.Path(sys.argv[1])
    now = sys.argv[2]

    edit(docs / "src_architecture.md", [
        ("- Updated: 2026-10-11\n", "- Updated: 2026-10-12\n"),
        ("## Operational Invariants\n", """## Operational Invariants
- Elastic pool retention (2026-10-12, 0.2.8234): the kernel pools keep what demand needed and let it go when demand
  falls. Every conduit's `SpellSpacePool` and every normal root's `ConduitPool` are built with `baseline_idle` 20 and
  `max_idle` 256. A miss always builds (live objects are never capped) and records pressure (`_note_miss`); a return
  that leaves at most 20 idle is one append and one compare, with no clock read and no lock. Above that,
  `_rebalance_after_return` reads the clock: under pressure (a miss within the settle time, 30 minutes) the target
  rises to the idle count a return observes, up to 256, and only shells above 256 are trimmed, so a burst is kept
  whole even while its returns race and its repeat builds nothing; once settled, the target falls by 10% of its
  stretched value every 10 minutes, with the steps of a quiet period applied together at the next return, never
  below 20, and the oldest idle shells are trimmed one decay step per return and destroyed outside the pool lock. A
  destroy that raises propagates from that return and the shells detached after it go back to the pool. A pool
  built with `max_idle == baseline_idle` keeps the one-eviction return with no clock read. There is no timer thread:
  a pool that sees no return keeps its shells. Through 0.2.8233 both kernel pools were pinned at 20/20, so every
  shell beyond 20 out at once was built and destroyed on each burst, and the base class's stretch (+200% per miss)
  and decay (only inside an overflowing return) never ran for them.
  EVIDENCE: `src/melder/utilities/general_base/abstract_elastic_pool.py:AbstractElasticPool._note_miss`,
  `AbstractElasticPool._rebalance_after_return`, `AbstractElasticPool._rebalance_locked`,
  `src/melder/aether/conduit/spell_space/spell_space_pool.py:SpellSpacePool.release`,
  `src/melder/aether/conduit/conduit_pool.py:ConduitPool.return_lesser_conduit` and
  `src/melder/aether/conduit/conduit.py:Conduit.__init__`.
"""),
        ("""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7178
  loc: 7178
  verified_at: 2026-10-11T20:29:47Z
  note: conduit lifecycle and meld facade; `cleanup_spell` emits the index destroy the Book reports (0.2.8231);
    `find_contracted_spell` and `inspect_spell` take no conduit lock (0.2.8232).
""", f"""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7188
  loc: 7188
  verified_at: {now}
  note: conduit lifecycle and meld facade; `cleanup_spell` emits the index destroy the Book reports (0.2.8231);
    `find_contracted_spell` and `inspect_spell` take no conduit lock (0.2.8232); builds its SpellSpacePool and a
    root's ConduitPool elastic, baseline 20 / max 256 (0.2.8234).
- path: `src/melder/aether/conduit/conduit_pool.py`
  start_line: 1
  end_line: 165
  loc: 165
  verified_at: {now}
  note: root-owned lesser pool; a miss records pressure and a return above 20 idle runs the elastic band (0.2.8234).
"""),
        ("""- path: `src/melder/aether/conduit/spell_space/spell_space_pool.py`
  start_line: 1
  end_line: 301
  loc: 301
  verified_at: 2026-09-27T23:41:28Z
  note: spellspace pool; release sets and acquisition clears the lease flag.
""", f"""- path: `src/melder/aether/conduit/spell_space/spell_space_pool.py`
  start_line: 1
  end_line: 307
  loc: 307
  verified_at: {now}
  note: spellspace pool; release sets and acquisition clears the lease flag; misses record pressure and returns
    above 20 idle run the elastic band (0.2.8234).
"""),
        ("""- path: `src/melder/utilities/general_base/cleanable.py`
  start_line: 1
""", f"""- path: `src/melder/utilities/general_base/abstract_elastic_pool.py`
  start_line: 1
  end_line: 599
  loc: 599
  verified_at: {now}
  note: elastic pool base of both kernel pools: stretch under pressure, timed decay with catch-up, bounded trims
    outside the lock, the fixed-capacity eviction (0.2.8234).
- path: `src/melder/utilities/general_base/cleanable.py`
  start_line: 1
"""),
        ("""- `src/melder/aether/conduit/spell_space/spell_space_pool.py`
- `src/melder/aether/conduit/spell_space/spell_space_thread_state.py`
""", """- `src/melder/aether/conduit/spell_space/spell_space_pool.py`
- `src/melder/aether/conduit/conduit_pool.py`
- `src/melder/utilities/general_base/abstract_elastic_pool.py`
- `src/melder/aether/conduit/spell_space/spell_space_thread_state.py`
"""),
        ("## Context / Handoff Summary\n\n", """## Context / Handoff Summary

2026-10-12 elastic pool retention (0.2.8234): the kernel pools keep what a burst needed, up to 256, and decay back to
20 once no miss has happened for 30 minutes - a miss records pressure, a return above 20 idle stretches, decays (with
catch-up) or trims outside the lock, and a fixed-capacity pool keeps the old eviction. The operational invariants,
the code map and the sources carry it; the component map carries the per-pool rules. Citations into conduit.py moved
10 lines with the prewarm docstrings, and the stale ones for the index-mutation verbs and `Conduit.link`'s type
check (off by 11 before this change) now point at their code.

"""),
    ])

    edit(docs / "src_components.md", [
        ("- Updated: 2026-10-11\n", "- Updated: 2026-10-12\n"),
        ("""### Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Execution scope for resolving spells and managing object lifecycles.

""", """### Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Execution scope for resolving spells and managing object lifecycles.

Elastic pool retention (2026-10-12, 0.2.8234): the conduit's `SpellSpacePool` and a normal root's `ConduitPool` are
built with baseline 20 and max 256 (`Conduit.__init__`; `upgrade_to_normal` builds the new root's pool the same way).
`ConduitPool.create_object` records a miss (`_note_miss`) before `create_lesser_conduit` builds the lesser;
`return_lesser_conduit` appends and, above 20 idle, runs `_rebalance_after_return`: a burst returning within 30
minutes of a miss raises the target to the idle count (up to 256) and is kept whole, so its repeat reuses every
shell; once quiet the target falls 10% per 10 minutes and the oldest shells are permanently cleaned outside the pool
lock. `prewarm_lesser_conduits` and `prewarm_spellspaces` clamp to 256 and their shells above 20 decay the same way.
Through 0.2.8233 both pools were 20/20 and every shell past 20 out at once was destroyed on its return.
EVIDENCE: `src/melder/aether/conduit/conduit_pool.py:ConduitPool.create_object`,
`ConduitPool.return_lesser_conduit`, `src/melder/aether/conduit/conduit.py:Conduit.__init__`,
`Conduit.prewarm_lesser_conduits` and
`src/melder/utilities/general_base/abstract_elastic_pool.py:AbstractElasticPool._rebalance_locked`.

"""),
        ("""- Own one `SpellSpacePool` for request-local spellspace surfaces and one
  `ConduitPool` for lesser-conduit reuse.
""", """- Own one `SpellSpacePool` for request-local spellspace surfaces and one
  `ConduitPool` for lesser-conduit reuse. Both are elastic: 20 idle always kept,
  up to 256 after a burst, decaying back when quiet (0.2.8234).
"""),
        ("""### Component: Creations and SpellSpace
Purpose:
- Instance lifecycle registry for Conduits and scoped spellspaces.

""", """### Component: Creations and SpellSpace
Purpose:
- Instance lifecycle registry for Conduits and scoped spellspaces.

SpellSpace pool retention (2026-10-12, 0.2.8234): `SpellSpacePool.acquire` and `acquire_untracked` record a miss
(`_note_miss`) after building a space; `release` sets the lease flag, appends and, above 20 idle, runs the elastic
band of `AbstractElasticPool`, so a burst of nested or concurrent managed spaces past 20 is kept (up to 256) and
reused, then decays when quiet; surplus spaces are destroyed oldest first outside the pool lock. The lease flag and
the release order are unchanged.
EVIDENCE: `src/melder/aether/conduit/spell_space/spell_space_pool.py:SpellSpacePool.acquire`,
`SpellSpacePool.acquire_untracked`, `SpellSpacePool.release` and
`src/melder/utilities/general_base/abstract_elastic_pool.py:AbstractElasticPool._rebalance_after_return`.

"""),
        ("""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7178
  loc: 7178
  verified_at: 2026-10-11T20:29:47Z
""", f"""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7188
  loc: 7188
  verified_at: {now}
"""),
        ("""- path: `src/melder/aether/conduit/spell_space/spell_space_pool.py`
  start_line: 1
  end_line: 301
  loc: 301
  verified_at: 2026-09-27T23:41:28Z
""", f"""- path: `src/melder/aether/conduit/spell_space/spell_space_pool.py`
  start_line: 1
  end_line: 307
  loc: 307
  verified_at: {now}
"""),
        ("- `src/melder/aether/conduit/conduit_pool.py` - Root-conduit-owned elastic pool scaffold for reusable lesser conduits\n",
         "- `src/melder/aether/conduit/conduit_pool.py` - Root-conduit-owned elastic pool for reusable lesser conduits\n"),
        ("- `src/melder/utilities/general_base/abstract_elastic_pool.py` - Reusable bounded elastic object-pool base\n",
         "- `src/melder/utilities/general_base/abstract_elastic_pool.py` - Elastic object-pool base: stretch, timed decay, bounded trims\n"),
        ("## Context / Handoff Summary\n\n", """## Context / Handoff Summary

2026-10-12 elastic pool retention (0.2.8234): Conduit Runtime carries the kernel pool sizes (20/256), the ConduitPool
miss and return paths and the prewarm ceiling; Creations and SpellSpace carries the SpellSpacePool paths; the code map
extents of conduit.py and spell_space_pool.py are remeasured, and the conduit.py citations moved 10 lines (those of
the index-mutation verbs and `Conduit.link`'s type check, stale by 11 before, now point at their code).

"""),
    ])

    edit(docs / "tests_components.md", [
        ("- Updated: 2026-10-10\n", "- Updated: 2026-10-12\n"),
        ("""  at conjure, with system caching cold and warm, and through the SpellSpace door; provider-first and
  bind-before-conjure controls
Key Files (C1):
""", """  at conjure, with system caching cold and warm, and through the SpellSpace door; provider-first and
  bind-before-conjure controls
- elastic kernel pools (0.2.8234): a repeat burst of 30 lessers or 30 nested managed spellspaces reuses every
  shell, a burst past 256 keeps 256, the root pool decays to 20 after the settle time with catch-up (fake clock
  through `_time_func`) and stretches again, and prewarming keeps 40 of each
Key Files (C1):
"""),
        ("""- `tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py` (2026-09-30)
""", """- `tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py` (2026-09-30)
- `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py` (elastic pools, 2026-10-12)
"""),
        ("""- the Cleanable cleanup contexts (0.2.8203): `using_cleanup()` and `async_using_cleanup()` clean up at
  most once and let the cleanup error propagate, chained to the block's error
""", """- the Cleanable cleanup contexts (0.2.8203): `using_cleanup()` and `async_using_cleanup()` clean up at
  most once and let the cleanup error propagate, chained to the block's error
- the elastic pool algorithm (0.2.8234), one test per rule with a fake clock: a miss records pressure, a burst
  is kept whole (with optional headroom, capped at `max_idle`), returns without pressure trim, decay waits for the
  settle time, steps per interval, catches up and stops at the baseline, a later miss postpones it, a fixed pool
  evicts without the clock, and a failing destroy keeps the rest of its trim pooled; concurrent band returns and a
  concurrent burst stay within bounds
"""),
        ("""- path: `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py`
  start_line: 1
  end_line: 243
  loc: 243
  verified_at: 2026-09-26T22:11:36Z
""", f"""- path: `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py`
  start_line: 1
  end_line: 265
  loc: 265
  verified_at: {now}
"""),
        ("""- path: `tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py`
  start_line: 1
  end_line: 286
  loc: 286
  verified_at: 2026-09-30T20:10:45Z
""", f"""- path: `tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py`
  start_line: 1
  end_line: 286
  loc: 286
  verified_at: 2026-09-30T20:10:45Z
- path: `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py`
  start_line: 1
  end_line: 169
  loc: 169
  verified_at: {now}
"""),
        ("## Context / Handoff Summary\n\n", """## Context / Handoff Summary

2026-10-12 elastic pool retention (0.2.8234): the Aether Component Cluster gains
`test_kernel_pool_elastic_retention.py` (repeat bursts, the 256 cap, decay and catch-up on the root pool, prewarm
past 20) and the Utilities Unit Cluster's elastic-pool files carry the new algorithm, one test per rule; two tests
that force a pool to keep nothing now set its baseline and ceiling too.

"""),
    ])
    return 0


if __name__ == "__main__":
    sys.exit(main())
