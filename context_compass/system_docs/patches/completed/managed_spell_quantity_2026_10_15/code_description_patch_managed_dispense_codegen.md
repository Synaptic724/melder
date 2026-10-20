# Code-description patch: the managed site in emitted plans (managed_spell_quantity_2026_10_15, S5)

Read with component_patch_managed_dispense_codegen.md. Triggers: control flow (a third site kind, nested failure
handling), concurrency (lock-free pops, the pool lock, cold races) and idempotency (each lease handed out or put
back exactly once).

## State
- Per plan namespace, a leasing managed site i binds `sid{i}` (the version id) and either `h{i}` (the pool) and
  `pp{i}` (its `_idle.pop`) as constants, or nothing (the per-creation shape reads `h{i}` as a local); a miss with
  disposal-bearing children binds `dm{K}` per child K. The helpers `_return_leases`, `_return_unused_leases` and
  `_raise_missing_managed_pool` are bound only into plans that have a managed site.
- SitePlanEmission keeps, per kept step: its kind (shared, many, leasing managed, fresh managed), whether it has a
  miss (shared or leasing managed), and per consumer the ordered leasing sites it reads (`_leases_by_consumer`).
  Leasing sites are skipped where they are placed and emitted in their consumer's lease group instead.

## Control flow (emitted shapes; `[ov]` only in override plans)
- Pool read, per-creation shape only (emitted first in the lease group, one per lease):
  ```text
  try:
      h{m} = spells[m]._owner_creations._managed_quantities[sid{m}]
  except (AttributeError, KeyError):
      _raise_missing_managed_pool(spells[m])
  ```
- Lease: `try: v{m} = pp{m}()` (constant shape) or `try: v{m} = h{m}._idle.pop()` (per creation), then
  `except IndexError: v{m} = _miss{m}(meld, [ov,] h{m}, <outer values>)`.
- Lease group of consumer k with leases m1..mn, around k's construction region:
  ```text
  <pool reads>                 # per-creation shape
  <lease m1>
  v{m2} = None ... v{mn} = None
  try:
      <lease m2> ... <lease mn>
      <construction region of k>
  except BaseException as exc:
      _return_leases(exc, ((h{m1}, v{m1}), ..., (h{mn}, v{mn})))
      raise
  ```
  The construction region is k's construction for a many or fresh consumer (its `register_many` line follows the
  `try`, unchanged); for a leasing managed consumer it is k's construction inside its miss; for a shared consumer it
  is the guard block, which then returns from inside:
  ```text
      with <guard>:                       # omitted for a door-held root
          v{c} = c{c}._creations.get(sid{c})
          [P2 refusal when pinned]
          if v{c} is None:
              <construct c> ; <publish c> ; [adopt_children]
              return v{c}
  except BaseException as exc: ... (as above)
  _return_unused_leases(((h{m1}, v{m1}), ...))     # lost race: another meld published c first
  return v{c}
  ```
- Leasing managed miss:
  ```text
  def _miss{m}(meld, [ov,] h{m}, <outer values>):
      [_raise_unresolved_input(spells[m], (...))]
      v{m} = h{m}.reserve()
      if v{m} is not None:
          return v{m}
      [kids{m} = []]
      try:
          <children placed in the miss>     # many child K with disposal: kids{m}.append((v{K}, dm{K}))
          <m's own lease group and construction>
      except BaseException as exc:
          h{m}.abandon(kids{m}, exc)        # `[]` when m has no such children
          raise
      [h{m}.adopt(v{m}, kids{m})]
      return v{m}
  ```
- Root: a leasing managed root is emitted at the plan top as its pool read and lease, and the plan returns it; a
  fresh managed root is constructed like a many root without registration.
- Placement: a leasing site's home is its consumer's miss when the consumer has one, else the consumer's home;
  a fresh site's home follows the many rule. A leasing non-root site with other than one consumer raises a
  RuntimeError at emission (per-path keys make it impossible). Outer values of a leasing miss pass through every
  enclosing miss as for shared sites.
- Unresolved inputs: a leasing site is checked at the top of its own miss (before `reserve`, so a refusal takes no
  place); many and fresh sites are checked at their context's top as today.

## Edge and error semantics
- `reserve()` refuses (exhausted, torn down): nothing was taken and nothing is abandoned - the `try` starts after it.
- `reserve()` serves an object (queue, or limited racing a release): it is returned unbuilt; none of the miss's
  children are built.
- A child, a lease's own build or the construction raises inside a miss: the leases taken for the object are put
  back first (inner group), then `abandon` frees the place and disposes the kids built so far; disposal and put-back
  failures become notes on the propagating exception.
- `adopt` on a pool torn down during the build disposes the object and its kids and raises the torn-down
  RuntimeError; leases that object held are not returned (it was built).
- A put-back runs the pool's resets; a raising reset destroys that object (S3). On the exception path the failure is
  a note; after a lost race all put-backs are tried, then one ExceptionGroup is raised.
- Per-creation pool read: a cleaned or unstamped owner (`_owner_creations` None or deleted) or a missing pool raises
  the named MeldExecutionError; a pool torn down after the read fails at `reserve` with the pool's own error, and a
  constant pool that was torn down has a drained deque, so it misses and fails the same way.
- A winning key on a consumer parameter fed by a managed site removes the site: no lease, no pool touched. Deeper
  keys under a leasing site apply only when it misses, as under a stored shared site.

## Invariants and idempotency
- Every object a plan leases is, before the meld returns or raises, either passed to exactly one constructed holder,
  returned to the melding caller (root), or put back to its pool once.
- Every place a miss reserves is either filled by the object it builds or given back by `abandon` once.
- The warm path takes no lock: a pop and the consumer's construction. `reserve`, `abandon` and `adopt` take only the
  pool's leaf lock and run no user code under it; a plan never leases while it holds a site's build guard (the only
  guard held around a lease is a door-held root's, as for every constructor of that plan).
- Plans without a managed step emit byte-identical source and namespace keys (the emission diff gate).

## Non-goals
- No identity tracking and no automatic return of leases held by a holder or by the caller.
- No pool construction outside ownership stamping, and no re-stamp at notch (S6, owner decision).
- No purge of managed objects; no fast-transient door for managed roots (the door's fast bit stays off).
