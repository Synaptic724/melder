# Component Patch: Nexus Config-Driven Projection Refresh Barrier

## Before
- `_refresh_rift_projection_sets_for_frame(...)` always disables impacted
  Rift gates, waits for drain using hardcoded timing, refreshes, then reopens.

## After
- `_refresh_rift_projection_sets_for_frame(...)` reads the new config-backed
  barrier settings.
- Default-on behavior stays the same.
- Opt-out bypasses the disable/wait/enable barrier and refreshes directly.

## Validation Expectation
- Focused Nexus tests prove default-on gated behavior and opt-out behavior.
