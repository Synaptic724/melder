# Design Tradeoffs

<!--
Audience: evaluator, adopter, integrator, contributor
Depth: mid
Status: current
Verified against: Melder 0.1.2 / git 7b31be6d7665
Last verified: 2026-08-29
Diagram source: none
Source anchors:
- README.md
- src/melder/aether/spellbook/spellbook.py
- src/melder/aether/conduit/creations/creations.py
- src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py
-->

[Architecture and design home](../README.md)

## Reader Question

What costs does Melder intentionally accept to obtain its runtime properties?

## Short Answer

Melder chooses explicit structure, lifecycle ownership, early compilation, and governed
mutation over invisible wiring and minimal ceremony. These are not detached drawbacks;
each cost purchases a specific operational property.

## Core Tradeoffs

| Design choice | Strength purchased | Cost accepted | Where it matters |
| --- | --- | --- | --- |
| Explicit binding | Predictable, inspectable topology | Registration declarations | Application composition |
| Conjure-time compilation | Early graph validation and reusable execution artifacts | Startup work | Boot and deployment |
| One root conduit per spellbook | Clear root ownership | Additional roots need books | Large system partitioning |
| Explicit lifetimes and cleanup | Deterministic reuse and teardown | Lifecycle design | Resources and concurrency |
| Separate conduits plus contracts | Independent subsystem ownership | Link/contract choreography | Modular platforms |
| Aetheric frames | Hard in-process worlds | Repeated frame state | Tenancy and isolation |
| Writer transaction plane | Governed structural change | Mutation-path overhead | Dynamic systems |
| Readers outside transactions | Fast steady-state resolution | Validity/dirty-state machinery | High-throughput meld paths |
| Fresh-identity restore | Reconstructable structural truth | Translation maps | Cold restart |
| Bounded Rift rooms | Controlled live access | ACL and room configuration | Tools and agents |

## The MRP Boundary

The beginner path uses explicit binding, conjure-time compilation, lifetimes, and cleanup.
Dynamic links, frames, rooms, persistence, and evolution are optional capabilities. This
keeps the low floor complete while preserving the high ceiling in the same runtime model.

## Where to Go Next

- [What Melder is](../01_overview/what_melder_is.md)
- [Capability ladder](../01_overview/capability_ladder.md)
- [Runtime model](../02_architecture/runtime_model.md)

Source entry points:

- [`Spellbook`](../../src/melder/aether/spellbook/spellbook.py)
- [`Creations`](../../src/melder/aether/conduit/creations/creations.py)
- [Frame-local transaction mediator](../../src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py)
