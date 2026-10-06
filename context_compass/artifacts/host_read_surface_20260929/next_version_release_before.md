# Melder 0.2.8207

**Unreleased**

## Melds by name or class take the warm lane

`conduit.meld("Service")` and `conduit.meld(spell=Service)` now reach the compiled builder in one lookup once
the spell has been built once through that call - the warm lane that `meld(spell_id=...)` already had.
`SpellSpace.meld` does the same for scoped melds. The meld door keeps a second success-only registry keyed
by the name string or the class object a caller passes, validated per call by the same guards as the id
entry (door epoch, creation-context identity, live hook and validation flags), so a warm hit returns exactly
what the full lane would.

Nothing changes in what you call or what comes back: the same object for a stored lifetime, a fresh one per
call for `Existence.many`, the same errors, the same override and existing-object behaviour. Melds that pass
`spellframe` or `binding_name`, an instance or a callable as `spell`, dynamic worlds, hooks, and list, tuple
or empty override payloads keep their current path.

Directional numbers on a 2-core VM (Python 3.14t, free-threaded): a warm meld by name of a dependency-free
class 453 -> 269 ns, with one singleton dependency 537 -> 350 ns, at width 4 888 -> 687 ns, a stored singleton
melded directly 333 -> 177 ns; melds by name, by class and by id now cost the same.

## `with` releases a Conduit, and every scope exit finishes its cleanup

**Breaking change:** `with conduit:` no longer holds the conduit's lock for the block. A Conduit is now a
dispose scope, like a .NET `using` block: when the block ends, a lesser conduit disposes the objects it holds
and goes back to its root's pool, and a root conduit is torn down. Code that used `with conduit:` as a lock
needs a lock of its own; code that cleaned the conduit up by hand after the block can drop that call.
`Spellbook`, `Aether`, `AethericFrame`, `ConduitWard` and `SpellIndex` keep `with` as a lock.

`Conduit.enter_lesser_conduit(logger=None, *, name=None)` makes a lesser for such a block; it returns exactly
what `create_lesser_conduit` returns:

```python
with root.enter_lesser_conduit() as request:
    handler = request.meld(Handler)
# the request's objects are disposed and the lesser is back in root's pool
```

**Breaking change:** a failing disposal method no longer stops cleanup half way, and its failure is no longer
only logged. A SpellSpace block exit, a SpellSpace `cleanup()`, a lesser's return to its pool and a root's
teardown now finish every step - the scope still goes back to its pool, or is fully torn down - and then raise
all the disposal failures together as one `ExceptionGroup`. Before, a failure could leave a SpellSpace or a
lesser out of its pool, and a conduit's teardown only logged these failures. If your disposal methods can
fail, catch `ExceptionGroup` (or use `except*`) around cleanup. When the `with` block itself raised, its
exception is kept and the cleanup group rises with it as `__context__`. `using_cleanup()` and
`async_using_cleanup()`, available on every Cleanable, now let a cleanup error propagate instead of
swallowing it.

Also fixed:

- A lesser's return disposes its child lessers first, then its SpellSpaces, then its own objects - the order a
  root's teardown already used.
- Calling `cleanup()` twice on a lesser or a SpellSpace no longer puts it in its pool twice, where two later
  acquisitions could receive the same object.
- A SpellSpace back in its pool refuses `meld` and `purge` with `SpellSpaceScopeError`, so a handle kept after
  its block can no longer build objects into the idle space that the next request would be served.
- A lesser cleaned up inside one of its own `enter_spellspace()` blocks no longer makes that block's exit
  raise "stack corruption".

What stays the same: the disposal order inside a scope (newest first, each object's methods in declared
order), which objects each scope owns, purge, and build locks. Frame teardown still cleans every conduit when
one fails; it now logs that failure instead of dropping it silently.

Directional numbers on a 2-core VM (Python 3.14t, free-threaded), same process, against 0.2.8202: a managed
SpellSpace enter and exit 9-19 ns faster, a lesser create and cleanup 7-20 ns faster, a warm `SpellSpace.meld`
2-5 ns faster; the GIL build measured no slower.

## Fixed: a SpellSpace's live-creation probe missed the `many` objects it holds

The no-create probe on the meld door a SpellSpace uses (`has_live_creation` and
`describe_live_creation_status`) now reads `Existence.many` objects from the space's own store. A `many` with
disposal methods melded through a space is kept there - the space's exit disposes it and the space's `purge`
removes it from there - but the probe looked in the owner conduit's store, so it reported nothing while the
space held such objects and counted the conduit's own instead. It now counts the space's, with
`storage_scope_kind` `"spellspace_many"` and the space's id in `active_spellspace_id`.
`Conduit.has_live_creation`, every other lifetime and the meld path are unchanged; the probe still creates
nothing.

## Fixed: same-named classes can use distinct spell addresses

Two classes named `Repo` can now share a Spellbook when their spellframes or binding names differ.
Previously both registrations succeeded, but `conjure()` rejected them with `DUPLICATE_SPELL_NAME`,
even though its error advised adding those same qualifiers.

```python
book.bind(spell=users.Repo, spellframe="users", existence="many")
book.bind(spell=orders.Repo, spellframe="orders", existence="many")
root = book.conjure()
users_repo = root.meld(spellframe="users")
orders_repo = root.meld(spellframe="orders")
```

Phase 4 now checks the normalized `(frame_key, binding_key)` used by registration and resolution.
This also permits qualified same-named definitions with `resolvable=False` and qualified contracted
bindings. A genuine shared address still produces a collision; its diagnostic retains the
`DUPLICATE_SPELL_NAME` code and names the normalized address. Discoverable definitions retain their
address ownership and direct-meld refusal. Bare-class lookup semantics are unchanged.

## Fixed: concurrent first reads of system documents

Concurrent first access to `__architecture__`, `__components__`, `__graph_network__` or
`__graph_details__` could fail with a `NoneType` error during section lookup. The lazy loader marked
the section table ready before publishing its key map, so another reader could observe only half
the index. It now publishes the complete map before setting that ready marker. A failed map build
also remains retryable. Loading stays deferred and reads remain lock-free.

## Packaging and documentation

- The packaged system documents (`melder.__components__`, `melder.__architecture__`) are regenerated: the Meld
  Resolution Runtime entry describes the name/class registry, its mint rule, its readers and its invalidation,
  and the meld sequence names both door registries.
- The packaged system documents also describe `with` as a dispose scope, `enter_lesser_conduit`, the finished
  scope exits and the SpellSpace lease; their stale SpellSpace claims (an active-scope check, `reset()`, a
  version) are corrected.
- The packaged system documents also describe which store each meld door's live-creation probe reads, and
  the Meld runtime's store-selection text now matches the code for `unique`, lineage and cluster lifetimes.
- The packaged system documents no longer paste the documentation tooling's commands or cite its files,
  which a reader of the packaged copy could not resolve, and the conduit meld door's docstrings now name
  the store each lifetime uses and no longer promise an active-spellspace check.
- The source and test system documents describe canonical address validation and the qualified-name
  regressions, including discoverable definitions, contracted bindings and genuine address collisions.
- The system-document contracts describe readiness-last index publication and the deterministic
  concurrency/retry regressions that protect it.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8207.
