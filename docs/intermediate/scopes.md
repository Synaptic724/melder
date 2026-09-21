# Spell spaces, lineage, and scopes that end

Prerequisite: [Beginner scopes](../beginner/scopes.md). Keep the scope boundary
explicit: a child conduit, a conduit lineage, and a spell space answer different
questions about where instances are shared.

| Lifetime | Scope demonstrated by the lessons |
| --- | --- |
| `unique_per_conduit` | A root and its child resolve different instances |
| `unique_per_conduit_lineage` | Root, child, and grandchild share one family instance |
| `unique_per_spell_space` | Reuse inside one spell space; separate instances across spaces |

## A job owns its child scope

Create a lesser conduit for a job, resolve the job's objects through it, and call
the child's `cleanup()` when the job ends. The scoped-cleanup lesson compares the
root and job sessions, ends the child, and resolves through the root again.
The root has a longer lifetime and is cleaned up separately when the application ends.

The runtime retains the objects it manages. Dropping your last local variable does
not end that ownership; [cleanup and memory ownership](../beginner/cleanup.md)
explains why the explicit end of the scope matters.

## A lesser conduit can grow into a named root

In a dynamic world, `upgrade_to_normal(name=...)` promotes the existing child.
The promotion lesson asserts that a previously created per-conduit workbench is
the same object afterward, then finds the promoted conduit through cloud lookup.
Read [dynamic mode](dynamic-linking.md) before using this operation.

[Clusters](../advanced/clusters.md) add a group-wide lifetime. The original cluster
lesson remains in its saved Intermediate collection and is linked from that guide.

## Purge creations while keeping the scope

Use `purge` to dispose and remove the retained creations for one registered target
without ending its scope or removing its registration:

```python
removed = conduit.purge("Job")
removed = space.purge("RequestSession")
```

Names, class/function references, spellframe/binding selectors, and explicit
`spell_id=` work through the same discovery as `meld`. The return value is the
number removed, or `0` when that authorized store has no matching creation.
`purge_all=True` is the default: a `many` target removes its whole retained bucket.
Only `many` objects with configured disposal are retained; untracked results are
not affected by purge.

An existing object provides a second input path: purge inspects its class and
passes that reference through the existing binding lookup. Choose the shortcut
or the explicit selectors for your binding. Both use the same scoped purge:

```python
job = conduit.meld("Job")
removed = conduit.purge(job, purge_all=False)  # Remove this object only.
removed = conduit.purge(job)                  # Remove remaining entries for its binding.
```

Single-object removal requires the instance and returns `0` if that object is
not retained in the authorized store. Other instances remain available for later
purge or normal scope cleanup. The same options work on `SpellSpace`.

| Lifetime | Who may purge it |
| --- | --- |
| `many` | The conduit or spell space holding those local creations |
| `unique_per_spell_space` | That spell space only |
| `unique_per_conduit` | That conduit only |
| `unique_per_conduit_lineage` | The lineage root conduit |
| `unique_per_conduit_cluster` | The elected cluster leader |
| `unique` | The spell's owning conduit |

A spell space always stays within its own creations. It cannot purge objects
belonging to its conduit, lineage root, or cluster leader.

Purge follows the configured disposal methods and their ordering. It attempts
other selected objects after an object's disposal fails, then raises an
`ExceptionGroup`; removed entries remain removed. A subsequent meld can create a
fresh factory-backed instance using the existing compiled context. References
already held by application objects are not rewritten. An externally supplied
object remains referenced by its registration, so purging its store entry does
not unbind it or turn it into a factory.
