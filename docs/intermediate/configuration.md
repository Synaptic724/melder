# Configure the book before conjure

Prerequisite: [bind → conjure → meld](../beginner/rhythm.md). A
`SpellbookConfiguration` states the book's policy: teardown vocabulary and
scheduler settings are common reasons to provide one explicitly.

## Choose defaults or supply a complete policy

Use `with_defaults()` for the standard policy, then adjust mutable scheduler
settings before conjure. If you need a custom disposal vocabulary, build that
configuration explicitly before handing it to `Spellbook(configuration=...)`.
The saved disposal lesson shows the complete setup rather than a fragment that
depends on an already-initialized configuration.

Conjure validates and freezes the configuration. Disposal names and priority are
resolved for each spell at bind time, so establish them before binding. The configuration lessons
also demonstrate unknown-property and incomplete-configuration failures.

## Ordered disposal: book block first or last

Per-bind `disposal_method_names` belong to that binding. Book-configured names
apply to every new binding that implements them. Matching happens once at bind;
cleanup consumes the resulting list without rereading configuration.

```python
config = md.SpellbookConfiguration()
config.with_disposal_method_names(["flush", "close"])
config.with_enforce_priority_disposal_methods(False)  # default: book block last
config.with_defaults().finalize()

book = md.Spellbook(configuration=config)
book.bind(
    spell=Resource,
    existence="many",
    disposal_method_names=["close", "release", "flush"],
)
```

Assuming `Resource` declares all three methods:

| Priority flag | Calls on each instance |
| --- | --- |
| `False` (default) | `release()` → `flush()` → `close()` |
| `True` | `flush()` → `close()` → `release()` |

The book owns shared names in **both** modes. Its complete matching block keeps
configuration order; spell-only methods keep their own order beside it. Missing
names are omitted and each accepted name runs once. An empty per-bind list does
not suppress book methods.

The existing matching scope is class-profile methods declared on the class;
inherited-only methods, factory returns, and prebuilt-instance methods are not
discovered by this binding path. Supply a class with explicit methods when you
want automatic disposal registration.

The method-name property is set-once; choose it before `with_defaults()` fills it.
The priority flag can be adjusted during configuration assembly and freezes with
the configuration. This is creation-time policy, not a post-bind mutation API.

Existing scope/key/bucket teardown order is unchanged. Within one object, a
method failure stops its remaining methods; other objects still receive cleanup.
Crystals preserve the resolved order, and replay applies the receiving book's
normal binding policy. A different policy can yield a different content ID.

## Tune the compile phase deliberately

| Property | Meaning |
| --- | --- |
| `phase_scheduler_workers_per_spellbook` | Worker count for the compile pipeline |
| `phase_scheduler_barrier_timeout_milliseconds` | Maximum wait at a phase barrier, in milliseconds |
| `disposal` | Stored configuration flag; matched method names drive current cleanup registration |
| `disposal_method_names` | Ordered book-wide teardown candidates, matched once per new spell |
| `enforce_priority_disposal_methods` | Place the book block first (`True`) or last (`False`, default) |

A larger timeout allows slower work to complete; it does not repair a dependency
error. The scheduler lesson checks that constructor DI still works with one worker
and an explicitly chosen barrier timeout.

## Share policy intentionally

The shared-policy lesson passes the **same configuration object** to two books and
asserts its identity. The books retain distinct registrations and named roots.
Do not confuse shared book policy with the world's posture: the latter determines
whether structural operations such as linking are available.

Continue with [lifecycle hooks](hooks.md) to observe the configured runtime.
