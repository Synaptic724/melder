# Architecture patch: `with` disposes a conduit, and every scope exit finishes its cleanup (2026-09-27)

Patch id: scope_exit_dispose_2026_09_27. Ticket:
tickets/tasks/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md. Findings, probes and the owner's
decisions: tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md.

## Scope and non-goals
Objective: leaving a scope always disposes what the scope owns, finishes returning the scope to its pool even when a
disposal method fails, and then reports every failure; a finished scope cannot be used again by mistake.
- `with conduit:` disposes like a .NET `using`: at block exit a lesser returns to its root's pool and a root is torn
  down. `Conduit.enter_lesser_conduit()` makes a lesser for such a block.
- SpellSpace managed exit, SpellSpace manual cleanup, lesser pool return and permanent teardown finish every step
  when disposal raises, then raise the failures as one `ExceptionGroup`.
- A lesser's pool return disposes its descendants first, then its SpellSpaces, then its own store.
- A second soft cleanup of a pooled lesser or a released SpellSpace does nothing (no double pooling).
- A released SpellSpace refuses `meld` and `purge`.
- `using_cleanup()` and `async_using_cleanup()` let cleanup errors propagate.
- Owner condition (2026-09-27): using a SpellSpace must cost no more than before. The lease flag's two writes per
  scope are paid back inside the same path (inline managed exit and stack push, one deque read, and no Space sweep
  call when nothing is open); measured at or below the old cost on 3.14t and the GIL build.
Non-goals:
- `with` keeps its lock meaning on Spellbook, Aether, AethericFrame, ConduitWard and SpellIndex.
- No change to disposal order inside a store, to purge authority, or to build locks.
- A pooled lesser handle is not checked on `Conduit.meld` (the hottest door); using a scope after cleanup stays a
  caller contract violation there.
- Infrastructure errors in permanent teardown (gate unregistration, record retirement, Nexus publication, spellbook
  cleanup, pool cleanup) stay logged, as today; only disposal failures are raised.
- Frame teardown keeps going when a conduit fails; it logs the failure instead of passing silently.

## Changed components
| component | change | component patch |
| --- | --- | --- |
| Conduit Runtime (Normal and Lesser) | dispose `with`, enter_lesser_conduit, pool return order, finish-then-raise | component_patch_conduit_runtime.md |
| Creations and SpellSpace | lease flag, released refusal, finish-then-raise exits | component_patch_spellspace.md |
| Cleanable (utilities) | cleanup contexts stop swallowing | component_patch_cleanable_contexts.md |

## Interface and boundary deltas
- Breaking: `Conduit.__enter__` no longer takes the conduit lock; `Conduit.__exit__` calls `cleanup()`. Code that
  used `with conduit:` as a lock now releases (lesser) or destroys (root) the conduit at block exit.
- New public method: `Conduit.enter_lesser_conduit(logger=None, *, name=None) -> Conduit`.
- `Conduit.cleanup()` raises an `ExceptionGroup` of disposal failures after finishing: lesser pool return (spaces
  and descendants now included; before, their failures were only logged) and permanent teardown (before: logged).
- `SpellSpace.meld` and `SpellSpace.purge` raise `SpellSpaceScopeError` (a RuntimeError) on a released space;
  after permanent cleanup they raise the usual cleaned RuntimeError.
- `Cleanable.using_cleanup()` / `async_using_cleanup()`: the owner's cleanup error propagates; with a failing block
  it rises chained to the block's exception (Python's rule for an error raised in `__exit__`).

## Cross-component invariants
- A scope's stores are swapped empty before any disposal method runs (Creations), so a failure leaves nothing to
  retry: finishing the pool return is always safe.
- Children before parents: descendants, then SpellSpaces, then the conduit's own store, on both pool return and
  permanent teardown.
- A lesser whose descendant could not finish (still attached) or whose named retirement failed stays attached and
  out of the pool, as today, so its owner can retry.
- A released SpellSpace is never served to two leases: release sets the flag, acquisition clears it, and only an
  unreleased space can meld, purge or be released again.

## Migration and rollout order
1. Red tests: conduit `with`, enter_lesser_conduit, double cleanup, pool-return order, failure paths (managed,
   manual, lesser, root), released refusal, owner cleaned inside its own managed space, cleanup contexts.
2. Baseline benchmarks on 3.14t (per-step scope cycle).
3. Source: cleanable.py, spell_space_thread_state.py, spell_space_pool.py, spell_space.py, conduit_ward.py,
   conduit.py, aetheric_frame.py; docstrings with each.
4. Rewrite the two lock tests and the 0.2.80 no-raise test; suites and the whole tree.
5. Benchmarks after; canonical docs, indexes, graph, release note (Breaking change), the next notch read at
   landing (0.2.8203; fable_0's meld entry cache took 0.2.8201 first), NOTICEs, build assets and LLM bundles last.

## Rollback
Revert the change set as one unit.

## Validation and evidence plan
| change | validation |
| --- | --- |
| `with` disposes | component: lesser pooled and objects disposed at exit; root cleaned at exit; block error kept |
| enter_lesser_conduit | component: named and anonymous; exit returns the shell |
| idempotent soft cleanup | component: two cleanups give one pool entry; two acquisitions give two objects |
| children first | component: disposal log order child, space, parent |
| finish then raise | component: each exit raises the group and the scope is pooled (or destroyed) anyway |
| released refusal | component: meld and purge on a kept handle raise SpellSpaceScopeError |
| owner cleaned inside its space | component: block exit returns without SpellSpaceScopeError |
| cleanup contexts | unit: cleanup error propagates, once only, chained to a block error |
| hot paths | per-step A/B on 3.14t: space enter, meld, exit; lesser create, cleanup |

## Ticket coverage map
One task: tickets/tasks/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md.

## Unknowns and decision requests
- None open; the owner decided the contract choices on 2026-09-27.
