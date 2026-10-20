# Component patch: ReleaseManagedSpell, the lease and the root exports (managed_spell_quantity_2026_10_15, S4)

Components: ReleaseManagedSpell (new, conduit/creations), ManagedSpellLease (new, conduit/creations), Aether
(constructs, owns and cleans the registry), Creations (registers and unregisters the pools it takes and gives up),
ManagedSpellQuantity (`managed_class`), SpellIndex (`_is_selected_unless_cleaned`), the package root (four exports).
Story: STORY-2026-10-15-release_managed_spell. Control flow and concurrency: the code-description patch beside this.

## Before / after
- Before (0.2.8243): every stamped managed version has a pool in its root's store, but nothing routes an object back
  to it and nothing describes the pools of a class.
- After: `ReleaseManagedSpell` is a process singleton with the hosted roots' shape (U11): `_instance`, a class
  `_singleton_lock`, `_initialized`, a double-checked `__new__`, a once-only `__init__` under the lock that refuses a
  first construction without its host (`ReleaseManagedSpell(aether=...)`; ValueError, bookkeeping reset), a
  `cleanup()` that resets the bookkeeping at its end, and `_reset_singleton_for_tests()`. `Aether.__init__` builds it
  last, after Nexus; `Aether.cleanup` cleans it right after the frames, whose stores unregister their pools first.
  `ReleaseManagedSpell()` returns the Aether-owned instance. Releasing never goes through Aether.
  - Registry state: `_pools_by_class` (`type` -> tuple of pools; the hot read) and `_registrations` (`id(pool)` ->
    `(class, holding root id)`; cold), both republished whole under the leaf `_lock`, read without it.
  - `register(pool, *, root_conduit_id)`: idempotent; re-keys a pool whose class changed (a rebind under the same id)
    and records the root whose store now holds it (a restore into another root).
  - `unregister(pool)`: idempotent; nothing to do for an unregistered pool or a cleaned registry.
  - `release(obj, *, spell_id=None, conduit=None)`: one dict get by `type(obj)`; exactly one pool and no filter ->
    `pool.put_back(obj)`. Anything else goes to the cold resolver.
  - The cold resolver: the cleaned check; `spell_id` must be a str and `conduit` a `Conduit` (a root or one of its
    lessers - its root is the filter); a class with no pool -> ValueError; keep the pools matching the filters; when
    several remain, keep those whose version is its index's selected one; exactly one -> it; otherwise ValueError
    naming every candidate and the keywords that pick one.
  - `managed(obj, ...)` -> `ManagedSpellLease(obj, pool)`, resolved the same way. `release_all(objects, ...)` releases
    each object, then raises one ExceptionGroup of the failures. `describe(cls)` -> one dict per pool: the pool's own
    `describe()` plus `holding_conduit_id` and `active_version`; `()` for a class with no pool; TypeError for a
    non-class.
  - `ManagedSpellLease(obj, pool)`: `object` (RuntimeError once released), `released`, `release()` (the first call
    puts the object back; later calls do nothing), `__enter__` -> the object, `__exit__` releases even when the block
    raised and never suppresses. One holder; not a thread-safe handle.
  - Creations: `ensure_managed_quantity` registers the pool after its store lock; `extract_spell_creations`
    unregisters the pool it gives up; `restore_spell_creations` unregisters a pool it replaces, registers the one it
    installs, then cleans the replaced one; `cleanup` unregisters each detached pool before cleaning it.
  - `ManagedSpellQuantity.managed_class`: the bound class, captured at construction and at `_rebind_spell`, readable
    after cleanup (the registry's key).
  - `SpellIndex._is_selected_unless_cleaned(spell_id)`: whether a live index selects that id; False once cleaned.
  - Package root: `ManagedSpellMode`, `ReleaseManagedSpell`, `ManagedSpellLease`, `ManagedSpellExhaustedError`. The
    owner's root ruling (2026-07-19) brings user-held surfaces, front-facing enums and user-catchable errors to the flat
    facade and keeps the no-export-wiring law below it; `ManagedSpellQuantity` stays off the root.

## Interface deltas
- Public: `ReleaseManagedSpell` (`release`, `managed`, `release_all`, `describe`), `ManagedSpellLease`, the four root
  exports.
- Internal: `register`, `unregister`, `_live_instance`, `_reset_singleton_for_tests`, `managed_class`,
  `SpellIndex._is_selected_unless_cleaned`.
- Persisted: none (the registry is runtime state, rebuilt as stores take pools).

## State / failure deltas
- Not managed: "<Class> is not a managed spell class in any live root: bind it with
  existence=Existence.managed_spell_quantity, or its root was torn down." (ValueError)
- Ambiguous: "<Class> is managed by <k> pools: spell_id=..., binding=..., frame=..., root=..., active=...; ... Pass
  spell_id=... or conduit=... to pick one." (ValueError)
- No match: "No pool of managed class <Class> matches spell_id=<id>, conduit root <id>. Its pools: ... ." (ValueError)
- Wrong filter types: TypeError naming the argument and what it takes.
- Bare first construction: "ReleaseManagedSpell is created by Aether at boot; construct Aether() first (import melder
  does), then ReleaseManagedSpell() returns it." (ValueError)
- A cleaned registry: `release`, `managed`, `release_all`, `describe` and `register` raise the cleaned RuntimeError
  (both maps are kept as empty tombstones, so the fast path misses and the cold path raises); `unregister` does
  nothing (it is part of teardown).
- A released lease's `object`: "This ManagedSpellLease was released; its object went back to its pool." (RuntimeError)
- `release_all`: ExceptionGroup "Errors occurred releasing <n> of <m> managed objects".

## Dependency / ordering
- S3 (pools, Creations). Boot order: Crystallizer, AetherUtilitySystem, LoadGate, Mediator, MutationResearch, Nexus,
  ReleaseManagedSpell. Teardown: gate, plane, frames (stores unregister), ReleaseManagedSpell, Crystallizer,
  MutationResearch, configuration, Nexus, utility system.
- S5 builds `Conduit.managed_spell_meld` on the lease; S6 relies on extract/restore unregistering and registering.

## Validation expectations
- Unit, test_release_managed_spell.py: the singleton (one instance, Aether-owned, bare first construction refused,
  reset and cleanup clear it, a cleaned registry refuses), register/unregister (idempotent, re-key, holding root),
  release (fast path, every resolver branch and text, type errors), managed, release_all, describe.
- Unit, test_managed_spell_lease.py: object, release once, `with` on success and on error, no suppression.
- Unit: Creations registers at ensure, unregisters at extract and cleanup, restore unregisters and registers;
  SpellIndex probe; `managed_class`; the root exports.
- Multithreaded: concurrent releases against register/unregister churn never see a torn map or lose a pool.
- Integration: a real Spellbook - conjure registers, a post-conjure bind registers, root and Aether teardown leave
  the registry empty, releases by class, by spell id and by conduit.
- A routing-cost probe (release through the registry vs `put_back`); both GIL modes.
