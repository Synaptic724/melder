# component_patch_interfaces

## Purpose
Extend the descriptor payload interface family to cover conduit and frame
payloads plus the matching record contracts.

## Required Changes
- add `IConduitDescriptorPayload`
- add `IFrameDescriptorPayload`
- extend `IConduitRecord` with `payload`
- extend `IFrameRecord` with `payload`

## Invariants
- payload interfaces remain `Protocol`-based
- record contracts stay in lockstep with runtime concrete classes
