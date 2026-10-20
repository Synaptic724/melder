---
myst:
  html_meta:
    description: >-
      Lease reusable Python objects from a Melder managed spell pool: elastic, limited
      and queue modes, release, reset methods, refusals, inspection and teardown.
---

# Managed spell pools: lease, release, reset

Prerequisites: [Choose an instance lifetime](../beginner/lifetimes.md),
[Cleanup and memory ownership](../beginner/cleanup.md) and
[Spell spaces, lineage, and child scopes](scopes.md).

Some objects cost more to build than to lend: connections, sessions, buffers, licence
seats. Bind such a class with the `managed_spell_quantity` existence and Melder keeps
its objects in a pool. A meld *leases* an object - an idle one when the pool has one,
a new one when it does not - and the holder gives it back when it is done. Nothing
goes back on its own: returning an object is the holder's decision.

## Bind a managed spell

```python
import melder as md

book = md.Spellbook()
book.bind(
    spell=DatabaseConnection,
    existence=md.Existence.managed_spell_quantity,
    managed_spell_mode="limited_quantity",      # elastic (default) | limited_quantity | queue
    managed_spell_limit=8,                      # at most 8 connections alive at once
    managed_spell_reset_methods=["rollback"],   # run on every release, in order
    disposal_method_names=["close"],            # run only when the pool destroys one
)
conduit = book.conjure()
```

The fluent form stages the same options:

```python
spell_id = (
    md.SpellBinder(book)
    .bind(DatabaseConnection)
    .as_managed_spell_quantity("queue", limit=1, timeout_seconds=5.0, reset_methods=["rollback"])
    .finalize()
)
```

Each managed spell gets one pool in the store of the root conduit that owns it - at
conjure, or at the bind itself when you bind on a live root. The pool starts empty and
is registered with `md.ReleaseManagedSpell()`, the process-wide registry that objects
go back through.

| Option | Meaning |
| --- | --- |
| `managed_spell_mode` | `"elastic"` (default), `"limited_quantity"` or `"queue"`; a `md.ManagedSpellMode` member works too |
| `managed_spell_limit` | elastic: the most idle objects the pool keeps (default 256); limited_quantity and queue: the most objects alive at once, idle plus out (required) |
| `managed_spell_timeout_seconds` | queue only, and required there: how long a meld waits for a release |
| `managed_spell_reset_methods` | names of zero-argument methods run, in order, on every release |

Bind refuses a malformed managed binding before anything is registered: a managed
option on another existence, a function or other non-class target, an unknown mode,
a limit below 1, a limited_quantity or queue binding without a limit, a timeout on an
elastic binding, a queue binding without one, and reset names that are not a list or
tuple of method names of the class. A managed spell may not depend on a shorter-lived
`unique_per_conduit` spell: conjure refuses that as a scope-ordering violation.

## Choose a pool mode

| Mode | When every object is out | Typical use |
| --- | --- | --- |
| `elastic` | Never refuses: a meld builds another object. A release that would keep more idle objects than the limit destroys the oldest idle one, and its disposal methods run. | Objects that must always be available; the limit caps what stays parked |
| `limited_quantity` | A meld raises `ManagedSpellExhaustedError` before anything is built | A hard cap, such as licence seats or a connection quota |
| `queue` | A meld waits up to `managed_spell_timeout_seconds`; a release hands the waiting meld the released object; past the timeout the meld raises `ManagedSpellExhaustedError` | A scarce resource where waiting beats failing |

`ManagedSpellExhaustedError` is a `MeldExecutionError`. It carries `mode`, `limit`
and `timeout_seconds` (`None` outside queue mode), and its message names the way out:
release an object, or bind a higher limit - or, for a queue, a longer timeout.

```python
try:
    conduit.meld("LicenseSeat")
except md.ManagedSpellExhaustedError as refused:
    print(refused.mode, refused.limit, refused.timeout_seconds)  # limited_quantity 2 None
```

Run [Managed spell elastic pool](../examples/intermediate/42-managed-spell-elastic-pool.md),
[Managed spell limited quantity](../examples/intermediate/43-managed-spell-limited-quantity.md)
and [Managed spell queue](../examples/intermediate/44-managed-spell-queue.md) to see each
mode at its limit.

## Lease objects

- `conduit.meld("DatabaseConnection")` leases one object. The pool hands out the most
  recently released idle object first and builds a new one only when none is idle.
- Constructor injection leases too. Annotate a parameter with the managed class: every
  injected parameter is its own lease, so two consumers hold two objects.
- `conduit.managed_spell_meld(DatabaseConnection)` melds the spell and returns a
  `md.ManagedSpellLease` whose `with` block gives the object back. It refuses a spell
  that is not managed with `ValueError`, before melding anything.

## Give objects back

```python
release = md.ReleaseManagedSpell().release

connection = conduit.meld("DatabaseConnection")
release(connection)                 # resets run, then the object is idle again

with conduit.managed_spell_meld(DatabaseConnection) as connection:
    ...                             # given back when the block ends, even if it raised

held = conduit.meld("DatabaseConnection")
with md.ReleaseManagedSpell().managed(held) as same:  # wrap an object you already hold
    ...
```

`release(obj)` finds the pool by the object's class. When more than one pool manages
that class, pass `spell_id=` or `conduit=` to pick one. A class that no live root
pools, a filter that no pool matches and a filter of the wrong type are refused.
`release_all(objects)` gives several objects back at once.

A lease releases exactly once: a second `release()` does nothing, and `lease.object`
raises `RuntimeError` once the object went back, because the pool may already have
leased it to someone else. A `with` block never swallows the block's own exception.
Run [Managed spell leases](../examples/intermediate/46-managed-spell-leases.md) for
every lease form.

## Reset objects between holders

The pool calls the named reset methods, in the order given, on every release and
before the object is idle again, so the next holder receives a clean object.

A reset that raises means the object cannot be trusted. The pool destroys it - its
disposal methods run and its place is freed - and the reset's error propagates from
`release`. The next meld builds a fresh object. Run
[Managed spell reset methods](../examples/intermediate/45-managed-spell-reset-methods.md)
to watch both outcomes.

## Inspect a pool

```python
(snapshot,) = md.ReleaseManagedSpell().describe(DatabaseConnection)
print(snapshot["count"], snapshot["idle_count"], snapshot["out_count"])  # alive, idle, out
print(snapshot["mode"], snapshot["limit"], snapshot["timeout_seconds"])
```

`describe(cls)` returns one snapshot per pool of the class, and an empty tuple when no
live root pools it. Each snapshot also names the spell (`spell_id`, `spell_name`), the
root that holds the pool (`holding_conduit_id`) and the reset and disposal method
names.

## Request scopes and root teardown

The pool belongs to the root conduit and outlives every lesser conduit made from it.
A request-scoped handler can return its connection in its own disposal method:
leaving the request scope disposes the handler, and the connection goes back to the
root's pool for the next request.

```python
class RequestHandler:
    def __init__(self, connection: PooledConnection) -> None:
        self.connection = connection

    def finish(self) -> None:
        md.ReleaseManagedSpell().release(self.connection)


book.bind(spell=RequestHandler, existence=md.Existence.many, disposal_method_names=["finish"])
root = book.conjure()

with root.enter_lesser_conduit() as request:
    handler = request.meld("RequestHandler")  # its connection is leased from the root's pool
# the scope ended: finish() ran and the connection is idle in the root's pool
```

When the root is torn down, its pools are cleaned first: idle objects are disposed,
and an object that is still out stays its holder's to dispose. The pools are then
unregistered, so a later `ReleaseManagedSpell().release(obj)` raises `ValueError` and
a lease's `release()` raises `RuntimeError`.

Because the pools are cleaned before the root's other disposals run, a consumer
melded on the root itself that releases its object in its own disposal method meets
a pool that is already gone, and the root's teardown raises an `ExceptionGroup`.
Release such objects before the root ends, or keep their holders in a lesser conduit
as above. [Managed spell injection and request scopes](../examples/intermediate/47-managed-spell-injection-and-request-scopes.md)
runs this pattern end to end.

A purge does not empty a pool: `conduit.purge` returns `0` for a managed spell, and a
spell space refuses to purge one (see [spell spaces and scopes](scopes.md)).

## Change settings or move a pool

A managed spell's mode, limit, queue timeout and reset methods are settings, not part
of its spell_id. In a [dynamic world](dynamic-linking.md), change them with
`cleanup_spell` and a new `bind`: the spell_id stays the same and so does the pool,
and every object alive stays alive and counted under the new settings.

```python
spell_id = root.bind(spell=ExportWorker, existence=md.Existence.managed_spell_quantity,
                     managed_spell_mode="limited_quantity", managed_spell_limit=1)
root.cleanup_spell(spell=root.get_spell_by_spell_id(spell_id))
rebound = root.bind(spell=ExportWorker, existence=md.Existence.managed_spell_quantity,
                    managed_spell_mode="limited_quantity", managed_spell_limit=3)
assert rebound == spell_id  # the same spell and the same pool, now with limit 3
```

`transfer_spell_ownership` moves the spell to another root, and its pool goes with it,
idle objects included. The new owner leases from it, releases still find it by class,
and the old owner can no longer meld the spell. Read
[Named conduits, transfer, and sever](ownership.md) before moving spells, then run
[Managed spell settings and transfer](../examples/intermediate/48-managed-spell-settings-and-transfer.md).
