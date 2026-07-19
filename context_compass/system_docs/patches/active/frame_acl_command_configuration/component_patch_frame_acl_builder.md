# Component Patch: FrameACLBuilder

## Component Purpose and Boundary In Current Architecture
Mutable authoring surface for one frame-local ACL draft owned by a
`FrameACLContainer`.

## Before / After Behavior Summary
Before:
- builder seeds/edits view and codegen children only

After:
- builder seeds/edits view, command, and codegen children

## Interface Deltas
- profile application and draft creation must produce a draft bundle with a
  command-config child
- JSON load/commit paths must preserve the command-config child

## State and Lifecycle Deltas
- no new builder-owned top-level state expected in the first cut

## Failure Mode Deltas
- builder should fail fast if draft bundle becomes incomplete

## Dependency and Ordering Constraints
- depends on the new bundle shape
- should land after command config and bundle changes

## Validation Expectations
- focused tests for:
  - draft creation includes command config
  - commit/install path preserves command config
  - JSON load path preserves command config

## Unknowns and Open Decisions
- whether reusable ACL profiles will later own a typed command profile sibling
  remains open outside this first cut
