# Component patch: Managed Spell Pools - a same-id rebind gives its pool the new settings

## Metadata
- Patch ID: managed_settings_spell_id_2026_10_17
- Component: Managed Spell Pools (`ManagedSpellQuantity._rebind_spell`, its class, `__init__` and `spell` docstrings)
  and Creations (`ensure_managed_quantity`)
- Status: landed at 0.2.8254 and promoted to the system documents and the graph; active with the story until
  part B
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T00:10:00Z
- Updated: 2026-10-18T02:05:25Z

## Component Purpose and Boundary
- Current boundary: `ensure_managed_quantity(spell)` composes one pool per (store, spell_id) at owner stamping; when
  the store already holds one (a definition removed with `cleanup_spell` and bound again under the same
  content-stable id, as a slotted replacement meets its slot, 0.2.8219), it calls `pool._rebind_spell(spell)` under
  the store lock, which re-points `_spell` and the class key and assumes the settings equal ("hence the same options
  and disposal names" - true while the settings were in the spell_id).
- Target boundary: the same id can now carry other settings, so `_rebind_spell` makes the pool's policy the new
  Spell's - mode, limit, queue timeout, reset names, and the retention sizes they imply - and re-points the disposal
  list; `ensure_managed_quantity` calls it after releasing the store lock.

## Before/After Behavior Summary
- Before: a rebind with other settings never meets the old pool (another spell_id); its new pool starts at count 0
  while the old pool keeps counting the objects it built (probe R1 on the tree).
- After: the rebind meets the old pool. Its objects - idle and out - stay alive and counted; leases from then on follow
  the new settings; a release of an object built before the rebind returns to this one pool (probe R1 on the
  prototype). Unchanged settings (an ownership transfer's restamp of the same Spell, a rebind with equal settings)
  re-point the Spell and change nothing else - the elastic target and its decay clock are kept.

## Interface Deltas
- Inputs: none new (`_rebind_spell(spell)` stays internal, called only by `ensure_managed_quantity`).
- Outputs: `describe()` and the `mode`, `limit`, `timeout_seconds` and `reset_method_names` properties report the
  current Spell's settings after a rebind.
- Error semantics: none new. `ManagedSpellExhaustedError` reports the limit in force when it is raised.

## State and Lifecycle Deltas
- Owned state changes, under the pool lock, only when a setting differs: `_mode`, `_limit`, `_timeout_seconds`,
  `_reset_method_names`, `_notify_on_return` (queue only), and the base pool's `_baseline_idle`, `_max_idle`,
  `_target_idle` (reset to the new baseline) and `_decay_step`, sized exactly as `__init__` sizes them (elastic:
  baseline min(20, limit), max limit; limited_quantity and queue: baseline = max = limit). Always: `_spell`,
  `_managed_class`, `_disposal_method_names` (the new Spell's list, equal in content, since disposal names stay in
  the spell_id). `_count`, `_idle`, the children maps and the pressure/decay clocks are kept.
- Lifecycle/cleanup changes: none; a rebind destroys nothing. A count above a smaller new limit stays until destroys
  bring it down: limited_quantity and queue build again only below the limit, and their fixed capacity evicts the
  oldest idle object on each release above it (probe R3); elastic trims through its band.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: the stranded count after a settings change (S6's Q2 and the tree's R1).
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Needs the binding fingerprint change (same notch): only a settings-free spell_id lets a settings change meet its
   pool.
2. Keeps the managed epic's rulings: nothing is destroyed by a notch, a cleanup_spell or a rebind; no identity record.

## Validation Expectations
- Unit (ManagedSpellQuantity): a rebind with equal settings keeps the retention state; a new limit, a new timeout and
  new reset names take effect; elastic -> limited_quantity resizes to fixed capacity and keeps count and idle; queue
  -> limited_quantity stops waking on release and wakes current waiters; limited_quantity -> queue makes the next
  miss wait; the disposal list is re-pointed; a torn-down pool is never re-composed (a store that holds a pool is
  live).
- Unit (Creations): `ensure_managed_quantity` meets the pool under the same id and calls `_rebind_spell` with the store
  lock released (a lock probe), then registers the pool once.
- Multithreaded: a rebind racing leases and releases under 8 threads leaves `count` equal to the objects alive and
  never above a limited_quantity limit once the count has come down below it.
- Integration: probe R1-R3 as tests on a real Spellbook, GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none of its own (the architecture patch carries the scope question).

## Context / Handoff Summary
- What changed: nothing yet; the prototype's `_rebind_spell` and `ensure_managed_quantity` passed every managed suite
  except the tests that build a second version from one class's settings (S6's MEASURE note).
- Remaining risks: a release racing the rebind runs either the old or the new reset names (one read); accepted and
  documented, as a release racing teardown is.
- Next entrypoint: code_description_patch_managed_pool_rebind.md.
