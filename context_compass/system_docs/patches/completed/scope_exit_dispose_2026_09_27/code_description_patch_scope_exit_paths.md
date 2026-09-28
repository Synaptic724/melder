# Code description patch: scope exits and pool returns (2026-09-27)

## Trigger
Lifecycle, concurrency and error-semantics change on the scope exit paths.

## Control flow
Conduit.__exit__(exc_type, exc, tb) -> None:  self.cleanup(); return None        # never suppresses

Conduit.cleanup():                                     # dispatch unchanged
  if _cleaned: return
  with _lock:
      if _cleaned: return
      if _permanent_cleanup_requested: _permanent_cleanup()
      else: _prepare_for_pool()

Conduit._prepare_for_pool():
  state = _conduit_state                                # read once
  if state is not lesser: normal -> _permanent_cleanup(); pooled_lesser -> nothing; return
  ward = _conduit_ward; pooled = ConduitState.pooled_lesser; failures = None
  if ward._lesser_conduits:                             # unlocked read: new child links take this conduit's lock
      failures = ward._cleanup_children_for_pool(collect_finished=True)   # still-attached child -> raise (retry)
  merge _cleanup_spellspaces_for_pool()                 # None when nothing is open or registered (no drain call)
  try: _creations.reset_for_pool() except ExceptionGroup as g: append g
  try: named -> _prepare_named_for_pool() | unnamed -> ward._detach_for_pool()
  except Exception as e: raise e if no failures else ExceptionGroup(failures + [e])   # stays attached for retry
  state -> pooled; ward type -> pooled; clear local hooks; reset Meld hooks; _conduit_pool.return_lesser_conduit()
  if failures: raise ExceptionGroup("...returned to its pool with disposal failures", failures)

Conduit._cleanup_spellspaces_for_pool() -> Optional[List[Exception]]:
  if not _spellspace_registry and not <this thread's managed stack>: return None     # common case, no drain call
  drain this thread's stack and pop the registry; clean every space; collect every error (list made lazily)

Conduit.enter_spellspace():
  space = _spellspace_pool.acquire_untracked(); <append to this thread's managed stack inline>; return space

Conduit._permanent_cleanup():
  failures = _cleanup_lesser_conduit() | _cleanup_normal_conduit()   # collect ward / spaces / store / cluster groups
  hooks, logger last, field deletes (unchanged)
  if failures: raise ExceptionGroup("...torn down with disposal failures", failures)

SpellSpace.__exit__(...):
  if _released: _leave_after_early_release(); return None      # released or destroyed inside the block
                                                                # released: discard_expected(self); destroyed: none
  _spellspace_stack_state.pop_expected(self)
  <the managed lane of recycle_from_managed_context, inline>   # one call and one flag read fewer per scope

SpellSpace.recycle_from_managed_context():
  if _released: return
  if _permanent_cleanup_requested or _registry_tracked: cleanup(); return
  try: _creations.reset_for_pool_unlocked()
  finally: reset Meld hooks if modified; _spellspace_pool.release(self)       # release sets _released

SpellSpace.cleanup():
  if _cleaned: return
  with _lock:
      if _cleaned: return
      if _permanent_cleanup_requested: _cleanup_for_destroy(); return
      if _released: return
      try: _cleanup_for_pool_reuse()        # reset in try, registry discard and hook reset in its finally
      finally: _spellspace_pool.release(self)

SpellSpace._cleanup_for_destroy():
  _released = True                          # kept after destroy as a documented tombstone
  try: _creations.cleanup()
  finally: Meld cleanup; registry discard; _spellspace_stack_state.discard_expected(self); _cleaned = True; deletes

SpellSpace.meld / purge: if _released: _refuse_released()   # SpellSpaceScopeError; cleaned -> RuntimeError

## Edge and error behaviour
- BaseException from disposal still propagates through the `finally` steps (the scope is pooled first).
- A failing block and a failing cleanup: the cleanup group rises with the block's exception as `__context__`.
- An explicit cleanup inside a `with` block is followed by a no-op exit while the shell is still idle; if another
  thread re-leases the shell in between, that exit reaches the new lease - using a scope after releasing it
  remains a caller contract violation, as for any Cleanable.

## Invariants and idempotency
- Soft cleanup is idempotent per lease; permanent cleanup is idempotent per object.
- Stores are empty before disposal methods run, so a finished pool return never hands out an object that a failed
  disposal left behind.
- The managed SpellSpace lane stays lock-free: the flag is read and written only by the leasing thread and the
  pool's deque hand-off orders it for the next lease.

## Non-goals
- No per-lease wrapper objects, tokens or thread-local tracking for lessers.
- No check on Conduit.meld for pooled lesser handles.

## Validation focus
- Disposal-log order assertions, pool idle counts and object identities across acquisitions, error-group contents
  and chaining, per-step timings before and after.
