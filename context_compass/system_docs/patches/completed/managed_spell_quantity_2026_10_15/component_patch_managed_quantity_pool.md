# Component patch: the managed pool in the root's Creations (managed_spell_quantity_2026_10_15, S3)

Components: ManagedSpellQuantity (new, conduit/creations), ManagedSpellExhaustedError (new,
utilities/custom_exceptions), Creations (pool map, ensure, cleanup, extract/restore, purge), Spell
(`_add_owned_conduit`), ConduitMeld and SpellSpaceMeld (purge store selection, live-creation probes).
Story: STORY-2026-10-15-managed_quantity_pool. Control flow and concurrency: the code-description patch beside this.

## Before / after
- Before: a managed spell (0.2.8241-0.2.8242) has no pool; conduit purge raises "Unsupported purge existence", the
  live-creation probes raise "Unsupported existence", and no store holds anything for it.
- After: every stamped managed spell version owns one `ManagedSpellQuantity` in its owner root's store, under its spell
  id, in `Creations._managed_quantities` (a map of its own: `_creations` never holds a pool).
- `ManagedSpellQuantity(AbstractElasticPool)`: built from the Spell (mode, limit, timeout, reset names, disposal names,
  spell id and name, binding name, frame) and the owner conduit id. Sizes: elastic - `baseline_idle=min(20, limit)`,
  `max_idle=limit`, every other argument the kernel pools' default (stretch 0, settle 1800 s, decay 10% per 600 s);
  limited_quantity and queue - `baseline_idle = max_idle = limit` (fixed capacity; idle never exceeds the count, so
  nothing is ever evicted).
  - `count`: objects built and alive (idle plus out), changed only under the pool lock.
  - `reserve()`: the miss's first step. elastic - count + 1, record pressure, None. limited_quantity - raises
    ManagedSpellExhaustedError at `count >= limit`, else count + 1, None. queue - waits on the pool's condition until a
    place is free (count + 1, None) or an object is idle (returned to the caller, no build), raising at the timeout.
  - `put_back(obj)`: the release. Runs the reset names in order outside every lock, appends, trims above the baseline
    (elastic) through the base rebalance, and wakes one queue waiter. A raising reset destroys the object (disposal
    methods and recorded children), frees its place and propagates the reset error (an ExceptionGroup when the
    destroy failed too). After cleanup raises RuntimeError naming the spell.
  - `abandon(children, error)`: a build that raised gives its place back, wakes a waiter and disposes the children it
    built; disposal failures become notes on `error`, never a new exception.
  - `adopt(obj, children)`: records the disposal-bearing `many` children built for `obj` under `id(obj)`; an entry
    already under that id belonged to an object dropped while out and is kept for teardown.
  - `destroy_object(obj)`: disposal methods, then the object's recorded children newest first; count - 1; wakes a
    waiter; failures raise one ExceptionGroup.
  - `create_object` and `acquire` refuse (the meld's plan builds); `release(obj)` is `put_back(obj)`.
  - `cleanup()`: detaches the idle objects and every children record under the lock, wakes all waiters (they raise),
    then destroys outside the lock - idle objects newest first, each with its children, then the children of objects
    still out - aggregating failures into one ExceptionGroup; idempotent.
  - `describe()`: the base keys plus mode, limit, timeout, count, recorded children, spell and owner identity.
- ManagedSpellExhaustedError(MeldExecutionError): `mode`, `limit`, `timeout_seconds`; texts below.
- Creations: `ensure_managed_quantity(spell)` returns the pool under the spell id or builds it from the Spell (a map
  write under the store lock; idempotent); `get_managed_quantity(spell_id)` is a lock-free read; `cleanup()` detaches
  the pools with the other maps and cleans them BEFORE the disposable registry, their failures joining the store's
  ExceptionGroup; `extract_spell_creations` adds a `{"scope": "managed", "disposable": False, "stored": pool}` row and
  gives the pool up; `restore_spell_creations` takes a managed row, cleaning the pool it replaces (the empty pool a
  transfer flip composed) and raising that cleanup's failures after the restore completes; `purge` returns 0 for a
  managed spell before any lock; `clear_all` and `reset_for_pool` never meet a pool (root stores only).
- Spell `_add_owned_conduit`: for a managed spell, after stamping, `creations.ensure_managed_quantity(self)`.
- ConduitMeld `_get_purge_creations`: managed -> the caller's own store (where purge returns 0). SpellSpaceMeld purge
  keeps refusing it ("purge it from its authorized conduit").
- Both live-creation probes: managed reads the owner store's pool - `is_live` when `count > 0`, `creation_count` =
  `count`, `storage_scope_kind` "managed_pool", `storage_owner_conduit_id` the owner root.

## Interface deltas
- Public: `ManagedSpellExhaustedError` (module `melder.utilities.custom_exceptions.managed_spell_exhausted_error`;
  root export with S4). The probes' new `storage_scope_kind` value "managed_pool".
- Internal: `ManagedSpellQuantity`; `Creations._managed_quantities`, `ensure_managed_quantity`,
  `get_managed_quantity`; the `managed` extract/restore row.
- Persisted: none (pools are runtime state; the record carries only the options, S2).

## State / failure deltas
- Limited: "Managed spell '<name>' (limited_quantity, limit <N>) has all <N> objects out. Release one with
  ReleaseManagedSpell().release(obj) before melding another, or bind it with a higher managed_spell_limit."
- Queue: "Managed spell '<name>' (queue, limit <N>) had no object free within <T> s. Release one with
  ReleaseManagedSpell().release(obj), or bind it with a higher managed_spell_limit or managed_spell_timeout_seconds."
- After teardown: "The pool of managed spell '<name>' was torn down with its root conduit; the object is yours to
  dispose." (RuntimeError from put_back, and from a queue waiter woken by the teardown.)
- Creations cleanup's ExceptionGroup gains the pools' disposal failures (one RuntimeError per failing method,
  chained, as for every other record).

## Dependency / ordering
- S2 (the Spell fields). S4 registers and unregisters pools with ReleaseManagedSpell at ensure, cleanup, extract and
  restore (seams named in the code). S5 calls reserve/abandon/adopt from the plan and reads `_idle`. S6 moves pools
  through extract/restore.

## Validation expectations
- Unit, per mode: sizes; reserve accounting; the limited refusal (type, text, nothing built); queue wait, timeout,
  served-by-release, woken by cleanup; reset order, a raising reset; disposal only on destroy; elastic trims (fake
  clock) with children; adopt, abandon (notes), orphan children; destroy accounting; refusals of create/acquire;
  cleanup aggregation and idempotence; put_back after cleanup; describe; no reference to an object that is out.
- Multithreaded: limited never above N under 8 threads; queue never hangs and serves waiters; elastic count consistent.
- Creations: ensure idempotent and separate from `_creations`; cleanup order (pools before the registry) and
  aggregation; extract/restore rows and replacement; purge 0; clear and reset untouched.
- Integration: a real Spellbook - conjure, post-conjure bind and bind_inactive ensure pools in the root store; root
  teardown cleans them; conduit purge returns 0; the probes answer.
- Both GIL modes; the creations, conduit, meld door and spell suites.
