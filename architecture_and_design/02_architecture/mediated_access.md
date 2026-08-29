# Mediated Runtime Access

<!--
Audience: integrator, contributor
Depth: mid
Status: current
Verified against: Melder 0.1.2 / git 7b31be6d7665
Last verified: 2026-08-29
Diagram source: architecture_and_design/diagrams/source/advanced_planes.mmd
Source anchors:
- src/melder/nexus/nexus.py
- src/melder/nexus/rift/rift.py
- src/melder/nexus/rift/rift_space/rift_space.py
- src/melder/nexus/rift/command_system/command_system.py
- tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py
-->

[Architecture and design home](../README.md)

## Reader Question

How can a tool or agent inspect and operate on live objects without receiving the process
as an unrestricted bag of references?

## Short Answer

`Nexus` is the public policy and registry root for Rift-domain work. A `Rift` links to
eligible frames and owns current projections plus one room. The room hosts a viewer,
workstation, command surface, events, and memory. Its posture—static, capability, or
codegen—determines which actions are available under compiled frame ACLs.

![Melder core and advanced planes](../diagrams/rendered/advanced_planes.svg)

[Editable diagram source](../diagrams/source/advanced_planes.mmd)

## Access Layers

- **Viewer** reads projection-backed frame, conduit, and spell records.
- **Workstation** holds selected live objects, attributes, methods, and one active target.
- **Command system** mediates room-appropriate runtime operations.
- **Codegen system** validates, builds a bounded namespace, compiles, and executes only in
  a codegen room.
- **Rift gates and frame ACLs** coordinate in-flight operations and refresh authority.

## Room Postures

| Room | Intended authority |
| --- | --- |
| Static | Read-only live introspection and reuse-only surfaces |
| Capability | Broader manual discovery, activation, and topology operations |
| Codegen | Selected runtime helpers plus validated code execution |

## Why This Design Is Strong

Authority is represented as a room and projection contract rather than an informal set of
objects handed to an operator. The same live world can support different users with
different compiled surfaces.

## Tradeoffs

Bounded access requires ACL families, projection refresh, gates, and room configuration.
That cost prevents the common alternative: one all-or-nothing introspection/tooling API
whose caller can see or mutate everything.

## Where to Go Next

- [Operate through a Rift](../03_usage/operate_through_a_rift.md)
- [System context](system_context.md)

Source entry points:

- [`Nexus`](../../src/melder/nexus/nexus.py)
- [`Rift`](../../src/melder/nexus/rift/rift.py)
- [`RiftSpace`](../../src/melder/nexus/rift/rift_space/rift_space.py)
- [Capability-room integration](../../tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py)
