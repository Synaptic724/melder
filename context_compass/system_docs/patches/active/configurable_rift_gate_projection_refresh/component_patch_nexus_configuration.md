# Component Patch: NexusConfiguration Refresh Barrier Settings

## Before
- Projection refresh gating is hardcoded in Nexus.
- No explicit config field documents whether gating is enabled or how long
  drain waits are allowed to last.

## After
- `NexusConfiguration` owns:
  - refresh-gating enabled flag
  - refresh-gating timeout seconds
  - refresh-gating poll interval seconds
- Defaults keep gating enabled.

## Validation Expectation
- Focused configuration tests prove defaults, fluent setters, and validation.
