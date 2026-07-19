# Component Patch: NexusFrameBuilder

## Component Purpose and Boundary in Current Architecture
`NexusFrameBuilder` is the fluent authored-frame helper created by
`NexusFrameManager.begin(...)`. It owns temporary authoring state only and
delegates final realization into the manager.

## Before/After Behavior Summary
Before:
- canonical docs did not name the builder explicitly
- authored Nexus-frame behavior was described only through manager-level prose

After:
- canonical docs describe `NexusFrameBuilder` as a distinct builder-owned
  authoring surface
- docs call out the default dynamic/AI-native/Rift-enabled posture and rooted
  create path

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - `manager`
  - `frame_name`
  - optional immutability, metadata, and root-conduit name overrides
- Outputs:
  - detached `NexusFrameConfiguration` from `build()`
  - rooted `IConduit` from `create()`
- Error semantics:
  - `TypeError` when manager is missing
  - `ValueError` for empty `frame_name` or empty `root_conduit_name`

## State and Lifecycle Deltas
- builder state includes frame name, posture fields, metadata, immutability,
  and root-conduit name
- cleanup is idempotent and clears temporary authoring state
- builder is short-lived and MUST be documented as disposable authoring state,
  not durable runtime state

## Failure Mode Deltas
- doc updates MUST state that build fails fast if required posture fields are
  unset
- docs MUST state that the builder is invalid after cleanup

## Dependency and Ordering Constraints
- architecture/components updates MUST place `NexusFrameBuilder` beneath
  `NexusFrameManager`
- graph update MUST add node and ownership/delegation edges before the readable
  graph is regenerated

## Validation Expectations
- component docs include an explicit `NexusFrameBuilder` entry or subcomponent
- graph carries a node for `src/melder/aether/nexus/nexus_frame_builder.py`
- architecture/components narrative names rooted conduit creation as the public
  builder one-shot path

## Unknowns and Open Decisions
- UNKNOWN: whether the architecture doc should mention
  `NexusFrameConfiguration` together with the builder in the same subsection or
  keep the builder-specific delta scoped to components/graph only
