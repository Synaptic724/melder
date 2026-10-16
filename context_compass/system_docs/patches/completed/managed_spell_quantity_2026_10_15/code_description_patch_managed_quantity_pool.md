# Code description patch: ManagedSpellQuantity control flow (managed_spell_quantity_2026_10_15, S3)

Story: STORY-2026-10-15-managed_quantity_pool. Component contract: component_patch_managed_quantity_pool.md.

## State
- `_idle` (the base deque): idle objects, oldest left, newest right. Warm lease: `_idle.pop()` (no lock).
- `_count`: objects built and alive. Written only under `_lock` (the base RLock); `count` reads it lock-free.
- `_condition`: a Condition over `_lock`; queue waiters wait on it, every place-freeing step notifies it.
- `_children_by_object`: `id(obj)` -> `[(child, child_methods), ...]` in build order, for objects that had
  disposal-bearing `many` children; `_orphaned_children`: records whose object was dropped while out (its id was
  reused by a new object). Both written under `_lock`, read only by destroy and cleanup.
- `_cleaned` (Cleanable): set once, under `_lock`.

## Control flow
- reserve (a miss in the plan, before any child is built):
  - elastic: `with _lock: count += 1`; `_note_miss()`; return None (the caller builds).
  - limited_quantity: `with _lock:` raise the exhaustion error when `count >= limit`, else `count += 1`; return None.
  - queue: `with _condition:` loop - cleaned -> RuntimeError; `count < limit` -> `count += 1`, return None; an idle
    object -> pop and return it (served by a release; the caller uses it as is); past the deadline -> raise the
    exhaustion error; else `wait(remaining)`. The deadline is `monotonic() + timeout` taken once.
- put_back (release): cleaned -> RuntimeError. Run each reset name (`getattr(obj, name)()`), outside every lock. On a
  reset exception: `destroy_object(obj)` (collect its failures), then raise the reset error alone, or an
  ExceptionGroup of the reset error and the disposal failures. Otherwise append; queue: `with _condition: notify()`;
  when more than `baseline_idle` are idle, the base `_rebalance_after_return()` (elastic stretch, decay and trim; a
  trim calls destroy_object outside the lock).
- abandon(children, error): `with _condition: count -= 1 (not below 0); notify()`; dispose the children newest first
  outside the lock; each failure -> `error.add_note(...)`.
- adopt(obj, children): `with _lock:` move an existing record under `id(obj)` to `_orphaned_children`; record
  `children` under `id(obj)`. No user code.
- destroy_object(obj): run the disposal methods outside every lock; `with _condition:` pop the object's children
  record, `count -= 1 (not below 0)`, notify; dispose the children newest first outside the lock; raise one
  ExceptionGroup of the failures, if any.
- cleanup: `with _condition:` cleaned -> return; mark cleaned; detach `_idle` into a list and clear it; detach both
  children maps; `notify_all()`. Outside the lock: idle objects newest first (disposal methods, then that object's
  children from the detached map), then the remaining records (objects still out), then the orphaned records, newest
  first each; one ExceptionGroup of every failure.

## Edge and error semantics
- An exhaustion error is raised before anything is built; the plan builds nothing and the count is unchanged.
- A failed build gives its place back exactly once (abandon); a raising reset frees its place exactly once (destroy).
- A raising disposal never stops the rest: every method of every object runs; each failure is one RuntimeError
  chained from what the method raised.
- A release after teardown and a queue wait interrupted by teardown raise the torn-down RuntimeError; the object
  stays the caller's.
- `count` never goes below 0, so a stray extra put_back of an unknown object cannot corrupt the accounting below
  zero (identity is not tracked by ruling: such an object is simply pooled).

## Invariants and idempotency
- limited_quantity and queue: `count <= limit` at every moment (only reserve raises it, under the lock, after the
  check).
- `len(_idle) <= count` for limited and queue, so the fixed-capacity eviction never fires there.
- No reference to an object that is out: only `id(obj)` keys a children record.
- No user code (reset, disposal, constructor) runs under `_lock`; the pool lock and the store lock are leaves and
  are never held together.
- cleanup is idempotent; ensure is idempotent (one pool per store and spell id).

## Explicit non-goals
- No identity tracking, no double-release or foreign-object refusal, no automatic return, no purge verb.
- The pool never constructs; the plan builds (S5).
- No timer thread: decay happens at returns, as in the kernel pools.
