# Patch Architecture: Configurable RiftGate Projection Refresh

## Objective
Expose the ACL-driven projection refresh barrier through `NexusConfiguration`
while keeping the barrier enabled by default.

## Non-Goals
- Redesigning `RiftGate`.
- Removing the refresh barrier from the default path.
- Broader AR/runtime ownership changes.

## Boundary
- In scope:
  - `NexusConfiguration`
  - `INexusConfiguration`
  - `Nexus._refresh_rift_projection_sets_for_frame(...)`
  - focused tests/docs
- Out of scope:
  - viewer/command/workstation design
  - ACL model redesign

## Invariants
- Default behavior remains gated refresh.
- New Rift admission is blocked before refresh starts.
- In-flight work is allowed to drain before the swap.
- Opt-out skips the barrier but still refreshes impacted Rifts.

## Required Deltas
- Add config-backed refresh gate enable flag.
- Add config-backed timeout and poll interval.
- Make Nexus read those values instead of hardcoded literals.
