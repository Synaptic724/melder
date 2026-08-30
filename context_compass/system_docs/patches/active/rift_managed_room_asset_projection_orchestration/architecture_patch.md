# Patch Architecture: Rift-Managed Room Asset Projection Orchestration

## Objective
Make `Rift` own projection registry + application while `RiftSpace` hosts
durable assets only.

## Non-Goals
- Redesigning Nexus projection compilation.
- Inventing a fake codegen asset.
- Broad command API redesign.

## Boundary
- In scope:
  - Rift-owned projection registry/application
  - room seam removal
  - command projection access rebasing
  - focused tests/docs
- Out of scope:
  - broader viewer API redesign
  - command vocabulary redesign
  - codegen execution design

## Invariants
- Projections still come from Nexus.
- Assets still live on RiftSpace.
- Rift orchestrates projection application to hosted assets.
- Agent-facing room surface does not expose projections.

## Required Deltas
- Add Rift-owned projection registry.
- Remove projection registry + accessors from RiftSpace.
- Rebase command projection access onto Rift.
- Keep viewer sync driven by Rift.
