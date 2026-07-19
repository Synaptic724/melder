# Component Patch: FrameViewer

## Component Purpose and Boundary In Current Architecture
Descriptor-hosting viewer surface over published frame, conduit, and spell records.

## Before / After Behavior Summary
Before:
- spell-facing viewer outputs emitted `lineage_id`

After:
- spell-facing viewer outputs emit `spell_index_id`

## Interface Deltas
- descriptor host helpers emit `spell_index_id`
- general frame/spell profile helpers emit `spell_index_id`
- lineage-group/listing helpers should be renamed only where they are part of
  the published output surface for this slice

## State and Lifecycle Deltas
- none; this is an output contract rename only

## Failure Mode Deltas
- none; behavior is unchanged if the sweep is complete

## Dependency and Ordering Constraints
- viewer comparisons and grouping logic that reference the field must be
  renamed in the same tranche
- focused descriptor/viewer tests must be swept with the runtime rename

## Validation Expectations
- focused frame-viewer descriptor host and profile tests stay green

## Unknowns and Open Decisions
- none for this slice
