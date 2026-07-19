# Component Patch: FrameDescriptorManager

## Component Purpose and Boundary In Current Architecture
Frame-scoped descriptor publication manager for canonical frame/conduit/spell
records.

## Before / After Behavior Summary
Before:
- `_publish_conduit_record(...)` short-circuits unless the conduit is normal

After:
- `_publish_conduit_record(...)` accepts the published conduit states for this
  slice (lesser + normal)

## Interface Deltas
- conduit publish eligibility broadens from normal-only to published-state-only

## State and Lifecycle Deltas
- no new descriptor record family
- same `ConduitRecord` model continues to be used

## Failure Mode Deltas
- no change to frame-posture gating or contract validation

## Dependency and Ordering Constraints
- must preserve upsert-by-`conduit_id` semantics so lesser -> normal upgrade
  overwrites the same descriptor record

## Validation Expectations
- focused tests proving published lesser records appear and disappear cleanly

## Unknowns and Open Decisions
- none for the first eligibility-expansion cut
