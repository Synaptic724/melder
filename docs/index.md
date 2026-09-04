# A runtime you can build on

Melder wires ordinary Python objects into a live dependency graph: services,
configuration, connections, and the objects your application works with.
Start with a small application. Grow into connected subsystems, isolated worlds,
and agent-operated infrastructure when you need them.

```text
bind       register what exists
conjure    compile and validate the graph
meld       resolve an instance
```

```bash
pip install melder
```

**Python 3.14+. Zero runtime dependencies.** The saved example curriculum targets
free-threaded Python 3.14.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Start with a working example
:link: examples/hello-melder
:link-type: doc

Bind a plain class and resolve your first instance.
:::

:::{grid-item-card} Browse the examples
:link: examples/index
:link-type: doc

Learn through the runnable scripts saved with Melder.
:::

:::{grid-item-card} Explore the full contents
:link: contents
:link-type: doc

Jump directly to a level, lesson, or reference.
:::
::::

## Choose your level

The four levels follow the same progression as the README. Read in order or
enter where your question belongs. Later capabilities stay optional.

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} 🟢 Beginner
:link: beginner/index
:link-type: doc
:class-card: level-beginner

The core runtime. Bind, resolve, categorize, scope, and clean up.

**For:** anyone building their first Melder application.
:::

:::{grid-item-card} 🟡 Intermediate
:link: intermediate/index
:link-type: doc
:class-card: level-intermediate

Connection. Register modules, configure scopes, and link independent subsystems.

**For:** applications growing beyond one scope.
:::

:::{grid-item-card} 🟠 Advanced
:link: advanced/index
:link-type: doc
:class-card: level-advanced

Isolation and inspection. Work with separate worlds, runtime views, and precise overrides.

**For:** multi-tenant and multi-world systems.
:::

:::{grid-item-card} 🔵 Expert
:link: expert/index
:link-type: doc
:class-card: level-expert

Agent rooms, transactions, checkpoints, research, and governed change.

**For:** runtime and agent infrastructure builders.
:::
::::

## Three verbs, a high ceiling

Your classes stay ordinary Python. A spellbook describes what can be built;
a conduit is the runtime you resolve through. Choose how long instances live
and who cleans them up.

That graph also gives deeper tooling something concrete to inspect and operate.
The higher levels explain those capabilities without making them prerequisites
for your first application.

Continue with [Hello Melder](examples/hello-melder.md), inspect the
[system picture](reference/architecture.md), or use the [API reference](reference/api.md).
