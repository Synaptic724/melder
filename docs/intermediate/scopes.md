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
