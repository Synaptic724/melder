# Melder 0.2.0 — The First Real Release

Melder 0.2.0 is the first release where the complete idea arrives as one coherent
system: a human-usable dependency runtime at the bottom, and a governed runtime world
that tools and agents can inspect, operate, preserve, and evolve at the top.

At its core, Melder is a zero-dependency Dependency Graph Runtime for Python 3.14+.
Register ordinary Python classes, functions, and instances; compile and validate their
dependency graph; resolve them through explicit scopes; and retain the live graph for
lifecycle management, introspection, isolation, and controlled structural change.

Dependency injection is the entry point. It is not the ceiling.

> Bind what can exist. Conjure a validated runtime world. Meld objects as work arrives.

## Install

```bash
pip install melder
```

- Python 3.14 or newer
- Zero runtime dependencies
- Inline typing with a shipped `py.typed` marker
- Designed for free-threaded CPython

## Sixty-Second Start

```python
import melder as md


class Config:
    def __init__(self) -> None:
        self.prefix = "hello"


class Greeter:
    def __init__(self, config: Config) -> None:
        self._config = config

    def greet(self, name: str) -> str:
        return f"{self._config.prefix}, {name}"


book = md.Spellbook()
book.bind(spell=Config, existence="unique")
book.bind(spell=Greeter, existence="unique")

conduit = book.conjure()
greeter = conduit.meld("Greeter")

print(greeter.greet("world"))
```

That is the complete entry model:

1. **Bind** ordinary application objects and choose their lifetime.
2. **Conjure** once to compile and validate the graph.
3. **Meld** by a human name when the application needs an object.

No Melder base class, metaclass, or import-time global registration is required.

## A Human-First Resolution API

Melder 0.2.0 makes the identity boundary explicit:

```python
service = conduit.meld("ReportService")              # human SpellName
same = conduit.meld(spell=ReportService)             # class/function/Protocol
exact = conduit.meld(spell_id=report_service_id)      # machine identity

variant = conduit.meld(
    "ReportService",
    override={"transport>credentials": test_credentials},
)
```

Human names occupy the simple string form. Content-derived machine identities use the
explicit `spell_id=` lane. Per-call graph substitutions use the shorter public
`override=` keyword while the internal execution machinery remains unchanged.

## What Ships in 0.2.0

### A complete dependency runtime

- Constructor injection through normal Python annotations
- Explicit `SpellMap` addressing and late-bound `SpellContract` sockets
- Six lifetime models, from fresh-per-meld objects to frame-wide uniqueness
- Request-local `SpellSpace` scopes and nested lesser conduits
- Conjure-time graph compilation and validation
- Lazy revalidation when structural changes make a lineage dirty
- Deterministic, newest-first disposal with aggregated teardown failures

### Runtime composition without a global container

- Separately owned Conduits that can link through directional contracts
- Pull-based sharing with explicit permissions
- Conduit clusters and ownership transfer for dynamic systems
- AethericFrames for tenant, plugin, test, or application-world isolation inside one
  interpreter
- Explicit graph boundaries instead of invisible autowiring

### An optional operational ceiling

The basic bind-conjure-meld path is complete on its own. The higher layers remain
dormant until an application chooses to use them.

| Capability | What it adds |
| --- | --- |
| Packaged system documents | Queryable architecture, component, and graph views inside the wheel |
| Nexus and Rift | Permissioned rooms for inspection, runtime operation, or validated code execution |
| Frame DevOps | Scope-aware transactions for safe linking, transfer, index mutation, and other structural changes |
| Crystallizer | Structural twins, profiles, checkpoints, drift detection, and all-or-nothing cold reconstruction |
| MutationResearch | Source, residency, diff, impact, preview, promotion, and rollback evidence |
| Free-threaded coordination | Reader resolution outside transactions; scoped claims and gates for writes |

This capability ladder is cumulative in power, not mandatory ceremony. An application
can permanently use only binding, scopes, and resolution. The higher ceiling exists so
growth does not require replacing the runtime model later.

## Why Melder Is More Than a DI Container

A conventional DI container usually finishes its job after constructing an object graph.
Melder retains the graph as a governed runtime world.

That retained world is what makes the rest possible:

- lifetimes have explicit owners;
- subsystems can connect without surrendering their registries;
- isolated worlds can coexist in one process;
- live state can be inspected through bounded authority;
- structural changes can be admitted, invalidated, revalidated, and audited;
- configured structure can be checkpointed and reconstructed;
- candidate changes can be examined before they enter the live graph.

The graph is not temporary construction data. It is part of the running system.

## Deliberate Tradeoffs

Melder chooses explicit structure over minimal ceremony:

- Binding is explicit; there is no magic autowiring.
- Conjure spends work up front to compile and validate the graph.
- A Spellbook owns one root Conduit; additional roots use additional books.
- Lifetimes and cleanup are designed deliberately rather than left to the garbage
  collector.
- Dynamic linking, Rift access, persistence, and governed evolution introduce concepts
  only when those layers are enabled.

These costs purchase predictable topology, deterministic ownership, early failure, and
safe runtime operation.

## Release Posture

Melder 0.2.0 is an **Alpha** release and the first real public baseline.

- Pre-1.0 APIs may still sharpen as public usage exposes better names and boundaries.
- Python 3.13 and earlier are not supported.
- Free-threaded Python is the intended runtime; GIL-enabled builds produce an import-time
  warning.
- This release is aimed at applications whose dependency graph, scopes, concurrency, or
  operational lifecycle are substantial enough to justify an explicit runtime model.
- A tiny application with three objects in `main()` probably does not need Melder.

There is no migration section for this release: 0.2.0 establishes the first real public
contract.

## Validation

The release-candidate supported suite completed with:

```text
10,991 passed, 28 skipped, 15 xfailed, 1 xpassed
```

That run covers the supported unit, component, and integration tiers. The deterministic
source and repository asset checks are also current at version 0.2.0. Published archives
still pass through the release workflow's distribution, version, and installed-wheel
verification gates before PyPI upload.

## Learn Melder

- [README tutorial](https://github.com/Synaptic724/melder#readme)
- [Architecture and design](https://github.com/Synaptic724/melder/tree/HEAD/architecture_and_design)
- [Engineering drawings][drawings]
- [Runnable beginner-to-expert examples](https://github.com/Synaptic724/melder/tree/HEAD/UX_and_AIX_experiences)
- [Getting started](https://www.synapticaisystems.com/melder/intro/)
- [API and technical documentation](https://melder.readthedocs.io/en/latest/)

[drawings]: https://github.com/Synaptic724/melder/tree/HEAD/architecture_and_design/05_engineering_drawings

## License and Feedback

Melder is licensed under
[GNU AGPL v3 or later](https://github.com/Synaptic724/melder/blob/HEAD/LICENSE).
The network-use source requirement applies to modified versions offered as a service.
The Melder name and marks are governed separately; see
[NOTICE](https://github.com/Synaptic724/melder/blob/HEAD/NOTICE).

Bug reports, adoption feedback, and design discussion are welcome through
[GitHub Issues](https://github.com/Synaptic724/melder/issues).

If you try 0.2.0, the most useful feedback is concrete: what you built, which capability
layer you used, where the model became clearer than a normal container, and where the
first-contact experience still created friction.

— Mark Geleta / Synaptic AI Systems
