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

Conjure validates and freezes the configuration. A post-conjure edit is a refusal,
so finish configuration before the runtime is created. The configuration lessons
also demonstrate unknown-property and incomplete-configuration failures.

## Tune the compile phase deliberately

| Property | Meaning |
| --- | --- |
| `phase_scheduler_workers_per_spellbook` | Worker count for the compile pipeline |
| `phase_scheduler_barrier_timeout_milliseconds` | Maximum wait at a phase barrier, in milliseconds |
| `disposal` | Enable registered disposal calls |
| `disposal_method_names` | Names of the teardown methods used by the book |

A larger timeout allows slower work to complete; it does not repair a dependency
error. The scheduler lesson checks that constructor DI still works with one worker
and an explicitly chosen barrier timeout.

## Share policy intentionally

The shared-policy lesson passes the **same configuration object** to two books and
asserts its identity. The books retain distinct registrations and named roots.
Do not confuse shared book policy with the world's posture: the latter determines
whether structural operations such as linking are available.

Continue with [lifecycle hooks](hooks.md) to observe the configured runtime.
