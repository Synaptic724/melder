# Component Patch: FrameACLBuilder

## Component Purpose and Boundary in Current Architecture
`FrameACLBuilder` is the frame-local mutable ACL authoring surface owned by one
`FrameACLContainer`. It owns one active draft session at a time and delegates
install/chain management back to the container.

## Before/After Behavior Summary
Before:
- the readable graph named `FrameACLBuilder`, but long-form docs only implied a
  generic builder surface

After:
- canonical docs describe the view/command/codegen family draft workflow,
  profile application, JSON load, commit, and discard responsibilities

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - family name and contract name
  - composed ACL profiles
  - JSON configuration payloads
- Outputs:
  - family-specific fluent builders for view/command/codegen
  - committed family configuration revision from `commit_change()`
- Error semantics:
  - `RuntimeError` when no draft is active or the wrong family is targeted
  - `ValueError` for unsupported family names

## State and Lifecycle Deltas
- builder-owned state includes:
  - active-session flag
  - draft family name
  - draft contract name
  - draft configuration
- cleanup MUST be documented as cleaning any open draft before dropping the
  borrowed container reference

## Failure Mode Deltas
- docs MUST state that only one draft may be active at a time
- docs MUST state that commit/discard clear the current draft session

## Dependency and Ordering Constraints
- components docs should align this builder directly under
  `FrameACLContainer`
- graph already includes the node/edge set, so this patch is narrative-first
  and MUST stay consistent with the existing graph relationships

## Validation Expectations
- component docs explicitly call out view/command/codegen draft entrypoints
- method-level call flows mention begin/apply/commit/discard behavior
- no graph edge changes are required unless source review finds a missing edge

## Unknowns and Open Decisions
- UNKNOWN: whether the long-form docs should name the family-specific builder
  wrappers (`FrameACLViewBuilder`, `FrameACLCommandBuilder`,
  `FrameACLCodegenBuilder`) individually in this pass
