# Ownership and Lifetimes

<!--
Audience: adopter, integrator, contributor
Depth: mid
Status: current
Verified against: Melder 0.1.2 / git 7b31be6d7665
Last verified: 2026-08-29
Diagram source: architecture_and_design/diagrams/source/ownership_lifetimes.mmd
Source anchors:
- src/melder/aether/spellbook/existence/existence.py
- src/melder/aether/conduit/creations/creations.py
- src/melder/aether/conduit/spell_space/spell_space.py
-->

[Architecture and design home](../README.md)

## Reader Question

Where do live objects belong, and when are they reused or disposed?

## Short Answer

Melder assigns every resolved object to an explicit lifetime boundary. The broadest
objects belong to a frame; narrower objects belong to conduits, conduit lineages,
clusters, or request-local spell spaces; `many` produces a new object per meld. Cleanup
walks owned scopes inward-to-outward and disposes objects in reverse creation order.

![Melder ownership and lifetime map](../diagrams/rendered/ownership_lifetimes.svg)

[Editable diagram source](../diagrams/source/ownership_lifetimes.mmd)

## Lifetime Choices

| Existence | Reuse boundary | Typical role |
| --- | --- | --- |
| `unique` | Aetheric frame | Configuration, pools, shared services |
| `unique_per_conduit` | One conduit | Session or request scope |
| `unique_per_conduit_lineage` | Root and lesser-conduit family | Context shared down a scope tree |
| `unique_per_conduit_cluster` | Named conduit group | Coordinated cross-scope service |
| `unique_per_spell_space` | Active spell space | Request-local ephemeral state |
| `many` | None | Fresh workers or value-producing services |

## Cleanup Is Part of the Model

Creation stores preserve registration order for teardown. Newer dependents are disposed
before earlier dependencies, and failures are aggregated so one bad disposer does not
prevent the remaining scope from being cleaned.

## Why This Design Is Strong

Scope is expressed in the same graph that creates objects. The runtime therefore knows
which store may reuse an instance and which owner must eventually dispose it.

## Tradeoffs

Application authors must choose lifetimes and teardown vocabulary explicitly. That cost
buys predictable reuse, deterministic cleanup, and fewer hidden process-wide singletons.

## Where to Go Next

- [Scope work and resources](../03_usage/scope_work.md)
- [Runtime model](runtime_model.md)

Source entry points:

- [`Existence`](../../src/melder/aether/spellbook/existence/existence.py)
- [`Creations`](../../src/melder/aether/conduit/creations/creations.py)
- [`SpellSpace`](../../src/melder/aether/conduit/spell_space/spell_space.py)
