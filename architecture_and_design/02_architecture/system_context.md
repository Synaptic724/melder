# System Context

<!--
Audience: evaluator, adopter, integrator
Depth: high
Status: current
Verified against: Melder 0.1.2 / git 7b31be6d7665
Last verified: 2026-08-29
Diagram source: architecture_and_design/diagrams/source/system_context.mmd
Source anchors:
- README.md
- pyproject.toml
- src/melder/aether/aether.py
- src/melder/nexus/nexus.py
-->

[Architecture and design home](../README.md)

## Reader Question

Where does Melder sit relative to application code, operators, agents, and persistence?

## Short Answer

Melder runs inside the application's Python process. Application code defines and enters
the object world through `bind`, `conjure`, and `meld`. Optional external systems do not
own that world: orchestrators or agents enter through bounded Rift surfaces, while
external storage carries structural persistence records through user-provided adapters.

![Melder system context](../diagrams/rendered/system_context.svg)

[Editable diagram source](../diagrams/source/system_context.mmd)

## Boundary Responsibilities

- **Application code** owns domain behavior and decides what to register.
- **Melder** owns graph compilation, scope/lifetime enforcement, and runtime structure.
- **Developers/operators** define configuration and lifecycle policy.
- **Orchestrators/agents** remain optional consumers of controlled live-system surfaces.
- **External persistence** remains caller-selected infrastructure; Melder records
  structure without requiring a database dependency.

## Why This Design Is Strong

Melder does not replace the application's entry point or domain model. It supplies the
systems layer beneath them, keeping domain objects ordinary while making their runtime
relationships explicit and inspectable.

## Tradeoffs

Embedding the runtime in-process gives direct object access and shared-memory performance.
It also means application owners must define process, frame, and cleanup boundaries
deliberately instead of delegating them to an external container service.

## Where to Go Next

- [Runtime model](runtime_model.md) opens the process boundary.
- [Compose an application](../03_usage/compose_an_application.md) shows the basic use.

Source entry points:

- [`Aether`](../../src/melder/aether/aether.py)
- [`Nexus`](../../src/melder/nexus/nexus.py)
- [Project metadata](../../pyproject.toml)
