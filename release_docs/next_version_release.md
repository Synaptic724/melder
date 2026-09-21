# Melder — next version

**Draft release notes. Version and publication date to be assigned.**

## Added: scoped creation purge

`Conduit.purge(...)` and `SpellSpace.purge(...)` retire retained creations without ending their
scope or removing the registered spell. This gives applications an explicit way to dispose of
objects while keeping their bindings and compiled creation machinery available for later melds.

### Choose an object reference or explicit selectors

Pass an existing object as a shortcut. Purge inspects its class and uses the existing spell lookup:

```python
worker = conduit.meld(Worker)
removed = conduit.purge(worker)
```

The normal meld-style selectors are also available. These are alternative call forms:

```python
conduit.purge(Worker)                           # Class reference
conduit.purge("Worker")                         # Registered name
conduit.purge(Worker, binding_name="primary")    # Named binding
conduit.purge(spellframe=IWorker, binding_name="primary")
conduit.purge(spell_id=worker_spell_id)           # Explicit machine identity
```

Both input paths use the same scope checks and creation-disposal machinery. Discovery itself
does not call a constructor or invoke meld execution.

### Remove all retained creations or one object

`purge_all=True` is the default. It removes all retained creations for the selected spell within
the authorized scope. For `many`, that means the spell's entire local retained bucket.

Use `purge_all=False` with an actual object instance to remove only that object:

```python
# Worker is bound as Existence.many with configured disposal.
first = conduit.meld(Worker)
second = conduit.meld(Worker)

removed = conduit.purge(first, purge_all=False)  # 1; second remains retained
removed = conduit.purge(Worker)                 # 1; removes second
```

The same options are available on a spell space:

```python
with conduit.enter_spellspace() as space:
    session = space.meld(RequestSession)
    removed = space.purge(session, purge_all=False)
```

Purge returns the number of removed creations. It returns `0` when the selected store has no
matching entry, including when a requested single object is no longer retained. Single-object
mode requires an instance; it does not choose an arbitrary object from a name or class selector.

### Scope authority follows the creation lifetime

| Existence | Authorized caller and target |
| --- | --- |
| `many` | The calling conduit or spell space removes its own local creations |
| `unique_per_spell_space` | That spell space removes its own creation |
| `unique_per_conduit` | That conduit removes its own creation |
| `unique_per_conduit_lineage` | Only the lineage root conduit removes the shared creation |
| `unique_per_conduit_cluster` | Only the elected cluster leader removes the shared creation |
| `unique` | Only the spell's owning conduit removes the creation |

A spell space can purge only its own `many` and `unique_per_spell_space` creations. A conduit
does not redirect purge into an ambient spell space. Unauthorized scope requests fail before removal.

### Disposal and subsequent melds

- Purge uses the configured disposal methods and their existing order. Retained `many` entries
  are disposed newest first; single-object mode invokes disposal only for the selected object.
- Live and disposal records are removed together under the existing creation locks. Disposal
  callbacks run after those locks are released.
- If disposal fails, other selected objects are still attempted and failures are reported as an
  `ExceptionGroup`. Removed entries remain removed and are not disposed again during later cleanup.
- Registrations, compiled contexts and scope objects remain available. A later meld can create a
  fresh factory-backed instance according to its normal lifetime.
- Only retained creations can be purged. `many` results without configured disposal are not retained.
- Existing Python references held by application code are not rewritten, and dependent objects are
  not recursively purged. An externally supplied object remains referenced by its registration;
  purge does not unbind it or turn it into a factory.

## Validation recorded for this change

The focused source selection passed **270 tests**, covering both selector paths, single/all removal,
scope authority, creation locks, disposal ordering/failures, concurrent purge and existing
Creations/Meld/lineage/cluster behavior. Scoped lint checks passed. This is not a full-suite or
coverage claim.
