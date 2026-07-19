# Component Patch: Conduit

## Component Purpose and Boundary In Current Architecture
`Conduit` owns publication/removal triggers for its canonical Nexus conduit
record.

## Before / After Behavior Summary
Before:
- only normal conduits publish/remove descriptor conduit records

After:
- published conduit states include lesser and normal
- lesser create path publishes
- lesser cleanup removes

## Interface Deltas
- `_publish_conduit_record_to_nexus(...)` and
  `_remove_conduit_record_from_nexus(...)` stop being normal-only
- lesser create flow triggers descriptor publication for the new lesser conduit

## State and Lifecycle Deltas
- lesser conduit lifecycle now includes descriptor record ownership/removal

## Failure Mode Deltas
- publication remains best-effort under existing Nexus publish gating
- frame summary publication should not become part of ordinary lesser
  create/dispose churn

## Dependency and Ordering Constraints
- lessers should publish after they are fully constructed and lineage-wired
- lessers should remove records before lesser cleanup nulls runtime identity

## Validation Expectations
- focused tests for lesser publish/remove and upgrade overwrite behavior

## Unknowns and Open Decisions
- none for the first publish/remove cut
