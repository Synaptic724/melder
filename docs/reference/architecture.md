# Architecture & Drawings

Melder keeps an object graph as a live runtime structure. The system picture
connects registration, scopes, resolution, and the optional layers that inspect
or preserve that world.

![Melder system context](../media/system_context.svg)

[Open the drawing at full size](../media/system_context.svg)

## Read at the depth you need

- **Beginner:** the spellbook, conduit, resolved objects, and their lifetimes.
- **Intermediate:** cooperating scopes and the contracts between them.
- **Advanced:** independent frames and controlled runtime inspection.
- **Expert:** agent operations, recorded worlds, and governed structural change.

The repository's [architecture and design collection](https://github.com/Synaptic724/melder/tree/prod/architecture_and_design)
contains the canonical explanations and engineering drawings.

[Full contents](../contents.md) · [API reference](api.md)
