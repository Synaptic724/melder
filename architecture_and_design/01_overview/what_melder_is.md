# What Melder Is

<!--
Audience: evaluator, adopter
Depth: high
Status: current
Verified against: Melder 0.1.2 / git 7b31be6d7665
Last verified: 2026-08-29
Diagram source: architecture_and_design/diagrams/source/runtime_process.mmd
Source anchors:
- README.md
- src/melder/aether/aether.py
- src/melder/aether/spellbook/spellbook.py
-->

[Architecture and design home](../README.md)

## Reader Question

What kind of system is Melder, beyond calling it a dependency-injection container?

## Short Answer

Melder is a Dependency Graph Runtime. Applications register ordinary Python classes,
functions, and instances; Melder compiles their dependency structure, establishes scoped
ownership, and resolves live objects from that retained graph. Dependency injection is
the familiar entry point, while lifecycle, introspection, isolation, and governed change
are capabilities of the retained runtime world.

![Melder inside a Python process](../diagrams/rendered/runtime_process.svg)

[Editable diagram source](../diagrams/source/runtime_process.mmd)

## The Three-Verbs Mental Model

1. **Bind** — declare what can exist and how long it should live.
2. **Conjure** — compile and validate the graph, then create its root execution scope.
3. **Meld** — resolve objects from that compiled world as work arrives.

The graph is not discarded after construction. It remains available to enforce lifetime,
permission, validity, and change-control decisions.

## Why This Design Is Strong

- **Early structural feedback.** Compilation moves graph-shape failures toward startup.
- **Explicit ownership.** Frames, conduits, spell spaces, and creation stores make
  lifecycle boundaries visible.
- **A retained world model.** Introspection, persistence, and controlled mutation build
  on real runtime structure rather than reconstructing it from scattered callables.
- **Plain application objects.** User classes do not need a Melder base class.

## Tradeoffs

- Explicit registration adds declarations and avoids invisible autowiring.
- Up-front compilation spends startup work and reduces first-use surprises.
- Explicit ownership requires cleanup discipline and enables deterministic teardown.
- Advanced capabilities add concepts, but remain dormant outside the layers that use them.

## Where to Go Next

- [Capability ladder](capability_ladder.md) shows which layers are optional.
- [Runtime model](../02_architecture/runtime_model.md) explains the core components.
- The runnable introduction remains in the repository [README](../../README.md).

Source entry points:

- [`Aether`](../../src/melder/aether/aether.py)
- [`Spellbook`](../../src/melder/aether/spellbook/spellbook.py)
- [`Conduit`](../../src/melder/aether/conduit/conduit.py)
